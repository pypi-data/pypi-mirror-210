# -*- coding: utf-8 -*-
"""
Celery tasks used to asynchronously generate exports (like excel exports)


Workflow :
    user provide filters
    TODO : user provide columns

    For UserDatas exports, we need to add some fields


    1- Task entry
    2- retrieve model
    3- generate the file or re-use the cached one
"""
import os
import transaction
from tempfile import mktemp

from pyramid_celery import celery_app
from beaker.cache import cache_region
from celery.utils.log import get_task_logger

from sqla_inspect.ods import SqlaOdsExporter, OdsExporter
from sqla_inspect.excel import SqlaXlsExporter, XlsExporter
from sqla_inspect.csv import SqlaCsvExporter, CsvExporter
from sqlalchemy.orm import RelationshipProperty
from sqlalchemy.sql.expression import label
from sqlalchemy import desc, func

from endi_base.utils.date import format_date
from endi_celery.conf import get_setting
from endi_celery.models import FileGenerationJob
from endi_celery.tasks import utils
from endi.compute.math_utils import integer_to_amount
from endi.export.utils import format_filename
from endi.models.task import Task
from endi.utils.html import strip_html_tags


MODELS_CONFIGURATION = {}

logger = utils.get_logger(__name__)


GENERATION_ERROR_MESSAGE = (
    "Une erreur inconnue a été rencontrée à la génération de votre fichier, "
    "veuillez contacter votre administrateur en lui"
    "fournissant l'identifiant suivant : %s"
)


def _add_o2m_headers_to_writer(writer, query, id_key):
    """
    Add column headers in the form "label 1",  "label 2" ... to be able to
    insert the o2m related elements to a main model's table export (allow to
    have 3 dimensionnal datas in a 2d array)

    E.g : Userdatas objects have got a o2m relationship on DateDatas objects

    Here we would add date 1, date 2... columns regarding the max number of
    configured datas (if a userdatas has 5 dates, we will have 5 columns)
    We fill the column with the value of an attribute of the DateDatas model
    (that is handled by sqla_inspect thanks to the couple index + related_key
    configuration)

    The name of the attribute is configured using the "flatten" key in the
    relationship's export configuration

    :param str id_key: The foreign key attribute mostly matching the class we
    export (e.g : when exporting UserDatas, most of the related elements point
    to it through a userdatas_id foreign key)
    """
    from endi_base.models.base import DBSESSION

    new_headers = []
    for header in writer.headers:
        if isinstance(header["__col__"], RelationshipProperty):
            if header["__col__"].uselist:
                class_ = header["__col__"].mapper.class_
                # On compte le nombre maximum d'objet lié que l'on rencontre
                # dans la base
                if not hasattr(class_, id_key):
                    continue

                count = (
                    DBSESSION()
                    .query(label("nb", func.count(class_.id)))
                    .group_by(getattr(class_, id_key))
                    .order_by(desc("nb"))
                    .first()
                )

                if count is not None:
                    count = count[0]
                else:
                    count = 0

                # Pour les relations O2M qui ont un attribut flatten de
                # configuré, On rajoute des colonnes "date 1" "date 2" dans
                # notre sheet principale
                for index in range(0, count):
                    if "flatten" in header:
                        flatten_keys = header["flatten"]
                        if not hasattr(flatten_keys, "__iter__"):
                            flatten_keys = [flatten_keys]

                        for flatten_key, flatten_label in flatten_keys:
                            new_header = {
                                "__col__": header["__col__"],
                                "label": "%s %s %s"
                                % (header["label"], flatten_label, index + 1),
                                "key": header["key"],
                                "name": "%s_%s_%s"
                                % (header["name"], flatten_key, index + 1),
                                "related_key": flatten_key,
                                "index": index,
                            }
                            new_headers.append(new_header)

    writer.headers.extend(new_headers)
    return writer


def _get_tmp_directory_path():
    """
    Return the tmp filepath configured in the current configuration
    :param obj request: The pyramid request object
    """
    asset_path_spec = get_setting("endi.static_tmp", mandatory=True)
    return asset_path_spec


def _get_tmp_filepath(directory, basename, extension):
    """
    Return a temp filepath for the given filename

    :param str basename: The base name to use
    :returns: A path to a non existing file
    :rtype: str
    """
    if not extension.startswith("."):
        extension = "." + extension

    filepath = mktemp(prefix=basename, suffix=extension, dir=directory)
    while os.path.exists(filepath):
        filepath = mktemp(prefix=basename, suffix=extension, dir=directory)
    return filepath


def _get_open_file(filepath, extension):
    """
    Get the appropriate writing mode regarding the provided extension
    """
    if extension == "csv":
        return open(filepath, "w", newline="")
    else:
        return open(filepath, "wb")


@cache_region("default_term")
def _write_file_on_disk(tmpdir, model_type, ids, filename, extension):
    """
    Return a path to a generated file

    :param str tmpdir: The path to write to
    :param str model_type: The model key we want to generate an ods file for
    :param list ids: An iterable containing all ids of models to be included in
    the output
    :param str filename: The path to the file output
    :param str extension: The desired extension (xls/ods)
    :returns: The name of the generated file (unique and temporary name)
    :rtype: str
    """
    logger.debug(" No file was cached yet")
    config = MODELS_CONFIGURATION[model_type]
    model = config["factory"]
    query = model.query()
    if ids is not None:
        query = query.filter(model.id.in_(ids))

    options = {}
    if "excludes" in config:
        options["excludes"] = config["excludes"]
    if "order" in config:
        options["order"] = config["order"]
    if extension == "ods":
        writer = SqlaOdsExporter(model=model, **options)
    elif extension == "xls":
        writer = SqlaXlsExporter(model=model, **options)
    elif extension == "csv":
        writer = SqlaCsvExporter(model=model, **options)

    writer = _add_o2m_headers_to_writer(writer, query, config["foreign_key_name"])

    if "hook_init" in config:
        writer = config["hook_init"](writer, query)

    for item in query:
        writer.add_row(item)
        if "hook_add_row" in config:
            config["hook_add_row"](writer, item)

    filepath = _get_tmp_filepath(tmpdir, filename, extension)
    logger.debug(" + Writing file to %s" % filepath)

    # Since csv module expects strings
    with _get_open_file(filepath, extension) as f_buf:
        writer.render(f_buf)
    return os.path.basename(filepath)


@celery_app.task(bind=True)
def export_to_file(self, job_id, model_type, ids, filename="test", file_format="ods"):
    """
    Export the datas provided in t)he given query to ods format and generate a

    :param int job_id: The id of the job object used to record file_generation
    informations
    :param str model_type: The model we want to export (see MODELS)
    :param list ids: List of ids to query
    :param str filename: The base filename to use for the export (unique string
    is appended)
    :param str file_format: The format in which we want to export
    """
    logger = get_task_logger(__name__)
    logger.info("Exporting to a file")
    logger.info(" + model_type : %s", model_type)
    logger.info(" + ids : %s", ids)

    # Mark job started
    utils.start_job(self.request, FileGenerationJob, job_id)

    filename = format_filename(filename)

    # Execute actions
    try:
        tmpdir = _get_tmp_directory_path()
        result_filename = _write_file_on_disk(
            tmpdir,
            model_type,
            ids,
            filename,
            file_format,
        )
        logger.debug(" -> The file %s been written", result_filename)
        transaction.commit()
    except Exception:
        transaction.abort()
        logger.exception("Error while generating file")
        errors = [GENERATION_ERROR_MESSAGE % job_id]
        utils.record_failure(FileGenerationJob, job_id, errors)
    else:
        utils.record_completed(FileGenerationJob, job_id, filename=result_filename)

    return ""


def _export_data_to_file(
    headers, data, filename="export", file_format="csv"
):
    """
    Generic function to export given data to given format

    :param list headers: List of dicts with headers data, format :
        (
            {"label": "Column label", "name": "col_1"},
            {"label": "Column label 2", "name": "col_2"},
        )
    :param list data: List of dicts with rows data for each headers, format :
        (
            {"col_1": "Value row 1 col 1", "col_2": "Value row 1 col 2"},
            {"col_1": "Value row 2 col 1", "col_2": "Value row 2 col 2"},
        )
    :param str filename: The base filename to use for the export
    :param str file_format: The format in which we want to export
    """
    logger = get_task_logger(__name__)
    logger.info("    + Exporting data to file")

    tmpdir = _get_tmp_directory_path()
    filename = format_filename(filename)
    if file_format == "ods":
        writer = OdsExporter()
    elif file_format == "xls":
        writer = XlsExporter()
    else:
        writer = CsvExporter()

    writer.headers = headers
    writer.set_datas(data)

    filepath = _get_tmp_filepath(tmpdir, filename, file_format)
    logger.debug(" + Writing file to %s" % filepath)
    with _get_open_file(filepath, file_format) as f_buf:
        writer.render(f_buf)
    result_filename = os.path.basename(filepath)

    logger.debug(f" -> The file {result_filename} been written")
    return result_filename


@celery_app.task(bind=True)
@cache_region("default_term", "invoices_details")
def export_invoices_details_to_file(self, job_id, task_ids, format="csv"):
    """
    Exporting details (each lines) of given invoices

    :param int job_id: The id of the job object
    :param list task_ids: List of invoices ids to query
    :param str format: The format in which we want to export
    """

    logger.debug(f" + Exporting details for the following invoice's ids : {task_ids}")

    # Mark job started
    utils.start_job(self.request, FileGenerationJob, job_id)

    headers = (
        {"label": "Enseigne", "name": "company"},
        {"label": "Facture", "name": "invoice_number"},
        {"label": "Date", "name": "invoice_date"},
        {"label": "Client", "name": "customer"},
        {"label": "Description", "name": "description"},
        {"label": "Prix Unit. HT", "name": "unit_ht"},
        {"label": "Prix Unit. TTC", "name": "unit_ttc"},
        {"label": "Quantité", "name": "quantity"},
        {"label": "Unité", "name": "unity"},
        {"label": "TVA", "name": "tva"},
        {"label": "Total HT", "name": "total_ht"},
        {"label": "Total TVA", "name": "tva_amount"},
        {"label": "Total TTC", "name": "total_ttc"},
        {"label": "Compte produit", "name": "product"},
        {"label": "Date d'exécution", "name": "date"},
    )

    try:
        data = []
        query = Task.query().filter(Task.id.in_(task_ids))
        for invoice in query:
            logger.debug(f" + Collecting data for invoice {invoice.id}")
            for line in invoice.all_lines:
                logger.debug(f"    > Computing data for line {line.id}")
                row_data = {
                    "company": invoice.company.name,
                    "invoice_number": invoice.official_number,
                    "invoice_date": format_date(invoice.date),
                    "customer": invoice.customer.label,
                    "description": strip_html_tags(line.description),
                    "unit_ht": integer_to_amount(line.unit_ht(), 5),
                    "unit_ttc": integer_to_amount(line.unit_ttc(), 5),
                    "quantity": line.quantity,
                    "unity": line.unity,
                    "tva": integer_to_amount(max(line.get_tva(), 0), 4),
                    "total_ht": integer_to_amount(line.total_ht(), 5),
                    "tva_amount": integer_to_amount(line.tva_amount(), 5),
                    "total_ttc": integer_to_amount(line.total(), 5),
                    "product": line.product.name if line.product else "",
                    "date": format_date(line.date),
                }
                data.append(row_data)
        logger.info(" + All invoice's details data where collected !")

        result_filename = _export_data_to_file(
            headers, data, filename="detail_factures_", file_format=format
        )
    except Exception:
        logger.exception("Error while generating export file")
        errors = [GENERATION_ERROR_MESSAGE % job_id]
        utils.record_failure(FileGenerationJob, job_id, errors)
    else:
        utils.record_completed(FileGenerationJob, job_id, filename=result_filename)
    return ""

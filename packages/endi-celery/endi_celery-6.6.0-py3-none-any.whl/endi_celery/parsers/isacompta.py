import datetime
import csv
import logging
from typing import Iterable, Optional, Generator

from pathlib import Path
from pyramid.request import Request
from endi_base.utils import date as date_utils
from endi.compute.math_utils import convert_to_float

from endi_celery.interfaces import IAccountingFileParser
from endi_celery.parsers import BaseProducer, OperationData
from endi_celery.parsers.sage import CsvFileParser


logger = logging.getLogger(__name__)


class IsacomptaFileParser(CsvFileParser):
    """
    Parse un fichier xlsx extrait de quadra
    """

    encoding = "iso-8859-15"

    def stream(self) -> Generator[dict, None, None]:
        with open(self.file_path, encoding=self.encoding) as fbuf:
            dialect = csv.Sniffer().sniff(fbuf.read())
            fbuf.seek(0)
            for line in csv.DictReader(fbuf, dialect=dialect):
                line = dict(
                    [(key.strip(), value.strip()) for key, value in line.items()]
                )
                yield line


class OperationProducer(BaseProducer):
    def _get_num_val(self, line: dict, key: str) -> float:
        result = 0
        val = line.get(key, "0").strip().replace(",", ".")
        result = val or 0
        if not isinstance(result, (float, int)):
            result = convert_to_float(result, default=0)
        return result

    def _get_label(self, line: dict) -> str:
        label = line.get("Libellé mouvement", "").strip()
        label = label[:80]
        return label

    def _get_date(self, line: dict) -> datetime.date:
        return date_utils.str_to_date(line.get("Date de pièce", "").strip()).date()

    def _stream_operation(self, line) -> Optional[OperationData]:
        analytical_account = line.get("Code activité", "").strip()
        general_account = line.get("N° de compte", "").strip()
        date = self._get_date(line)
        if not date:
            logger.error("This line has incorrect date data : %s" % line)
            return None

        label = self._get_label(line)
        credit = self._get_num_val(line, key="Crédit")
        debit = self._get_num_val(line, key="Débit")
        balance = 0
        result = OperationData(
            analytical_account=analytical_account,
            general_account=general_account,
            date=date,
            label=label,
            debit=debit,
            credit=credit,
            balance=balance,
        )
        return result

    def stream_operations(self) -> Iterable[OperationData]:
        for line in self.parser.stream():
            data = self._stream_operation(line)
            if data is not None:
                yield data


def parser_factory(context: Path, request: Request):
    return IsacomptaFileParser(context)


def producer_factory(context: IAccountingFileParser, request: Request):
    return OperationProducer(context)

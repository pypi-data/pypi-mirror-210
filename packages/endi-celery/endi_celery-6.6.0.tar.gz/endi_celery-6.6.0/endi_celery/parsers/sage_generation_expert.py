import csv
import logging
from typing import Iterable, List, Optional, Generator

from pathlib import Path
from pyramid.request import Request
from endi_base.utils import date as date_utils
from endi_base.utils.math import convert_to_float

from endi_celery.interfaces import IAccountingFileParser
from endi_celery.parsers import BaseParser, BaseProducer, OperationData


logger = logging.getLogger(__name__)


class TxtFileParser(BaseParser):
    """
    Parse un fichier texte

    La partie contenant les écritures

    ECRITURES

        15/11/2021 BQ 512000 "1" "Apport capital social" D 6000,00 E  ( axe1 COOP00 )
        15/11/2021 BQ 101000 "2" "Apport capital social" C 6000,00 E  ( axe1 COOP00 )
        15/11/2021 BQ 101000 "2" "Apport capital social" C 6000,00 E  A ( axe1 COOP00 )
        ....

    """

    encoding = "iso8859-15"
    key_line = "ECRITURES"

    def _stream_operation_lines_from_file(self) -> Generator[str, None, None]:
        stream = False
        with open(self.file_path, "r", encoding=self.encoding) as fbuf:
            for line in fbuf.readlines():
                line = line.strip()
                if line.startswith("ECRITURES"):
                    stream = True
                elif stream and len(line) > 5:
                    yield line

    def stream(self) -> Generator[list, None, None]:
        for line in csv.reader(
            self._stream_operation_lines_from_file(),
            quotechar='"',
            delimiter=" ",
            skipinitialspace=True,
        ):
            yield line


class OperationProducer(BaseProducer):
    def _get_num_val(self, line: List[str], index: int) -> float:
        result = 0
        if len(line) > index:
            result = line[index].strip() or 0
        return convert_to_float(result)

    def _get_label(self, line: List[str]) -> str:
        label = line[4].strip()
        label = label[:80]
        return label

    def _get_analytical_account(self, line) -> str:
        """
        Cas 1 :
        15/11/2021 BQ 101000 "2" "Apport capital social" C 6000,00 E  ( axe1 COOP00 )

        Cas 2 (cf le A en plus):
        15/11/2021 BQ 101000 "2" "Apport capital social" C 6000,00 E  A ( axe1 COOP00 )
        """
        if len(line) == 12:
            analytical_account = line[10].strip()
        else:
            analytical_account = line[11].strip()
        return analytical_account

    def _stream_operation(self, line) -> Optional[OperationData]:
        result = None
        print(line)
        if len(line) >= 12:
            analytical_account = self._get_analytical_account(line)
            general_account = line[2].strip()
            date = date_utils.str_to_date(line[0].strip()).date()
            if not date:
                logger.error("This line has incorrect datas : %s" % line)
                return None

            label = self._get_label(line)
            type_ = line[5]
            if type_ == "C":
                debit = 0
                credit = self._get_num_val(line, index=6)
            else:
                credit = 0
                debit = self._get_num_val(line, index=6)
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
    return TxtFileParser(context)


def producer_factory(context: IAccountingFileParser, request: Request):
    return OperationProducer(context)

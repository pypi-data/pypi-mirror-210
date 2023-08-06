import csv
import typing
from cvm             import datatypes, utils, exceptions
from cvm.csvio.row   import CSVRow
from cvm.csvio.batch import CSVBatch, CSVBatchReader

class RegularDocumentHeadReader:
    def __init__(self, file, delimiter: str = ';'):
        self._dict_reader = csv.DictReader(file, delimiter=delimiter)

    def read(self) -> datatypes.RegularDocument:
        row = next(self._dict_reader)
        row = CSVRow(row)

        strtype = row.required('CATEG_DOC', str)

        try:
            doctype = getattr(datatypes.DocumentType, strtype)
        except AttributeError:
            if strtype == 'FRE NOVO':
                doctype = datatypes.DocumentType.FRE
            else:
                raise exceptions.BadDocument(f"unknown document type '{strtype}'") from None

        return datatypes.RegularDocument(
            cnpj           = row.required('CNPJ_CIA',  datatypes.CNPJ.from_zfilled_with_separators),
            reference_date = row.required('DT_REFER',  utils.date_from_string),
            version        = row.required('VERSAO',    int),
            company_name   = row.required('DENOM_CIA', str),
            cvm_code       = row.required('CD_CVM',    utils.lzstrip),
            type           = doctype,
            id             = row.required('ID_DOC',    int),
            receipt_date   = row.required('DT_RECEB',  utils.date_from_string),
            url            = row.required('LINK_DOC',  str),
        )

class UnexpectedBatch(Exception):
    pass

class RegularDocumentBodyReader(CSVBatchReader):
    def __init__(self, file, delimiter: str = ';'):
        super().__init__(file, delimiter)

        self._cached_batch: typing.Optional[CSVBatch] = None

    def read_expected_batch(self, expected_batch_id: int) -> CSVBatch:
        if self._cached_batch is None:
            batch = self.read_batch()
        else:
            batch = self._cached_batch
            self._cached_batch = None

        if batch.id == expected_batch_id:
            return batch
        else:
            self._cached_batch = batch
            raise UnexpectedBatch()
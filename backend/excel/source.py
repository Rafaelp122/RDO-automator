import io
from typing import BinaryIO

import pandas as pd

from backend.logger import logger
from backend.schemas import SheetData, SourcePreviewResponse
from backend.exceptions import InvalidFileExtension


class ExcelLoader:
    def __init__(self, file: BinaryIO, header_row: int = 0):
        self.file = file
        self.header_row = header_row

    def load_all_sheets(self) -> dict[str, pd.DataFrame]:
        logger.info("Lendo dados do arquivo (header na linha %d)", self.header_row)
        abas = pd.read_excel(self.file, sheet_name=None, header=self.header_row)
        return self._normalize_dates(abas)

    def _normalize_dates(self, abas: dict[str, pd.DataFrame]) -> dict[str, pd.DataFrame]:
        for nome_aba, df in abas.items():
            col_data = self._find_date_column(df)
            if col_data:
                df[col_data] = pd.to_datetime(df[col_data], errors="coerce")
                df["_dia_aux"] = df[col_data].dt.day
            else:
                df["_dia_aux"] = None
        return abas

    @staticmethod
    def _find_date_column(df: pd.DataFrame) -> str:
        for col in df.columns:
            if "data" in str(col).lower():
                return col
        return ""


def preview_source(file_bytes: bytes, filename: str) -> SourcePreviewResponse:
    if not filename.lower().endswith((".xlsx", ".xls")):
        raise InvalidFileExtension("Arquivo de origem deve ser .xlsx ou .xls")

    buffer = io.BytesIO(file_bytes)
    loader = ExcelLoader(buffer)
    all_sheets = loader.load_all_sheets()

    sheets = []
    for name, df in all_sheets.items():
        cols = [str(c) for c in df.columns if c != "_dia_aux"]
        rows = df[cols].fillna("").head(20).values.tolist()
        string_rows = [[str(cell) for cell in row] for row in rows]
        sheets.append(SheetData(name=name, columns=cols, data=string_rows))

    logger.info("Preview source: %d sheets from %s", len(sheets), filename)
    return SourcePreviewResponse(sheets=sheets, filename=filename)

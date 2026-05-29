import pandas as pd
from typing import Dict, BinaryIO
from .logger import logger

class ExcelLoader:
    def __init__(self, file: BinaryIO, header_row: int = 0):
        self.file = file
        self.header_row = header_row

    def load_all_sheets(self) -> Dict[str, pd.DataFrame]:
        logger.info("Lendo dados do arquivo (header na linha %d)", self.header_row)
        abas = pd.read_excel(self.file, sheet_name=None, header=self.header_row)
        return self._normalize_dates(abas)

    def _normalize_dates(self, abas: Dict[str, pd.DataFrame]) -> Dict[str, pd.DataFrame]:
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

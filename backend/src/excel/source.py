import io
import re
from typing import BinaryIO

import pandas as pd

from src.exceptions import InvalidFileExtension
from src.logger import logger
from src.schemas import SheetData, SourcePreviewResponse


def load_source_data(file: BinaryIO, header_row: int = 0) -> dict[str, pd.DataFrame]:
    """Carrega todas as abas de uma planilha Excel e normaliza datas."""
    logger.info("Lendo dados do arquivo (header na linha %d)", header_row)
    sheets = pd.read_excel(file, sheet_name=None, header=header_row)
    return _normalize_dates(sheets)


def find_date_column(df: pd.DataFrame) -> str:
    """Localiza a coluna de data pelo nome e valida o conteúdo."""
    for col in df.columns:
        if "data" in str(col).lower():
            sample = df[col].dropna().head(3)
            if len(sample) > 0:
                try:
                    pd.to_datetime(sample, errors="raise")
                    return col
                except (ValueError, TypeError):
                    continue
    return ""


def _normalize_dates(sheets: dict[str, pd.DataFrame]) -> dict[str, pd.DataFrame]:
    for _sheet_name, df in sheets.items():
        date_col = find_date_column(df)
        if date_col:
            df[date_col] = pd.to_datetime(df[date_col], errors="coerce")
            df["_dia_aux"] = df[date_col].dt.day
        else:
            df["_dia_aux"] = None
    return sheets


def _extract_acronym_candidates(all_sheets: dict[str, pd.DataFrame]) -> list[str]:
    """Varre todas as células de todas as abas em busca de palavras
    em CAIXA ALTA com 2-4 caracteres — prováveis siglas.

    Retorna uma lista ordenada e sem duplicatas para o frontend
    exibir como sugestões editáveis.
    """
    candidates: set[str] = set()
    for df in all_sheets.values():
        for col in df.columns:
            for value in df[col].dropna():
                text = str(value).strip()
                for word in text.split():
                    clean = re.sub(r"[^\w]", "", word)
                    if 2 <= len(clean) <= 4 and clean.isupper() and clean.isalpha():
                        candidates.add(clean)

    logger.info("Siglas candidatas detectadas: %s", candidates)
    return sorted(candidates)


def preview_source(file_bytes: bytes, filename: str) -> SourcePreviewResponse:
    if not filename.lower().endswith((".xlsx", ".xls")):
        raise InvalidFileExtension("Arquivo de origem deve ser .xlsx ou .xls")

    buffer = io.BytesIO(file_bytes)
    all_sheets = load_source_data(buffer)

    sheets = []
    for name, df in all_sheets.items():
        cols = [str(c) for c in df.columns if c != "_dia_aux"]
        rows = df[cols].fillna("").head(20).values.tolist()
        string_rows = [[str(cell) for cell in row] for row in rows]
        sheets.append(SheetData(name=name, columns=cols, data=string_rows))

    acronyms = _extract_acronym_candidates(all_sheets)

    logger.info(
        "Preview source: %d sheets, %d acronyms from %s", len(sheets), len(acronyms), filename
    )
    return SourcePreviewResponse(sheets=sheets, filename=filename, suggestedAcronyms=acronyms)

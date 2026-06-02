import io
from typing import BinaryIO

import pandas as pd

from src.exceptions import InvalidFileExtension
from src.logger import logger
from src.schemas import SheetData, SourcePreviewResponse


def load_source_data(file: BinaryIO, header_row: int = 0) -> dict[str, pd.DataFrame]:
    """Carrega todas as abas de uma planilha Excel e normaliza datas."""
    logger.info("Lendo dados do arquivo (header na linha %d)", header_row)
    sheets = pd.read_excel(file, sheet_name=None, header=header_row)
    for sheet_name in sheets:
        sheets[sheet_name] = sheets[sheet_name].convert_dtypes()
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
    for sheet_name, df in sheets.items():
        date_col = find_date_column(df)
        if date_col:
            before_nan = df[date_col].isna().sum()
            df[date_col] = pd.to_datetime(df[date_col], errors="coerce")
            after_nan = df[date_col].isna().sum()
            new_nat = after_nan - before_nan
            if new_nat > 0:
                logger.warning(
                    "Sheet '%s': %d invalid dates coerced to NaT in column '%s'",
                    sheet_name,
                    new_nat,
                    date_col,
                )
            df["_dia_aux"] = df[date_col].dt.day
    return sheets


def _extract_acronym_candidates(all_sheets: dict[str, pd.DataFrame]) -> list[str]:
    """Varre todas as células de todas as abas em busca de palavras
    em CAIXA ALTA com 2-4 caracteres — prováveis siglas.

    Retorna uma lista ordenada e sem duplicatas para o frontend
    exibir como sugestões editáveis.
    """
    all_series = [df[col].dropna().astype(str) for df in all_sheets.values() for col in df.columns]
    if not all_series:
        return []

    all_text = pd.concat(all_series, ignore_index=True)
    words = all_text.str.strip().str.split().explode().dropna()
    clean = words.str.replace(r"[^\w]", "", regex=True)
    mask = clean.str.len().between(2, 4) & clean.str.isupper() & clean.str.isalpha()
    candidates = sorted(set(clean[mask]))

    logger.info("Siglas candidatas detectadas: %s", candidates)
    return candidates


def preview_source(file_bytes: bytes, filename: str) -> SourcePreviewResponse:
    if not filename.lower().endswith((".xlsx", ".xls")):
        raise InvalidFileExtension("Arquivo de origem deve ser .xlsx ou .xls")

    buffer = io.BytesIO(file_bytes)
    all_sheets = load_source_data(buffer)

    sheets = []
    for name, df in all_sheets.items():
        cols = [str(c) for c in df.columns if c != "_dia_aux"]
        rows = df[cols].astype(object).fillna("").head(20).to_numpy().tolist()
        string_rows = [[str(cell) for cell in row] for row in rows]
        sheets.append(SheetData(name=name, columns=cols, data=string_rows))

    acronyms = _extract_acronym_candidates(all_sheets)

    logger.info(
        "Preview source: %d sheets, %d acronyms from %s", len(sheets), len(acronyms), filename
    )
    return SourcePreviewResponse(sheets=sheets, filename=filename, suggestedAcronyms=acronyms)

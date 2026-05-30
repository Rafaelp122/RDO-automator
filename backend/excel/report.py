import calendar
import io
import json
from datetime import datetime

from backend.logger import logger
from backend.processor import TextProcessor
from backend.schemas import GenerateConfig
from backend.exceptions import InvalidFileExtension, InvalidConfigError
from backend.excel.source import ExcelLoader
from backend.excel.template import TemplateManager


def generate_report(
    source_bytes: bytes,
    template_bytes: bytes,
    source_filename: str,
    template_filename: str,
    config: dict | str,
) -> io.BytesIO:
    _validate_files(source_filename, template_filename)
    cfg = _parse_config(config)
    source_data = _load_source(source_bytes)
    tm = _load_template(template_bytes)
    _build_report(tm, source_data, cfg)
    return _save(tm)


def _validate_files(source_filename: str, template_filename: str):
    if not source_filename.lower().endswith((".xlsx", ".xls")):
        raise InvalidFileExtension("Arquivo de origem deve ser .xlsx ou .xls")
    if not template_filename.lower().endswith(".xlsx"):
        raise InvalidFileExtension("Template deve ser .xlsx")


def _parse_config(config: dict | str) -> dict:
    if isinstance(config, str):
        try:
            config_dict = json.loads(config)
        except json.JSONDecodeError as e:
            raise InvalidConfigError(f"JSON invalido: {e}")
    else:
        config_dict = config

    try:
        parsed = GenerateConfig(**config_dict)
    except Exception as e:
        raise InvalidConfigError(str(e))

    return parsed.model_dump()


def _load_source(source_bytes: bytes) -> dict:
    loader = ExcelLoader(io.BytesIO(source_bytes))
    return loader.load_all_sheets()


def _load_template(template_bytes: bytes) -> TemplateManager:
    tm = TemplateManager(io.BytesIO(template_bytes))
    tm.load()
    return tm


def _build_report(tm: TemplateManager, source_data: dict, cfg: dict):
    contract = cfg["contract"]
    mappings = cfg["mappings"]
    separator = cfg.get("listSeparator", ", ")
    connector = cfg.get("listConnector", " e ")
    ano, mes = contract["ano"], contract["mes"]
    _, ultimo_dia = calendar.monthrange(ano, mes)

    logger.info("Gerando relatorio: mes=%d/%d, %d mappings", mes, ano, len(mappings))

    for dia in range(1, ultimo_dia + 1):
        ws = tm.clone_worksheet(datetime(ano, mes, dia).strftime("%d-%m"))
        for mapping in mappings:
            _fill_cell(ws, source_data, dia, mapping, separator, connector)


def _fill_cell(ws, source_data: dict, dia: int, mapping: dict, separator: str, connector: str):
    celula = mapping.get("templateCell", "")
    if not celula:
        return

    values = _extract_cell_values(source_data, dia, mapping.get("sourceColumns", []))
    if not values:
        ws[celula] = None
        return

    for col in values:
        values[col] = list(dict.fromkeys(values[col]))

    texto = TextProcessor.formatar_resumo(
        values, mapping.get("formatTemplate", ""), separator, connector
    )
    ws[celula] = texto if texto else None


def _extract_cell_values(source_data: dict, dia: int, columns: list[str]) -> dict:
    combined = {}
    for df in source_data.values():
        if "_dia_aux" not in df.columns:
            continue
        filtro = df[df["_dia_aux"] == dia]
        if filtro.empty:
            continue
        for col in columns:
            if col not in filtro.columns:
                continue
            vals = filtro[col].dropna().unique().tolist()
            vals = [v for v in vals if str(v).strip() and str(v).lower() != "nan"]
            if vals:
                combined.setdefault(col, []).extend(vals)
    return combined


def _save(tm: TemplateManager) -> io.BytesIO:
    output = io.BytesIO()
    tm.save_to_stream(output)
    output.seek(0)
    logger.info("Relatorio gerado com sucesso")
    return output

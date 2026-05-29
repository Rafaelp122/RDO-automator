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
    if not source_filename.lower().endswith((".xlsx", ".xls")):
        raise InvalidFileExtension("Arquivo de origem deve ser .xlsx ou .xls")
    if not template_filename.lower().endswith(".xlsx"):
        raise InvalidFileExtension("Template deve ser .xlsx")

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

    cfg = parsed.model_dump()
    contract = cfg["contract"]
    mappings = cfg["mappings"]
    list_separator = cfg.get("listSeparator", ", ")
    list_connector = cfg.get("listConnector", " e ")

    loader = ExcelLoader(io.BytesIO(source_bytes))
    abas_origem = loader.load_all_sheets()

    tm = TemplateManager(io.BytesIO(template_bytes))
    tm.load()

    ano = contract["ano"]
    mes = contract["mes"]
    _, ultimo_dia = calendar.monthrange(ano, mes)

    logger.info("Gerando relatorio: mes=%d/%d, %d mappings", mes, ano, len(mappings))

    for dia in range(1, ultimo_dia + 1):
        data_atual = datetime(ano, mes, dia)
        ws = tm.clone_worksheet(data_atual.strftime("%d-%m"))

        for mapping in mappings:
            celula = mapping.get("templateCell", "")
            if not celula:
                continue

            format_template = mapping.get("formatTemplate", "")
            source_columns = mapping.get("sourceColumns", [])

            combined_values = {}
            for sheet_name, df in abas_origem.items():
                if "_dia_aux" not in df.columns:
                    continue
                filtro = df[df["_dia_aux"] == dia]
                if filtro.empty:
                    continue
                for col in source_columns:
                    if col in filtro.columns:
                        vals = filtro[col].dropna().unique().tolist()
                        vals = [v for v in vals if str(v).strip() and str(v).lower() != "nan"]
                        if vals:
                            if col not in combined_values:
                                combined_values[col] = []
                            combined_values[col].extend(vals)

            if not combined_values:
                ws[celula] = None
                continue

            for col in combined_values:
                combined_values[col] = list(dict.fromkeys(combined_values[col]))

            resumo = TextProcessor.formatar_resumo(combined_values, format_template, list_separator, list_connector)
            ws[celula] = resumo if resumo else None

    output = io.BytesIO()
    tm.save_to_stream(output)
    output.seek(0)
    logger.info("Relatorio gerado com sucesso")
    return output

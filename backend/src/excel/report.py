"""Geração do relatório consolidado (diário de obra)."""

import calendar
import io
import json
from datetime import datetime

from pydantic import ValidationError

from src.excel.processor import TextProcessor
from src.excel.source import load_source_data
from src.excel.template import TemplateManager
from src.exceptions import InvalidConfigError, InvalidFileExtension
from src.logger import logger
from src.schemas import GenerateConfig


class ReportGenerator:
    """Gera o relatório consolidado (Diário de Obra).

    Pipeline: valida extensões → parse do config JSON → carrega
    planilha de origem e template → para cada dia do mês clona o
    template e preenche as células mapeadas → salva em BytesIO.
    """

    def __init__(
        self,
        source_bytes: bytes,
        template_bytes: bytes,
        source_filename: str,
        template_filename: str,
        raw_config: dict | str,
        header_row: int = 0,
    ):
        self.source_bytes = source_bytes
        self.template_bytes = template_bytes
        self.source_filename = source_filename
        self.template_filename = template_filename
        self.raw_config = raw_config
        self.header_row = header_row

    def generate(self) -> io.BytesIO:
        """Executa o pipeline completo e retorna o arquivo Excel gerado."""
        if not self.source_filename.lower().endswith((".xlsx", ".xls")):
            raise InvalidFileExtension("Arquivo de origem deve ser .xlsx ou .xls")
        if not self.template_filename.lower().endswith(".xlsx"):
            raise InvalidFileExtension("Template deve ser .xlsx")

        config = self._parse_configuration()

        logger.info(
            "Gerando relatorio: mes=%d/%d, %d mappings",
            config["contract"]["mes"],
            config["contract"]["ano"],
            len(config["mappings"]),
        )

        source_data = load_source_data(io.BytesIO(self.source_bytes), header_row=self.header_row)

        template = TemplateManager(io.BytesIO(self.template_bytes))

        self._build_daily_sheets(source_data, template, config)
        return self._write_output(template)

    def _parse_configuration(self) -> dict:
        """Converte o JSON de config em dicionário validado via Pydantic."""
        if isinstance(self.raw_config, str):
            try:
                config_dict = json.loads(self.raw_config)
            except json.JSONDecodeError as error:
                raise InvalidConfigError(f"JSON invalido: {error}") from error
        else:
            config_dict = self.raw_config

        try:
            validated = GenerateConfig(**config_dict)
        except ValidationError as error:
            raise InvalidConfigError(str(error)) from error

        return validated.model_dump()

    def _build_daily_sheets(self, source_data, template, config):
        """Para cada dia do mês, clona o template e preenche as células."""
        contract = config["contract"]
        mappings = config["mappings"]
        year, month = contract["ano"], contract["mes"]
        _, last_day = calendar.monthrange(year, month)

        for day in range(1, last_day + 1):
            sheet_title = datetime(year, month, day).strftime("%d-%m")
            worksheet = template.clone_worksheet(sheet_title)
            for mapping in mappings:
                self._fill_worksheet_cell(worksheet, day, mapping, source_data, config)

    def _fill_worksheet_cell(self, worksheet, day, mapping, source_data, config):
        """Extrai valores da origem para o dia, formata e escreve na célula."""
        target_cell = mapping.get("templateCell", "")
        if not target_cell:
            return

        column_values = self._extract_column_values(
            day, mapping.get("sourceColumns", []), source_data
        )

        if not column_values:
            worksheet[target_cell] = None
            return

        for column_name in column_values:
            column_values[column_name] = list(dict.fromkeys(column_values[column_name]))

        formatted_text = TextProcessor.format_summary(
            column_values,
            mapping.get("formatTemplate", ""),
            config.get("listSeparator", ", "),
            config.get("listConnector", " e "),
            acronyms=config.get("siglas"),
        )
        worksheet[target_cell] = formatted_text if formatted_text else None

    def _extract_column_values(self, day, column_names, source_data):
        """Coleta valores das colunas em todas as abas para o dia informado."""
        combined: dict[str, list] = {}

        for df in source_data.values():
            if "_dia_aux" not in df.columns:
                continue

            rows_for_day = df[df["_dia_aux"] == day]
            if rows_for_day.empty:
                continue

            for column_name in column_names:
                if column_name not in rows_for_day.columns:
                    continue

                raw_series = rows_for_day[column_name].dropna()
                raw_series = raw_series[raw_series.astype(str).str.lower() != "nan"]
                clean_values = raw_series.unique().tolist()

                if clean_values:
                    combined.setdefault(column_name, []).extend(clean_values)

        return combined

    def _write_output(self, template):
        """Salva o workbook em BytesIO e reposiciona o cursor."""
        output_stream = io.BytesIO()
        template.save_to_stream(output_stream)
        output_stream.seek(0)
        logger.info("Relatorio gerado com sucesso")
        return output_stream

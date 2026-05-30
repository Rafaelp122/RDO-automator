"""Geração do relatório consolidado (diário de obra)."""

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


class ReportGenerator:
    """
    Gera um relatorio consolidado (diario de obra) a partir de uma
    planilha de dados de origem e um arquivo de template Excel.

    Pipeline:
        1. Valida extensoes dos arquivos (xlsx/xls para origem, xlsx para template)
        2. Interpreta e valida a configuracao JSON (contrato, mapeamentos, separadores)
        3. Carrega a planilha de origem (todas as abas, normaliza datas)
        4. Carrega o arquivo de template (preserva imagens e estilos)
        5. Para cada dia do mes, clona o template e preenche as celulas mapeadas
        6. Salva o workbook resultante em um stream BytesIO
    """

    def __init__(
        self,
        source_bytes: bytes,
        template_bytes: bytes,
        source_filename: str,
        template_filename: str,
        raw_config: dict | str,
    ):
        self.source_bytes = source_bytes
        self.template_bytes = template_bytes

        self._validate_filenames(source_filename, template_filename)
        self.config = self._parse_configuration(raw_config)
        self.source_data = self._load_source_data()
        self.template_manager = self._load_template()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def generate(self) -> io.BytesIO:
        """Executa o pipeline completo e retorna o arquivo Excel gerado."""
        self._build_daily_sheets()
        return self._write_output()

    # ------------------------------------------------------------------
    # Pipeline: validação
    # ------------------------------------------------------------------

    def _validate_filenames(self, source_filename: str, template_filename: str):
        """Garante que os arquivos tem as extensoes esperadas."""
        if not source_filename.lower().endswith((".xlsx", ".xls")):
            raise InvalidFileExtension("Arquivo de origem deve ser .xlsx ou .xls")
        if not template_filename.lower().endswith(".xlsx"):
            raise InvalidFileExtension("Template deve ser .xlsx")

    def _parse_configuration(self, raw_config: dict | str) -> dict:
        """
        Converte a configuracao (JSON string ou dict) em um dicionario
        validado via Pydantic. Retorna os campos padronizados.
        """
        if isinstance(raw_config, str):
            try:
                config_dict = json.loads(raw_config)
            except json.JSONDecodeError as error:
                raise InvalidConfigError(f"JSON invalido: {error}")
        else:
            config_dict = raw_config

        try:
            validated = GenerateConfig(**config_dict)
        except Exception as error:
            raise InvalidConfigError(str(error))

        return validated.model_dump()

    # ------------------------------------------------------------------
    # Pipeline: carga de dados
    # ------------------------------------------------------------------

    def _load_source_data(self) -> dict:
        """Carrega todas as abas da planilha de origem e normaliza as datas."""
        loader = ExcelLoader(io.BytesIO(self.source_bytes))
        return loader.load_all_sheets()

    def _load_template(self) -> TemplateManager:
        """Carrega o arquivo de template e extrai imagens embutidas."""
        template_manager = TemplateManager(io.BytesIO(self.template_bytes))
        template_manager.load()
        return template_manager

    # ------------------------------------------------------------------
    # Pipeline: construção das abas diárias
    # ------------------------------------------------------------------

    def _build_daily_sheets(self):
        """
        Para cada dia do mes do contrato:
          - Clona a aba do template com titulo 'DD-MM'
          - Preenche cada celula mapeada com os dados extraidos da origem
        """
        contract = self.config["contract"]
        mappings = self.config["mappings"]
        year, month = contract["ano"], contract["mes"]
        __, last_day = calendar.monthrange(year, month)

        logger.info(
            "Gerando relatorio: mes=%d/%d, %d mappings",
            month, year, len(mappings),
        )

        for day in range(1, last_day + 1):
            sheet_title = datetime(year, month, day).strftime("%d-%m")
            worksheet = self.template_manager.clone_worksheet(sheet_title)

            for mapping in mappings:
                self._fill_worksheet_cell(worksheet, day, mapping)

    def _fill_worksheet_cell(self, worksheet, day: int, mapping: dict):
        """
        Extrai os valores da origem filtrados pelo dia, remove duplicatas,
        formata o texto final e escreve na celula do template.
        """
        target_cell = mapping.get("templateCell", "")
        if not target_cell:
            return

        column_values = self._extract_column_values(
            day, mapping.get("sourceColumns", [])
        )

        if not column_values:
            worksheet[target_cell] = None
            return

        # Remove duplicatas mantendo a ordem de inserção
        for column_name in column_values:
            column_values[column_name] = list(dict.fromkeys(column_values[column_name]))

        list_separator = self.config.get("listSeparator", ", ")
        list_connector = self.config.get("listConnector", " e ")

        formatted_text = TextProcessor.formatar_resumo(
            column_values,
            mapping.get("formatTemplate", ""),
            list_separator,
            list_connector,
        )
        worksheet[target_cell] = formatted_text if formatted_text else None

    def _extract_column_values(self, day: int, column_names: list[str]) -> dict:
        """
        Percorre todas as abas da origem e coleta os valores das colunas
        especificadas para o dia informado.

        Retorna um dicionario no formato:
            { "Servico": ["Pintura", "Concretagem"], "Bairro": ["Centro"] }
        """
        combined: dict[str, list] = {}

        for dataframe in self.source_data.values():
            if "_dia_aux" not in dataframe.columns:
                continue

            rows_for_day = dataframe[dataframe["_dia_aux"] == day]
            if rows_for_day.empty:
                continue

            for column_name in column_names:
                if column_name not in rows_for_day.columns:
                    continue

                raw_values = rows_for_day[column_name].dropna().unique().tolist()
                # Remove strings vazias e representacoes de NaN
                clean_values = [
                    value for value in raw_values
                    if str(value).strip() and str(value).lower() != "nan"
                ]

                if clean_values:
                    combined.setdefault(column_name, []).extend(clean_values)

        return combined

    # ------------------------------------------------------------------
    # Pipeline: saída
    # ------------------------------------------------------------------

    def _write_output(self) -> io.BytesIO:
        """Salva o workbook gerado em um stream BytesIO e reposiciona o cursor."""
        output_stream = io.BytesIO()
        self.template_manager.save_to_stream(output_stream)
        output_stream.seek(0)
        logger.info("Relatorio gerado com sucesso")
        return output_stream


# ------------------------------------------------------------------
# Função pública (mantém compatibilidade com a API e testes)
# ------------------------------------------------------------------

def generate_report(
    source_bytes: bytes,
    template_bytes: bytes,
    source_filename: str,
    template_filename: str,
    config: dict | str,
) -> io.BytesIO:
    """Atalho para ReportGenerator.generate()."""
    return ReportGenerator(
        source_bytes, template_bytes, source_filename, template_filename, config
    ).generate()

import calendar
import io
from datetime import datetime, timedelta
import pandas as pd
from typing import Callable, Optional
from utils.logger import logger
from utils.processor import TextProcessor
from utils.excel_loader import ExcelLoader
from utils.template_manager import TemplateManager


class WebReportBuilder:
    def __init__(self, source_file: bytes, template_file: bytes, header_row: int = 0):
        self.source_file = source_file
        self.template_file = template_file
        self.header_row = header_row

    def build(
        self,
        contract: dict,
        mappings: list[dict],
        list_separator: str = ", ",
        list_connector: str = " e ",
        progress_callback: Optional[Callable] = None,
    ) -> io.BytesIO:
        loader = ExcelLoader(io.BytesIO(self.source_file), self.header_row)
        abas_origem = loader.load_all_sheets()

        tm = TemplateManager(io.BytesIO(self.template_file))
        tm.load()

        ano = contract["ano"]
        mes = contract["mes"]
        _, ultimo_dia = calendar.monthrange(ano, mes)

        data_inicio = datetime.strptime(contract["start_date"], "%Y-%m-%d")
        prazo_dias = contract["prazo_dias"]
        data_final = data_inicio + timedelta(days=prazo_dias)

        logger.info("Iniciando loop diario para %d/%d (%d dias)", mes, ano, ultimo_dia)

        for dia in range(1, ultimo_dia + 1):
            if progress_callback:
                progress_callback(int(dia / ultimo_dia * 100))

            data_atual = datetime(ano, mes, dia)
            ws = tm.clone_worksheet(data_atual.strftime("%d-%m"))

            self._fill_dynamic_mappings(ws, abas_origem, dia, mappings, list_separator, list_connector)

        output = io.BytesIO()
        tm.save_to_stream(output)
        output.seek(0)
        return output

    def _fill_dynamic_mappings(self, ws, abas_origem, dia, mappings, list_separator, list_connector):
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
            if resumo:
                ws[celula] = resumo
            else:
                ws[celula] = None

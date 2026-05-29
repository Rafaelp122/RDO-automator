import re
import pandas as pd
from io import BytesIO

class ReportValidator:
    @staticmethod
    def is_valid_excel_coordinate(coord: str) -> bool:
        return bool(re.match(r'^[A-Z]{1,3}[1-9][0-9]*$', str(coord).upper()))

    @staticmethod
    def validate_coordinates(positions: dict) -> tuple[list[str], dict[str, str]]:
        errors = []
        field_errors = {}
        for name, cell in positions.items():
            if cell and not ReportValidator.is_valid_excel_coordinate(cell):
                msg = f"Celula '{cell}' para '{name}' e invalida."
                errors.append(msg)
                field_errors[name] = msg
        return errors, field_errors

    @staticmethod
    def validate_columns_in_file(file_bytes: bytes, header_row: int, expected_columns: list[str]) -> tuple[list[str], dict[str, str]]:
        errors = []
        field_errors = {}
        try:
            buffer = BytesIO(file_bytes)
            with pd.ExcelFile(buffer) as xls:
                for sheet_name in xls.sheet_names:
                    df_header = pd.read_excel(xls, sheet_name=sheet_name, header=header_row, nrows=0)
                    for col in expected_columns:
                        if col not in df_header.columns:
                            msg = f"Aba '{sheet_name}': Coluna '{col}' nao encontrada."
                            errors.append(msg)
                            field_errors[f"column_{col}"] = msg
        except Exception as e:
            errors.append(f"Erro ao ler arquivo Excel: {e}")
        return errors, field_errors

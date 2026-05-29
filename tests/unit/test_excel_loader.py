import io
import pandas as pd
from backend.utils.excel_loader import ExcelLoader

def test_load_all_sheets_from_bytesio():
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        pd.DataFrame({"Data": ["2026-01-01", "2026-01-02"], "Atividade": ["Escavacao", "Concretagem"]}).to_excel(writer, sheet_name="Pintura", index=False)
        pd.DataFrame({"Data": ["2026-01-03"], "Drenagem": ["Tubo 600mm"]}).to_excel(writer, sheet_name="Drenagem", index=False)
    buffer.seek(0)

    loader = ExcelLoader(buffer)
    result = loader.load_all_sheets()

    assert "Pintura" in result
    assert "Drenagem" in result
    assert "Atividade" in result["Pintura"].columns
    assert "_dia_aux" in result["Pintura"].columns
    assert result["Pintura"]["_dia_aux"].iloc[0] == 1

def test_find_date_column():
    df = pd.DataFrame({"DATA_HOJE": ["2026-01-01"], "Outra": [1]})
    result = ExcelLoader._find_date_column(df)
    assert result == "DATA_HOJE"

def test_find_date_column_none():
    df = pd.DataFrame({"A": [1], "B": [2]})
    result = ExcelLoader._find_date_column(df)
    assert result == ""

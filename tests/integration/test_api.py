import io
import pandas as pd
from openpyxl import Workbook
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def _create_source_xlsx() -> bytes:
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        pd.DataFrame({"Data": ["2026-01-01"], "Atividade": ["Escavacao"]}).to_excel(writer, sheet_name="Obra", index=False)
    buffer.seek(0)
    return buffer.read()

def _create_template_xlsx() -> bytes:
    wb = Workbook()
    ws = wb.active
    ws["A1"] = "RDO"
    buffer = io.BytesIO()
    wb.save(buffer)
    buffer.seek(0)
    return buffer.read()

def test_preview_source_endpoint():
    data = _create_source_xlsx()
    response = client.post("/api/preview/source", files={"file": ("medicao.xlsx", data, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")})
    assert response.status_code == 200
    body = response.json()
    assert len(body["sheets"]) == 1
    assert body["sheets"][0]["name"] == "Obra"

def test_preview_template_endpoint():
    data = _create_template_xlsx()
    response = client.post("/api/preview/template", files={"file": ("template.xlsx", data, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")})
    assert response.status_code == 200
    assert len(response.json()["sheets"]) >= 1

def test_preview_source_rejects_csv():
    response = client.post("/api/preview/source", files={"file": ("data.csv", b"a,b\n1,2", "text/csv")})
    assert response.status_code == 400

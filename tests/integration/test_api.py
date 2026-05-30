import io
import json
import pandas as pd
from openpyxl import Workbook
from fastapi.testclient import TestClient
from src.main import app

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


def test_generate_endpoint():
    source_data = _create_source_xlsx()
    template_data = _create_template_xlsx()

    config = {
        "contract": {"start_date": "2026-01-01", "prazo_dias": 30, "mes": 1, "ano": 2026},
        "mappings": [{"formatTemplate": "{Atividade}", "templateCell": "B3", "sourceColumns": ["Atividade"]}],
        "listSeparator": ", ",
        "listConnector": " e ",
    }

    response = client.post(
        "/api/generate",
        files={
            "source": ("medicao.xlsx", source_data, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"),
            "template": ("template.xlsx", template_data, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"),
        },
        data={"config": json.dumps(config)},
    )

    assert response.status_code == 200
    assert "spreadsheetml" in response.headers["content-type"]
    assert len(response.content) > 0

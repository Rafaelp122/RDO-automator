import json
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import StreamingResponse
from services.web_report_service import generate_report
from models.api_models import GenerateConfig

router = APIRouter(tags=["generate"])


@router.post("/generate")
async def generate_endpoint(
    source: UploadFile = File(...),
    template: UploadFile = File(...),
    config: str = Form(...),
):
    if not source.filename.endswith((".xlsx", ".xls")):
        raise HTTPException(400, "Arquivo de origem deve ser .xlsx ou .xls")
    if not template.filename.endswith(".xlsx"):
        raise HTTPException(400, "Template deve ser .xlsx")

    try:
        config_dict = json.loads(config)
        parsed = GenerateConfig(**config_dict)
    except Exception as e:
        raise HTTPException(400, f"Config JSON invalido: {e}")

    source_bytes = await source.read()
    template_bytes = await template.read()

    output = generate_report(
        source_bytes,
        template_bytes,
        config_dict,
    )

    return StreamingResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=Diario_Consolidado.xlsx"},
    )

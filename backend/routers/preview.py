from fastapi import APIRouter, UploadFile, File, HTTPException
from services.preview_service import preview_source, preview_template
from models.api_models import SourcePreviewResponse, TemplatePreviewResponse

router = APIRouter(tags=["preview"])

@router.post("/preview/source", response_model=SourcePreviewResponse)
async def preview_source_endpoint(file: UploadFile = File(...)):
    if not file.filename.endswith((".xlsx", ".xls")):
        raise HTTPException(400, "Apenas arquivos .xlsx ou .xls sao aceitos")
    contents = await file.read()
    return preview_source(contents, file.filename)

@router.post("/preview/template", response_model=TemplatePreviewResponse)
async def preview_template_endpoint(file: UploadFile = File(...)):
    if not file.filename.endswith(".xlsx"):
        raise HTTPException(400, "Apenas arquivos .xlsx sao aceitos")
    contents = await file.read()
    return preview_template(contents, file.filename)

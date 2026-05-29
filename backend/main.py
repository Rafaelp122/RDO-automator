from fastapi import FastAPI, Request, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse

from exceptions import AppError
from schemas import SourcePreviewResponse, TemplatePreviewResponse
from excel import preview_source, preview_template, generate_report

app = FastAPI(title="RDO Automator API", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173", "https://rdo.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(AppError)
async def app_error_handler(request: Request, exc: AppError):
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.message})


@app.post("/api/preview/source", response_model=SourcePreviewResponse)
def preview_source_route(file: UploadFile = File(...)):
    contents = file.file.read()
    return preview_source(contents, file.filename)


@app.post("/api/preview/template", response_model=TemplatePreviewResponse)
def preview_template_route(file: UploadFile = File(...)):
    contents = file.file.read()
    return preview_template(contents, file.filename)


@app.post("/api/generate")
def generate_route(
    source: UploadFile = File(...),
    template: UploadFile = File(...),
    config: str = Form(...),
):
    source_bytes = source.file.read()
    template_bytes = template.file.read()
    output = generate_report(source_bytes, template_bytes, source.filename, template.filename, config)
    return StreamingResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=Diario_Consolidado.xlsx"},
    )

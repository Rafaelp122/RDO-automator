from typing import Annotated

from fastapi import APIRouter, File, Form, UploadFile
from fastapi.responses import StreamingResponse

from src.excel import ReportGenerator, preview_source, preview_template
from src.schemas import SourcePreviewResponse, TemplatePreviewResponse

router = APIRouter(prefix="/api")


@router.post("/preview/source", response_model=SourcePreviewResponse)
async def preview_source_route(file: Annotated[UploadFile, File()]):
    """Retorna as abas, colunas e as 20 primeiras linhas da planilha de origem.

    Aceita arquivos .xlsx ou .xls. A coluna de data é detectada automaticamente
    e uma coluna auxiliar ``_dia_aux`` é gerada internamente (não exposta no preview).
    """
    contents = await file.read()
    return preview_source(contents, file.filename or "")


@router.post("/preview/template", response_model=TemplatePreviewResponse)
async def preview_template_route(file: Annotated[UploadFile, File()]):
    """Retorna células, imagens (base64) e ranges mesclados do template Excel.

    Usado pelo frontend para renderizar a interface de mapeamento célula-a-célula,
    permitindo que o usuário clique visualmente nas células de destino.
    """
    contents = await file.read()
    return preview_template(contents, file.filename or "")


@router.post("/generate")
async def generate_route(
    source: Annotated[UploadFile, File()],
    template: Annotated[UploadFile, File()],
    config: Annotated[str, Form()],
):
    """Gera o relatório consolidado (Diário de Obra) a partir da planilha de dados,
    do template Excel e da configuração de mapeamento (JSON string).

    Para cada dia do mês do contrato, clona o template, filtra os dados da origem
    por dia e preenche as células mapeadas com os valores formatados.

    Retorna o arquivo .xlsx como download (StreamingResponse).
    """
    source_bytes = await source.read()
    template_bytes = await template.read()
    output = ReportGenerator(
        source_bytes, template_bytes, source.filename or "", template.filename or "", config
    ).generate()
    return StreamingResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=Diario_Consolidado.xlsx"},
    )

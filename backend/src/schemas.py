from pydantic import BaseModel, Field
from typing import Optional


class SheetData(BaseModel):
    """Dados de uma aba da planilha de origem, retornados no preview."""

    name: str
    columns: list[str]
    data: list[list[str]]


class SourcePreviewResponse(BaseModel):
    """Resposta do preview da planilha de origem.

    Inclui as abas com suas colunas e linhas (limitadas a 20),
    além de siglas candidatas extraídas automaticamente dos dados.
    """

    sheets: list[SheetData]
    filename: str
    suggestedAcronyms: list[str] = []


class CellData(BaseModel):
    """Célula individual do template, com coordenada e formatação da fonte."""

    coord: str
    row: int
    col: int
    value: Optional[str] = None
    font: Optional[dict[str, Optional[int | bool]]] = None


class ImageData(BaseModel):
    """Imagem embutida no template, serializada em base64 com posição."""

    b64: str
    position: dict[str, int]


class TemplateSheet(BaseModel):
    """Aba do template com células, imagens e ranges mesclados."""

    name: str
    cells: list[CellData]
    images: list[ImageData]
    merged: list[dict] = []


class TemplatePreviewResponse(BaseModel):
    """Resposta do preview do template com todas as abas."""

    sheets: list[TemplateSheet]


class ContractConfig(BaseModel):
    """Metadados do contrato: vigência, mês e ano de referência."""

    start_date: str = Field(description="YYYY-MM-DD")
    prazo_dias: int
    mes: int
    ano: int


class MappingItem(BaseModel):
    """Mapeamento entre colunas de origem e célula do template.

    Define qual template de texto será aplicado aos valores extraídos
    das colunas especificadas e em qual célula do template será inserido.
    """

    formatTemplate: str
    templateCell: str
    sourceColumns: list[str]


class GenerateConfig(BaseModel):
    """Configuração completa para geração do relatório.

    Inclui dados do contrato, mapeamentos coluna → célula,
    lista de siglas a preservar em maiúsculo e separadores de texto.
    """

    contract: ContractConfig
    mappings: list[MappingItem]
    siglas: list[str] = []
    listSeparator: str = ", "
    listConnector: str = " e "


class ErrorResponse(BaseModel):
    """Resposta padronizada para erros da API."""

    detail: str
    code: str = "application_error"
    errors: list[str] = []

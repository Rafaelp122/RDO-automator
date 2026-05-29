from pydantic import BaseModel, Field
from typing import Optional


class SheetData(BaseModel):
    name: str
    columns: list[str]
    data: list[list[str]]


class SourcePreviewResponse(BaseModel):
    sheets: list[SheetData]
    filename: str


class CellData(BaseModel):
    coord: str
    row: int
    col: int
    value: Optional[str] = None
    font: Optional[dict[str, Optional[int | bool]]] = None


class ImageData(BaseModel):
    b64: str
    position: dict[str, int]


class TemplateSheet(BaseModel):
    name: str
    cells: list[CellData]
    images: list[ImageData]
    merged: list[dict] = []


class TemplatePreviewResponse(BaseModel):
    sheets: list[TemplateSheet]


class ContractConfig(BaseModel):
    start_date: str = Field(description="YYYY-MM-DD")
    prazo_dias: int
    mes: int
    ano: int


class MappingItem(BaseModel):
    formatTemplate: str
    templateCell: str
    sourceColumns: list[str]


class GenerateConfig(BaseModel):
    contract: ContractConfig
    mappings: list[MappingItem]
    listSeparator: str = ", "
    listConnector: str = " e "


class ErrorResponse(BaseModel):
    detail: str
    errors: list[str] = []

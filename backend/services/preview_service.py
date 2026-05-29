import base64
import io
from ..utils.logger import logger
from ..utils.excel_loader import ExcelLoader
from ..utils.template_manager import TemplateManager
from ..models.api_models import (
    SourcePreviewResponse, SheetData,
    TemplatePreviewResponse, TemplateSheet,
    CellData, ImageData
)


def preview_source(file_bytes: bytes, filename: str) -> SourcePreviewResponse:
    buffer = io.BytesIO(file_bytes)
    loader = ExcelLoader(buffer)
    all_sheets = loader.load_all_sheets()

    sheets = []
    for name, df in all_sheets.items():
        cols = [str(c) for c in df.columns if c != "_dia_aux"]
        rows = df[cols].fillna("").head(20).values.tolist()
        string_rows = [[str(cell) for cell in row] for row in rows]
        sheets.append(SheetData(name=name, columns=cols, data=string_rows))

    logger.info("Preview source: %d sheets from %s", len(sheets), filename)
    return SourcePreviewResponse(sheets=sheets, filename=filename)


def preview_template(file_bytes: bytes, filename: str) -> TemplatePreviewResponse:
    buffer = io.BytesIO(file_bytes)
    tm = TemplateManager(buffer)
    tm.load()

    all_sheets = []
    for ws in tm.wb.worksheets:
        cells = []
        for row in ws.iter_rows():
            for cell in row:
                font_info = None
                if cell.font:
                    font_info = {
                        "bold": cell.font.bold,
                        "size": cell.font.size,
                    }
                cells.append(CellData(
                    coord=cell.coordinate,
                    row=cell.row,
                    col=cell.column,
                    value=str(cell.value) if cell.value is not None else None,
                    font=font_info,
                ))

        images = []
        if hasattr(ws, "_images"):
            for img in ws._images:
                try:
                    img_bytes = img._data()
                    b64 = base64.b64encode(img_bytes).decode()
                    position = {}
                    if hasattr(img.anchor, "_from"):
                        position["col"] = img.anchor._from.col
                        position["row"] = img.anchor._from.row
                        position["colOff"] = img.anchor._from.colOff
                        position["rowOff"] = img.anchor._from.rowOff
                    images.append(ImageData(b64=f"data:image/png;base64,{b64}", position=position))
                except Exception as e:
                    logger.warning("Failed to extract image: %s", e)

        all_sheets.append(TemplateSheet(name=ws.title, cells=cells, images=images, merged=[]))

    logger.info("Preview template: %d sheets from %s", len(all_sheets), filename)
    return TemplatePreviewResponse(sheets=all_sheets)

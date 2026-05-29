# Web Migration Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Migrate RDO Automator from PyQt6 desktop app to web app: FastAPI backend (Cloud Run) + React frontend (Vercel), eliminating TOML config in favor of visual interaction.

**Architecture:** Two-codebase monorepo. Backend reuses 100% of the Python processing engine (processor, report_builder, template_manager) adapted for BytesIO. Frontend replaces PySide6 with React Vite single-page app using accordion UX with visual preview and cell-click mapping.

**Tech Stack:** FastAPI, uvicorn, openpyxl, pandas, pydantic, python-multipart (backend) — React, Vite, TypeScript, Tailwind CSS, framer-motion (frontend) — Docker, Cloud Run, Vercel (deploy)

> **Backend import convention:** All code under `backend/` uses relative imports (e.g. `from utils.logger import logger`). All test code uses absolute imports via root (e.g. `from backend.utils.logger import logger`). Run all `uv run pytest` commands from the `backend/` directory (where `pyproject.toml` lives) so that `pythonpath = [".."]` resolves correctly for test imports.

---

## File Structure

```
report_automator/
├── backend/
│   ├── pyproject.toml
│   ├── .python-version
│   ├── Dockerfile
│   ├── main.py                       # FastAPI app, CORS, lifespan
│   ├── routers/
│   │   ├── preview.py                # POST /api/preview/source, /api/preview/template
│   │   └── generate.py               # POST /api/generate
│   ├── models/
│   │   └── api_models.py             # Pydantic request/response schemas
│   ├── services/
│   │   ├── preview_service.py        # Excel → JSON serialization
│   │   ├── web_report_service.py     # Simplified report orchestration (no ReportConfig)
│   │   └── report_builder.py         # Adapted from src/app/core/
│   └── utils/
│       ├── processor.py              # Copied from src/app/core/ (zero change)
│       ├── validator.py              # Copied from src/app/core/ (zero change)
│       ├── excel_loader.py           # Adapted for BytesIO
│       ├── template_manager.py       # Adapted for BytesIO
│       └── logger.py                 # Copied from src/app/core/ (zero change)
├── frontend/                         # React Vite (Vercel)
│   └── [see Task 13 for full tree]
├── tests/                            # Backend tests
│   ├── conftest.py
│   ├── unit/
│   │   ├── test_preview_service.py
│   │   └── test_web_report_service.py
│   └── integration/
│       └── test_api.py
└── src/app/                          # Original PyQt code (reference only)
```

---

### Task 1: Backend Project Scaffold

**Files:**
- Create: `backend/.python-version`
- Create: `backend/pyproject.toml`
- Create: `backend/Dockerfile`

- [ ] **Step 1: Create backend directory and .python-version**

```bash
mkdir -p backend/routers backend/models backend/services backend/utils
echo "3.14" > backend/.python-version
```

- [ ] **Step 2: Write backend/pyproject.toml**

```toml
[project]
name = "rdo-automator-backend"
version = "2.0.0"
description = "RDO Automator web API backend"
requires-python = ">=3.11"
dependencies = [
    "fastapi>=0.115.0",
    "uvicorn[standard]>=0.34.0",
    "openpyxl>=3.1.0",
    "pandas>=2.0.0",
    "pydantic>=2.13.3",
    "python-multipart>=0.0.20",
    "pillow>=10.0.0",
]

[dependency-groups]
dev = [
    "pytest>=9.0.3",
    "pytest-cov>=7.1.0",
    "httpx>=0.28.0",
]

[tool.pytest.ini_options]
testpaths = ["../tests"]
python_files = "test_*.py"
pythonpath = [".."]
addopts = "-v --tb=short"
```

- [ ] **Step 3: Write backend/Dockerfile**

```dockerfile
FROM python:3.14-slim
WORKDIR /app
COPY backend/ .
RUN pip install uv && uv sync --frozen --no-dev
CMD ["uv", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
```

- [ ] **Step 4: Install dependencies and verify**

```bash
uv sync
```

- [ ] **Step 5: Commit**

```bash
git add backend/.python-version backend/pyproject.toml backend/Dockerfile
git commit -m "feat: scaffold backend project with FastAPI deps and Dockerfile"
```

---

### Task 2: Copy Utility Modules (No Changes)

**Files:**
- Create: `backend/utils/processor.py`
- Create: `backend/utils/logger.py`
- Create: `backend/utils/__init__.py`
- Create: `backend/services/__init__.py`
- Create: `backend/models/__init__.py`
- Create: `backend/routers/__init__.py`

- [ ] **Step 1: Copy processor.py (zero modifications)**

```bash
cp src/app/core/processor.py backend/utils/processor.py
```

- [ ] **Step 2: Copy logger.py with adapted import path**

Write `backend/utils/logger.py`:

```python
import logging
from pathlib import Path

def setup_logger(name="rdo_automator", log_path=None, level=logging.INFO):
    if log_path is None:
        log_path = Path("/tmp/rdo_automator.log")

    log_path.parent.mkdir(parents=True, exist_ok=True)

    formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    file_handler = logging.FileHandler(str(log_path), encoding="utf-8")
    file_handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(level)

    if not logger.handlers:
        logger.addHandler(console_handler)
        logger.addHandler(file_handler)

    return logger

logger = setup_logger()
```

- [ ] **Step 3: Copy validator.py with minimal adaptation**

Write `backend/utils/validator.py`:

```python
import re
import pandas as pd
from io import BytesIO

class ReportValidator:
    @staticmethod
    def is_valid_excel_coordinate(coord: str) -> bool:
        return bool(re.match(r'^[A-Z]{1,3}[1-9][0-9]*$', str(coord).upper()))

    @staticmethod
    def validate_coordinates(positions: dict) -> tuple[list[str], dict[str, str]]:
        errors = []
        field_errors = {}
        for name, cell in positions.items():
            if cell and not ReportValidator.is_valid_excel_coordinate(cell):
                msg = f"Celula '{cell}' para '{name}' e invalida."
                errors.append(msg)
                field_errors[name] = msg
        return errors, field_errors

    @staticmethod
    def validate_columns_in_file(file_bytes: bytes, header_row: int, expected_columns: list[str]) -> tuple[list[str], dict[str, str]]:
        errors = []
        field_errors = {}
        try:
            buffer = BytesIO(file_bytes)
            with pd.ExcelFile(buffer) as xls:
                for sheet_name in xls.sheet_names:
                    df_header = pd.read_excel(xls, sheet_name=sheet_name, header=header_row, nrows=0)
                    for col in expected_columns:
                        if col not in df_header.columns:
                            msg = f"Aba '{sheet_name}': Coluna '{col}' nao encontrada."
                            errors.append(msg)
                            field_errors[f"column_{col}"] = msg
        except Exception as e:
            errors.append(f"Erro ao ler arquivo Excel: {e}")
        return errors, field_errors
```

- [ ] **Step 4: Create empty __init__.py files**

```bash
touch backend/utils/__init__.py backend/services/__init__.py backend/models/__init__.py backend/routers/__init__.py
```

- [ ] **Step 5: Verify imports work**

```bash
cd backend && uv run python -c "from utils.processor import TextProcessor; print('OK')"
cd backend && uv run python -c "from utils.logger import logger; print('OK')"
cd backend && uv run python -c "from utils.validator import ReportValidator; print('OK')"
```

- [ ] **Step 6: Commit**

```bash
git add backend/utils/
git commit -m "feat: copy and adapt processor, validator, logger to backend/utils"
```

---

### Task 3: Adapt Excel Loader for BytesIO

**Files:**
- Create: `backend/utils/excel_loader.py`
- Test: `tests/unit/test_excel_loader.py`

- [ ] **Step 1: Write the failing test**

Write `tests/unit/test_excel_loader.py`:

```python
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
```

- [ ] **Step 2: Run test to verify it fails**

```bash
cd backend && uv run pytest ../tests/unit/test_excel_loader.py -v
```

Expected: FAIL — `ModuleNotFoundError` or `ImportError`

- [ ] **Step 3: Write backend/utils/excel_loader.py**

```python
import pandas as pd
from typing import Dict, BinaryIO
from utils.logger import logger

class ExcelLoader:
    def __init__(self, file: BinaryIO, header_row: int = 0):
        self.file = file
        self.header_row = header_row

    def load_all_sheets(self) -> Dict[str, pd.DataFrame]:
        logger.info("Lendo dados do arquivo (header na linha %d)", self.header_row)
        abas = pd.read_excel(self.file, sheet_name=None, header=self.header_row)
        return self._normalize_dates(abas)

    def _normalize_dates(self, abas: Dict[str, pd.DataFrame]) -> Dict[str, pd.DataFrame]:
        for nome_aba, df in abas.items():
            col_data = self._find_date_column(df)
            if col_data:
                df[col_data] = pd.to_datetime(df[col_data], errors="coerce")
                df["_dia_aux"] = df[col_data].dt.day
            else:
                df["_dia_aux"] = None
        return abas

    @staticmethod
    def _find_date_column(df: pd.DataFrame) -> str:
        for col in df.columns:
            if "data" in str(col).lower():
                return col
        return ""
```

- [ ] **Step 4: Run test to verify it passes**

```bash
cd backend && uv run pytest ../tests/unit/test_excel_loader.py -v
```

Expected: 3 PASS

- [ ] **Step 5: Commit**

```bash
git add backend/utils/excel_loader.py tests/unit/test_excel_loader.py
git commit -m "feat: adapt ExcelLoader to accept BytesIO instead of file path"
```

---

### Task 4: Adapt Template Manager for BytesIO

**Files:**
- Modify: `backend/utils/template_manager.py`
- Test: `tests/unit/test_template_manager.py`

- [ ] **Step 1: Write the failing test**

Write `tests/unit/test_template_manager.py`:

```python
import io
from openpyxl import Workbook
from backend.utils.template_manager import TemplateManager

def _create_template_xlsx() -> bytes:
    wb = Workbook()
    ws = wb.active
    ws["A1"] = "RDO - RELATORIO DIARIO DE OBRA"
    ws["B3"] = "Servicos:"
    buffer = io.BytesIO()
    wb.save(buffer)
    buffer.seek(0)
    return buffer.read()

def test_load_from_bytesio():
    data = _create_template_xlsx()
    buffer = io.BytesIO(data)
    tm = TemplateManager(buffer)
    tm.load()
    assert tm.wb is not None
    assert tm.ws_template is not None
    assert tm.ws_template["A1"].value == "RDO - RELATORIO DIARIO DE OBRA"

def test_clone_worksheet():
    data = _create_template_xlsx()
    buffer = io.BytesIO(data)
    tm = TemplateManager(buffer)
    tm.load()
    ws = tm.clone_worksheet("01-01")
    assert ws.title == "01-01"
    assert ws["A1"].value == "RDO - RELATORIO DIARIO DE OBRA"
    assert len(tm.wb.sheetnames) == 2

def test_save_to_bytesio():
    data = _create_template_xlsx()
    buffer = io.BytesIO(data)
    tm = TemplateManager(buffer)
    tm.load()
    tm.clone_worksheet("01-01")
    output = io.BytesIO()
    tm.save_to_stream(output)
    output.seek(0)
    assert output.read(4) == b"PK\x03\x04"
```

- [ ] **Step 2: Run test to verify it fails**

```bash
cd backend && uv run pytest ../tests/unit/test_template_manager.py -v
```

Expected: FAIL — `ModuleNotFoundError`

- [ ] **Step 3: Write backend/utils/template_manager.py**

```python
import io
from copy import deepcopy
from openpyxl import load_workbook
from openpyxl.drawing.image import Image as OpenpyxlImage
from typing import BinaryIO
from utils.logger import logger

class TemplateManager:
    def __init__(self, file: BinaryIO):
        self.file = file
        self.wb = None
        self.ws_template = None
        self.extracted_images = []

    def load(self):
        try:
            self.wb = load_workbook(self.file)
            self.ws_template = self.wb.active
            self.extracted_images = []
            if hasattr(self.ws_template, "_images"):
                for img in self.ws_template._images:
                    try:
                        img_bytes = img._data()
                        anchor = img.anchor
                        self.extracted_images.append({"bytes": img_bytes, "anchor": anchor})
                    except Exception as e:
                        logger.warning("Nao foi possivel ler uma imagem do template: %s", e)
                self.ws_template._images = []
        except Exception as e:
            logger.exception("Erro ao abrir template Excel")
            raise ValueError(f"O arquivo de template nao e um Excel (.xlsx) valido: {e}")

    def clone_worksheet(self, title: str):
        new_ws = self.wb.copy_worksheet(self.ws_template)
        new_ws.title = title
        for img_info in self.extracted_images:
            try:
                new_img = OpenpyxlImage(io.BytesIO(img_info["bytes"]))
                new_img.anchor = deepcopy(img_info["anchor"])
                new_ws.add_image(new_img)
            except Exception as e:
                logger.warning("Nao foi possivel injetar imagem na aba %s: %s", title, e)
        return new_ws

    def save_to_stream(self, stream: BinaryIO):
        if self.ws_template:
            self.wb.remove(self.ws_template)
        self.wb.save(stream)
        logger.info("Relatorio salvo no stream")
```

- [ ] **Step 4: Run test to verify it passes**

```bash
cd backend && uv run pytest ../tests/unit/test_template_manager.py -v
```

Expected: 3 PASS

- [ ] **Step 5: Commit**

```bash
git add backend/utils/template_manager.py tests/unit/test_template_manager.py
git commit -m "feat: adapt TemplateManager to accept BytesIO, add save_to_stream"
```

---

### Task 5: Create API Models (Pydantic)

**Files:**
- Create: `backend/models/api_models.py`

- [ ] **Step 1: Write backend/models/api_models.py**

```python
from pydantic import BaseModel, Field
from typing import Optional


class SheetData(BaseModel):
    name: str
    columns: list[str]
    data: list[list]


class SourcePreviewResponse(BaseModel):
    sheets: list[SheetData]
    filename: str


class CellData(BaseModel):
    coord: str
    row: int
    col: int
    value: Optional[str] = None
    font: Optional[dict] = None


class ImageData(BaseModel):
    b64: str
    position: dict


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
```

- [ ] **Step 2: Verify module imports**

```bash
cd backend && uv run python -c "from models.api_models import GenerateConfig; print('OK')"
```

- [ ] **Step 3: Commit**

```bash
git add backend/models/api_models.py
git commit -m "feat: add Pydantic API models for preview and generate endpoints"
```

---

### Task 6: Create Preview Service

**Files:**
- Create: `backend/services/preview_service.py`
- Test: `tests/unit/test_preview_service.py`

- [ ] **Step 1: Write backend/services/preview_service.py**

```python
import base64
import io
from utils.logger import logger
from utils.excel_loader import ExcelLoader
from utils.template_manager import TemplateManager
from models.api_models import (
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
```

- [ ] **Step 2: Write integration test**

Write `tests/unit/test_preview_service.py`:

```python
import io
import pandas as pd
from openpyxl import Workbook
from backend.services.preview_service import preview_source, preview_template

def _create_source_xlsx() -> bytes:
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        pd.DataFrame({"Data": ["2026-01-01"], "Atividade": ["Escavacao"]}).to_excel(writer, sheet_name="Obra", index=False)
    buffer.seek(0)
    return buffer.read()

def _create_template_xlsx() -> bytes:
    wb = Workbook()
    ws = wb.active
    ws["A1"] = "RDO Header"
    ws["B3"] = "Servicos:"
    buffer = io.BytesIO()
    wb.save(buffer)
    buffer.seek(0)
    return buffer.read()

def test_preview_source():
    data = _create_source_xlsx()
    result = preview_source(data, "medicao.xlsx")
    assert len(result.sheets) == 1
    assert result.sheets[0].name == "Obra"
    assert "Atividade" in result.sheets[0].columns

def test_preview_template():
    data = _create_template_xlsx()
    result = preview_template(data, "template.xlsx")
    assert len(result.sheets) >= 1
    assert any(c.value == "RDO Header" for c in result.sheets[0].cells)
```

- [ ] **Step 3: Run tests**

```bash
cd backend && uv run pytest ../tests/unit/test_preview_service.py -v
```

Expected: 2 PASS

- [ ] **Step 4: Commit**

```bash
git add backend/services/preview_service.py tests/unit/test_preview_service.py
git commit -m "feat: add preview service for Excel source and template serialization"
```

---

### Task 7: Create FastAPI App and Preview Router

**Files:**
- Create: `backend/main.py`
- Create: `backend/routers/preview.py`
- Test: `tests/integration/test_api.py`

- [ ] **Step 1: Write backend/main.py**

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import preview

app = FastAPI(title="RDO Automator API", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "https://rdo.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(preview.router, prefix="/api")
```

- [ ] **Step 2: Write backend/routers/preview.py**

```python
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
```

- [ ] **Step 3: Write integration test**

Write `tests/integration/test_api.py`:

```python
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
```

- [ ] **Step 4: Run tests**

```bash
cd backend && uv run pytest ../tests/integration/test_api.py -v
```

Expected: 3 PASS

- [ ] **Step 5: Verify server starts**

```bash
cd backend && timeout 5 uv run uvicorn main:app --host 0.0.0.0 --port 8000 || true
```

Should print "Uvicorn running on..."

- [ ] **Step 6: Commit**

```bash
git add backend/main.py backend/routers/preview.py tests/integration/test_api.py
git commit -m "feat: add FastAPI app with CORS and preview endpoints"
```

---

### Task 8: Create Web Report Service

**Files:**
- Create: `backend/services/web_report_service.py`
- Create: `backend/services/report_builder.py`
- Test: `tests/unit/test_web_report_service.py`

- [ ] **Step 1: Write adapted report_builder (minimal, no ReportConfig)**

Write `backend/services/report_builder.py`:

```python
import calendar
import io
from datetime import datetime, timedelta
import pandas as pd
from typing import Callable, Optional
from utils.logger import logger
from utils.processor import TextProcessor
from utils.excel_loader import ExcelLoader
from utils.template_manager import TemplateManager


class WebReportBuilder:
    def __init__(self, source_file: bytes, template_file: bytes, header_row: int = 0):
        self.source_file = source_file
        self.template_file = template_file
        self.header_row = header_row

    def build(
        self,
        contract: dict,
        mappings: list[dict],
        list_separator: str = ", ",
        list_connector: str = " e ",
        progress_callback: Optional[Callable] = None,
    ) -> io.BytesIO:
        loader = ExcelLoader(io.BytesIO(self.source_file), self.header_row)
        abas_origem = loader.load_all_sheets()

        tm = TemplateManager(io.BytesIO(self.template_file))
        tm.load()

        ano = contract["ano"]
        mes = contract["mes"]
        _, ultimo_dia = calendar.monthrange(ano, mes)

        data_inicio = datetime.strptime(contract["start_date"], "%Y-%m-%d")
        prazo_dias = contract["prazo_dias"]
        data_final = data_inicio + timedelta(days=prazo_dias)

        logger.info("Iniciando loop diario para %d/%d (%d dias)", mes, ano, ultimo_dia)

        for dia in range(1, ultimo_dia + 1):
            if progress_callback:
                progress_callback(int(dia / ultimo_dia * 100))

            data_atual = datetime(ano, mes, dia)
            ws = tm.clone_worksheet(data_atual.strftime("%d-%m"))

            self._fill_dynamic_mappings(ws, abas_origem, dia, mappings, list_separator, list_connector)

        output = io.BytesIO()
        tm.save_to_stream(output)
        output.seek(0)
        return output

    def _fill_dynamic_mappings(self, ws, abas_origem, dia, mappings, list_separator, list_connector):
        for mapping in mappings:
            celula = mapping.get("templateCell", "")
            if not celula:
                continue

            format_template = mapping.get("formatTemplate", "")
            source_columns = mapping.get("sourceColumns", [])

            combined_values = {}
            for sheet_name, df in abas_origem.items():
                if "_dia_aux" not in df.columns:
                    continue
                filtro = df[df["_dia_aux"] == dia]
                if filtro.empty:
                    continue
                for col in source_columns:
                    if col in filtro.columns:
                        vals = filtro[col].dropna().unique().tolist()
                        vals = [v for v in vals if str(v).strip() and str(v).lower() != "nan"]
                        if vals:
                            if col not in combined_values:
                                combined_values[col] = []
                            combined_values[col].extend(vals)

            if not combined_values:
                ws[celula] = None
                continue

            for col in combined_values:
                combined_values[col] = list(dict.fromkeys(combined_values[col]))

            resumo = TextProcessor.formatar_resumo(combined_values, format_template, list_separator, list_connector)
            if resumo:
                ws[celula] = resumo
            else:
                ws[celula] = None
```

- [ ] **Step 2: Write web_report_service.py**

Write `backend/services/web_report_service.py`:

```python
import io
from services.report_builder import WebReportBuilder
from utils.logger import logger


def generate_report(source_bytes: bytes, template_bytes: bytes, config: dict) -> io.BytesIO:
    builder = WebReportBuilder(source_bytes, template_bytes)

    contract = config["contract"]
    mappings = config["mappings"]
    list_separator = config.get("listSeparator", ", ")
    list_connector = config.get("listConnector", " e ")

    logger.info("Gerando relatorio: mes=%d/%d, %d mappings", contract["mes"], contract["ano"], len(mappings))

    output = builder.build(
        contract=contract,
        mappings=mappings,
        list_separator=list_separator,
        list_connector=list_connector,
    )

    logger.info("Relatorio gerado com sucesso")
    return output
```

- [ ] **Step 3: Write test**

Write `tests/unit/test_web_report_service.py`:

```python
import io
import pandas as pd
from openpyxl import Workbook, load_workbook
from backend.services.web_report_service import generate_report

def _create_source_xlsx() -> bytes:
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        df = pd.DataFrame({
            "Data": ["2026-01-02"],
            "Atividade": ["Concretagem"],
        })
        df.to_excel(writer, sheet_name="Obra", index=False)
    buffer.seek(0)
    return buffer.read()

def _create_template_xlsx() -> bytes:
    wb = Workbook()
    ws = wb.active
    ws["A1"] = "RDO"
    ws["B3"] = ""
    buffer = io.BytesIO()
    wb.save(buffer)
    buffer.seek(0)
    return buffer.read()

def test_generate_report():
    source = _create_source_xlsx()
    template = _create_template_xlsx()

    config = {
        "contract": {"start_date": "2026-01-01", "prazo_dias": 30, "mes": 1, "ano": 2026},
        "mappings": [{"formatTemplate": "{Atividade}", "templateCell": "B3", "sourceColumns": ["Atividade"]}],
        "listSeparator": ", ",
        "listConnector": " e ",
    }

    output = generate_report(source, template, config)
    output.seek(0)

    wb = load_workbook(output)
    sheets = wb.sheetnames
    assert len(sheets) >= 30
    assert "05-01" in sheets
```

- [ ] **Step 4: Run test**

```bash
cd backend && uv run pytest ../tests/unit/test_web_report_service.py -v
```

Expected: 1 PASS

- [ ] **Step 5: Commit**

```bash
git add backend/services/web_report_service.py backend/services/report_builder.py tests/unit/test_web_report_service.py
git commit -m "feat: add web report service and builder (no ReportConfig dependency)"
```

---

### Task 9: Create Generate Router

**Files:**
- Create: `backend/routers/generate.py`
- Modify: `tests/integration/test_api.py` (add generate test)

- [ ] **Step 1: Write backend/routers/generate.py**

```python
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
```

- [ ] **Step 2: Register router in main.py**

In `backend/main.py`, add after existing import:

```python
from routers import generate

app.include_router(generate.router, prefix="/api")
```

- [ ] **Step 3: Add generate test to tests/integration/test_api.py**

Append to `tests/integration/test_api.py`:

```python
import json

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
    assert response.headers["content-type"] == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    assert len(response.content) > 0
```

- [ ] **Step 4: Run all integration tests**

```bash
cd backend && uv run pytest ../tests/integration/test_api.py -v
```

Expected: 4 PASS

- [ ] **Step 5: Commit**

```bash
git add backend/routers/generate.py backend/main.py tests/integration/test_api.py
git commit -m "feat: add generate endpoint returning .xlsx download"
```

---

### Task 10: Bootstrap Frontend from Prototype

**Files:**
- Move: `rdo-automator(1)/*` → `frontend/`
- Modify: `frontend/package.json` (name field)
- Create: `frontend/.env`

- [ ] **Step 1: Move prototype to frontend directory**

```bash
cp -r "rdo-automator(1)" frontend
```

- [ ] **Step 2: Update name and add VITE_API_URL env**

Edit `frontend/package.json`: change `"name": "rdo-automator"` to `"name": "rdo-automator-frontend"`.

Write `frontend/.env`:

```
VITE_API_URL=http://localhost:8000
```

- [ ] **Step 3: Install and verify build**

```bash
npm install --prefix frontend
npm run build --prefix frontend
```

Expected: Build succeeds with no errors.

- [ ] **Step 4: Commit**

```bash
git add frontend/
git commit -m "feat: bootstrap frontend from prototype, add env config"
```

---

### Task 11: Create API Service Layer (Frontend)

**Files:**
- Create: `frontend/src/services/api.ts`
- Create: `frontend/src/types.ts` (updated)
- Modify: `frontend/src/components/Header.tsx` (v2.0 text)

- [ ] **Step 1: Update types.ts**

Write `frontend/src/types.ts`:

```ts
export type Sheet = {
  name: string;
  selected: boolean;
  columns: string[];
  selectedColumns: string[];
  data: string[][];
};

export type MappingData = {
  id: string;
  sourceColumns: string[];
  templateCell: string;
  formatTemplate: string;
};

export type AppState = {
  dataUploadDone: boolean;
  templateUploadDone: boolean;
  mappings: MappingData[];
  sheets: Sheet[];
};

export type SourcePreviewResponse = {
  sheets: { name: string; columns: string[]; data: string[][] }[];
  filename: string;
};

export type CellData = {
  coord: string;
  row: number;
  col: number;
  value: string | null;
  font: { bold: boolean; size: number } | null;
};

export type ImageData = {
  b64: string;
  position: Record<string, number>;
};

export type TemplateSheet = {
  name: string;
  cells: CellData[];
  images: ImageData[];
  merged: { start: string; end: string }[];
};

export type TemplatePreviewResponse = {
  sheets: TemplateSheet[];
};

export type ContractConfig = {
  start_date: string;
  prazo_dias: number;
  mes: number;
  ano: number;
};

export type MappingItem = {
  formatTemplate: string;
  templateCell: string;
  sourceColumns: string[];
};

export type GenerateConfig = {
  contract: ContractConfig;
  mappings: MappingItem[];
  listSeparator: string;
  listConnector: string;
};
```

- [ ] **Step 2: Write api.ts**

Write `frontend/src/services/api.ts`:

```ts
import type { SourcePreviewResponse, TemplatePreviewResponse, GenerateConfig } from "../types";

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

export async function previewSource(file: File): Promise<SourcePreviewResponse> {
  const form = new FormData();
  form.append("file", file);
  const res = await fetch(`${API_URL}/api/preview/source`, { method: "POST", body: form });
  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.detail || "Erro ao enviar arquivo de origem");
  }
  return res.json();
}

export async function previewTemplate(file: File): Promise<TemplatePreviewResponse> {
  const form = new FormData();
  form.append("file", file);
  const res = await fetch(`${API_URL}/api/preview/template`, { method: "POST", body: form });
  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.detail || "Erro ao enviar template");
  }
  return res.json();
}

export async function generateReport(
  source: File,
  template: File,
  config: GenerateConfig,
): Promise<Blob> {
  const form = new FormData();
  form.append("source", source);
  form.append("template", template);
  form.append("config", JSON.stringify(config));

  const res = await fetch(`${API_URL}/api/generate`, { method: "POST", body: form });
  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.detail || "Erro ao gerar relatorio");
  }
  return res.blob();
}
```

- [ ] **Step 3: Fix Header version text**

Edit `frontend/src/components/Header.tsx`: change `"Versão Desktop v2.4"` to `"Versão v2.0"`.

- [ ] **Step 4: Verify build**

```bash
npm run build --prefix frontend
```

- [ ] **Step 5: Commit**

```bash
git add frontend/src/services/api.ts frontend/src/types.ts frontend/src/components/Header.tsx
git commit -m "feat: add API service layer, update types, fix header version to v2.0"
```

---

### Task 12: Add ContractFields Component

**Files:**
- Create: `frontend/src/components/ContractFields.tsx`
- Modify: `frontend/src/App.tsx`

- [ ] **Step 1: Write ContractFields.tsx**

Write `frontend/src/components/ContractFields.tsx`:

```tsx
import React from "react";

interface ContractFieldsProps {
  startDate: string;
  prazo: number;
  mes: number;
  ano: number;
  onChange: (field: string, value: string | number) => void;
}

export function ContractFields({ startDate, prazo, mes, ano, onChange }: ContractFieldsProps) {
  return (
    <div className="mb-4 p-4 bg-slate-50 border border-slate-200 rounded-lg">
      <h4 className="text-label mb-3">Periodo do Contrato</h4>
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        <div>
          <label className="text-[10px] font-medium text-slate-500 block mb-1">Data Inicio</label>
          <input
            type="date"
            className="w-full bg-white border border-slate-300 rounded px-2 py-1.5 text-xs focus:ring-1 focus:ring-[var(--color-primary)] outline-none"
            value={startDate}
            onChange={(e) => onChange("startDate", e.target.value)}
          />
        </div>
        <div>
          <label className="text-[10px] font-medium text-slate-500 block mb-1">Prazo (dias)</label>
          <input
            type="number"
            className="w-full bg-white border border-slate-300 rounded px-2 py-1.5 text-xs focus:ring-1 focus:ring-[var(--color-primary)] outline-none"
            value={prazo}
            min={1}
            onChange={(e) => onChange("prazo", parseInt(e.target.value) || 0)}
          />
        </div>
        <div>
          <label className="text-[10px] font-medium text-slate-500 block mb-1">Mes</label>
          <input
            type="number"
            className="w-full bg-white border border-slate-300 rounded px-2 py-1.5 text-xs focus:ring-1 focus:ring-[var(--color-primary)] outline-none"
            value={mes}
            min={1}
            max={12}
            onChange={(e) => onChange("mes", parseInt(e.target.value) || 1)}
          />
        </div>
        <div>
          <label className="text-[10px] font-medium text-slate-500 block mb-1">Ano</label>
          <input
            type="number"
            className="w-full bg-white border border-slate-300 rounded px-2 py-1.5 text-xs focus:ring-1 focus:ring-[var(--color-primary)] outline-none"
            value={ano}
            min={2020}
            max={2100}
            onChange={(e) => onChange("ano", parseInt(e.target.value) || 2026)}
          />
        </div>
      </div>
    </div>
  );
}
```

- [ ] **Step 2: Integrate into App.tsx**

In `frontend/src/App.tsx`:

Add import:

```tsx
import { ContractFields } from './components/ContractFields';
```

Add state after existing `useState` lines near line 54:

```tsx
const [contractStart, setContractStart] = useState<string>("2026-01-01");
const [contractPrazo, setContractPrazo] = useState<number>(30);
const [contractMes, setContractMes] = useState<number>(1);
const [contractAno, setContractAno] = useState<number>(2026);
```

Add `ContractFields` inside Section 1, right before `FileUpload` (after line 91, before FileUpload):

```tsx
<ContractFields
  startDate={contractStart}
  prazo={contractPrazo}
  mes={contractMes}
  ano={contractAno}
  onChange={(field, value) => {
    if (field === "startDate") setContractStart(value as string);
    else if (field === "prazo") setContractPrazo(value as number);
    else if (field === "mes") setContractMes(value as number);
    else if (field === "ano") setContractAno(value as number);
  }}
/>
```

Fix footer status text: change from `"Sistema Operacional - Pronto para gerar"` to `"Pronto para gerar"` and `"Sistema Operacional - Aguardando configuracao"` to `"Aguardando configuracao"`.

- [ ] **Step 3: Verify build**

```bash
npm run build --prefix frontend
```

- [ ] **Step 4: Commit**

```bash
git add frontend/src/components/ContractFields.tsx frontend/src/App.tsx
git commit -m "feat: add ContractFields component with date/prazo/mes/ano, fix footer text"
```

---

### Task 13: Wire DataPreview to Real API

**Files:**
- Modify: `frontend/src/App.tsx`

- [ ] **Step 1: Update App.tsx to use real preview API**

Replace the `FileUpload` onFileSelect handler in Section 1 and the subsequent DataPreview render. Replace the MOCK_SHEETS logic with real API calls.

Key changes to `frontend/src/App.tsx`:

Remove `MOCK_SHEETS` constant (lines 11-41).

Add import:
```tsx
import { previewSource, previewTemplate, generateReport } from './services/api';
import type { GenerateConfig } from './types';
```

Replace the source file upload handler (line 59 inside FileUpload onFileSelect):

```tsx
onFileSelect={(name) => {
  setDataSourceFile(name || null);
  if (!name) {
    setAppState(prev => ({ ...prev, dataUploadDone: false }));
  }
}}
```

becomes:

```tsx
onFileSelect={async (name, file) => {
  if (!name || !file) {
    setDataSourceFile(null);
    setAppState(prev => ({ ...prev, dataUploadDone: false, sheets: [] }));
    return;
  }
  setDataSourceFile(name);
  try {
    const result = await previewSource(file);
    const sheets = result.sheets.map(s => ({
      name: s.name,
      selected: true,
      columns: s.columns,
      selectedColumns: [...s.columns],
      data: s.data,
    }));
    setAppState(prev => ({ ...prev, sheets }));
  } catch (err) {
    alert((err as Error).message);
    setDataSourceFile(null);
  }
}}
```

The template file upload (Section 2, line 128) similarly calls `previewTemplate` instead of just setting the name.

Note: FileUpload needs its `onFileSelect` to also pass the `File` object (not just the name). Update `FileUpload` prop:

```tsx
interface FileUploadProps {
  label: string;
  onFileSelect: (fileName: string | null, file?: File | null) => void;
  selectedFileName?: string | null;
}
```

Update the `handleFile` function in FileUpload.tsx to call `onFileSelect(file.name, file)` instead of just `onFileSelect(file.name)`.

Also update the template upload section similarly.

- [ ] **Step 2: Verify build**

```bash
npm run build --prefix frontend
```

- [ ] **Step 3: Commit**

```bash
git add frontend/src/App.tsx frontend/src/components/FileUpload.tsx
git commit -m "feat: wire DataPreview and TemplatePreview to real backend API"
```

---

### Task 14: Wire Generate to Real API and Download

**Files:**
- Modify: `frontend/src/App.tsx`

- [ ] **Step 1: Update handleGenerate to call real API**

Replace the `handleGenerate` function in App.tsx with:

```tsx
const handleGenerate = async () => {
  if (!sourceFileRef.current || !templateFileRef.current) {
    alert("Arquivos nao carregados. Recarregue a pagina.");
    return;
  }
  setIsGenerating(true);
  try {
    const config: GenerateConfig = {
      contract: {
        start_date: contractStart,
        prazo_dias: contractPrazo,
        mes: contractMes,
        ano: contractAno,
      },
      mappings: appState.mappings.map(m => ({
        formatTemplate: m.formatTemplate,
        templateCell: m.templateCell,
        sourceColumns: m.sourceColumns,
      })),
      listSeparator: ", ",
      listConnector: " e ",
    };

    const blob = await generateReport(sourceFileRef.current, templateFileRef.current, config);
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `Diario_Consolidado_${String(contractMes).padStart(2, "0")}_${contractAno}.xlsx`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  } catch (err) {
    alert((err as Error).message);
  } finally {
    setIsGenerating(false);
  }
};
```

Add useRef imports and refs at the top of the App component:

```tsx
import React, { useState, useRef } from 'react';

const sourceFileRef = useRef<File | null>(null);
const templateFileRef = useRef<File | null>(null);
```

Update onFileSelect for source to also set the ref:

```tsx
sourceFileRef.current = file;
```

Same for template:

```tsx
templateFileRef.current = file;
```

- [ ] **Step 2: Verify build**

```bash
npm run build --prefix frontend
```

- [ ] **Step 3: Commit**

```bash
git add frontend/src/App.tsx
git commit -m "feat: wire generate button to real API with file download"
```

---

### Task 15: Add List Separator and Connector Fields

**Files:**
- Modify: `frontend/src/components/MappingSection.tsx`
- Modify: `frontend/src/App.tsx`

- [ ] **Step 1: Add inputs to MappingSection**

In MappingSection, add below the format textarea's preview section (after the `generatePreview` div, around line 138-139):

```tsx
<div className="mt-3 grid grid-cols-2 gap-3">
  <div>
    <label className="text-[10px] font-medium text-slate-500 block mb-1">Separador de lista</label>
    <input
      type="text"
      className="w-full bg-white border border-slate-300 rounded px-2 py-1.5 text-xs focus:ring-1 focus:ring-[var(--color-primary)] outline-none"
      value={listSeparator}
      onChange={(e) => setListSeparator(e.target.value)}
    />
  </div>
  <div>
    <label className="text-[10px] font-medium text-slate-500 block mb-1">Conector final</label>
    <input
      type="text"
      className="w-full bg-white border border-slate-300 rounded px-2 py-1.5 text-xs focus:ring-1 focus:ring-[var(--color-primary)] outline-none"
      value={listConnector}
      onChange={(e) => setListConnector(e.target.value)}
    />
  </div>
</div>
```

Add interface props:

```tsx
interface MappingSectionProps {
  mappings: MappingData[];
  onMappingsChange: (mappings: MappingData[]) => void;
  availableColumns: string[];
  listSeparator: string;
  onListSeparatorChange: (val: string) => void;
  listConnector: string;
  onListConnectorChange: (val: string) => void;
}
```

Add state inside the component:

```tsx
const [listSeparator, setListSeparator] = useState<string>(", ");
const [listConnector, setListConnector] = useState<string>(" e ");
```

Use the props instead of local state — pass them through:

Actually, the simpler approach: use props values with callbacks. But for the prototype, we can keep it as internal state and lift it up later. Let me keep it simple:

```tsx
// Inside MappingSection, use the provided props
```

No, let me just keep local state in App.tsx and pass down. Update App.tsx to add:

```tsx
const [listSeparator, setListSeparator] = useState<string>(", ");
const [listConnector, setListConnector] = useState<string>(" e ");
```

Pass to MappingSection:
```tsx
<MappingSection
  mappings={appState.mappings}
  availableColumns={availableColumns}
  onMappingsChange={(mappings) => setAppState(prev => ({ ...prev, mappings }))}
  listSeparator={listSeparator}
  onListSeparatorChange={setListSeparator}
  listConnector={listConnector}
  onListConnectorChange={setListConnector}
/>
```

Use in generate config:
```tsx
listSeparator,
listConnector,
```

- [ ] **Step 2: Verify build**

```bash
npm run build --prefix frontend
```

- [ ] **Step 3: Commit**

```bash
git add frontend/src/components/MappingSection.tsx frontend/src/App.tsx
git commit -m "feat: add list separator and connector fields to mapping section"
```

---

### Task 16: CI/CD for Backend (Cloud Run)

**Files:**
- Create: `.github/workflows/deploy-backend.yml`

- [ ] **Step 1: Write deploy-backend.yml**

```yaml
name: Deploy Backend

on:
  push:
    branches: [master]
    paths:
      - 'backend/**'

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: google-github-actions/auth@v2
        with:
          credentials_json: ${{ secrets.GCP_SA_KEY }}

      - uses: google-github-actions/setup-gcloud@v2

      - name: Build and push
        run: |
          gcloud builds submit backend/ \
            --tag gcr.io/${{ secrets.GCP_PROJECT_ID }}/rdo-automator:${{ github.sha }}

      - name: Deploy to Cloud Run
        run: |
          gcloud run deploy rdo-automator \
            --image gcr.io/${{ secrets.GCP_PROJECT_ID }}/rdo-automator:${{ github.sha }} \
            --platform managed \
            --region us-central1 \
            --memory 512Mi \
            --timeout 3600 \
            --max-instances 1 \
            --min-instances 0 \
            --allow-unauthenticated
```

- [ ] **Step 2: Write deploy-frontend.yml**

Create `.github/workflows/deploy-frontend.yml`:

```yaml
name: Deploy Frontend

on:
  push:
    branches: [master]
    paths:
      - 'frontend/**'

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: amondnet/vercel-action@v25
        with:
          vercel-token: ${{ secrets.VERCEL_TOKEN }}
          vercel-org-id: ${{ secrets.VERCEL_ORG_ID }}
          vercel-project-id: ${{ secrets.VERCEL_PROJECT_ID }}
          vercel-args: '--prod'
          working-directory: ./frontend
```

- [ ] **Step 3: Commit**

```bash
git add .github/workflows/
git commit -m "ci: add deploy workflows for backend (Cloud Run) and frontend (Vercel)"
```

---

### Task 17: Full Integration Test

**Files:**
- Create: `tests/integration/test_e2e.py`

- [ ] **Step 1: Write end-to-end test**

Write `tests/integration/test_e2e.py`:

```python
import io
import json
import pandas as pd
from openpyxl import Workbook
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def test_full_flow():
    source_buffer = io.BytesIO()
    with pd.ExcelWriter(source_buffer, engine="openpyxl") as writer:
        df1 = pd.DataFrame({
            "Data": ["2026-01-05", "2026-01-10", "2026-01-15", "2026-01-20"],
            "Atividade": ["Pintura", "Concretagem", "Escavacao", "Armação"],
            "Bairro": ["Centro", "Vista Alegre", "Centro", "Leste"],
        })
        df1.to_excel(writer, sheet_name="Relatorio_Geral", index=False)
    source_buffer.seek(0)

    template_buffer = io.BytesIO()
    wb = Workbook()
    ws = wb.active
    ws["A1"] = "RDO - RELATORIO DIARIO DE OBRA"
    ws["B3"] = ""
    ws["B5"] = ""
    wb.save(template_buffer)
    template_buffer.seek(0)

    config = {
        "contract": {"start_date": "2026-01-01", "prazo_dias": 180, "mes": 1, "ano": 2026},
        "mappings": [
            {
                "formatTemplate": "Servicos Realizados: {Atividade}. No Bairro: {Bairro}",
                "templateCell": "B3",
                "sourceColumns": ["Atividade", "Bairro"],
            }
        ],
        "listSeparator": ", ",
        "listConnector": " e ",
    }

    response = client.post(
        "/api/generate",
        files={
            "source": ("medicao.xlsx", source_buffer.getvalue(), "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"),
            "template": ("template.xlsx", template_buffer.getvalue(), "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"),
        },
        data={"config": json.dumps(config)},
    )

    assert response.status_code == 200
    assert "spreadsheetml" in response.headers["content-type"]

    output = io.BytesIO(response.content)
    from openpyxl import load_workbook
    wb_out = load_workbook(output)
    assert "05-01" in wb_out.sheetnames
    ws_out = wb_out["05-01"]
    cell_val = ws_out["B3"].value
    assert cell_val is not None
    assert "Servicos Realizados:" in str(cell_val)
    assert "Pintura" in str(cell_val)
    assert "Centro" in str(cell_val)
```

- [ ] **Step 2: Run e2e test**

```bash
cd backend && uv run pytest ../tests/integration/test_e2e.py -v
```

Expected: 1 PASS

- [ ] **Step 3: Run all tests**

```bash
cd backend && uv run pytest ../tests/ -v
```

- [ ] **Step 4: Commit**

```bash
git add tests/integration/test_e2e.py
git commit -m "test: add end-to-end integration test for full generate flow"
```

---

### Task 18: Verify & Finalize

- [ ] **Step 1: Run full backend test suite**

```bash
cd backend && uv run pytest ../tests/ -v --tb=short
```

Expected: All tests pass.

- [ ] **Step 2: Verify backend runs locally**

```bash
cd backend && uv run uvicorn main:app --host 0.0.0.0 --port 8000 &
sleep 2
curl -s http://localhost:8000/docs | head -c 100
kill %1
```

Expected: OpenAPI docs HTML.

- [ ] **Step 3: Verify frontend builds**

```bash
npm run build --prefix frontend
```

Expected: Build success, output in `frontend/dist/`.

- [ ] **Step 4: Final commit**

```bash
git add -A
git commit -m "chore: finalize web migration — backend + frontend + deploy configs"
```

# Template Preview Styling — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Render template preview with original Excel formatting (background colors, font colors, borders, alignment, merged cells, column widths, row heights, images).

**Architecture:** Extract style properties from openpyxl cells into a CSS-inline `style` dict on `CellData`, apply via React `style={{...}}` on `<td>`. Read merged cells, column widths, and row heights from openpyxl and serialize into `TemplateSheet`.

**Tech Stack:** Python (openpyxl, pydantic), TypeScript (React, Tailwind)

---

## File Structure

| File | Responsibility |
|---|---|
| `backend/src/schemas.py` | Pydantic models — add `style`, `colWidths`, `rowHeights` fields |
| `backend/src/excel/template.py` | Style extraction (`_cell_style`), merged cells, dimensions |
| `frontend/src/types.ts` | TypeScript types — mirror new fields |
| `frontend/src/components/templatepreview/TemplatePreviewGrid.tsx` | Apply styles, merged cells, column/row dimensions, render images |
| `backend/tests/unit/test_preview_service.py` | Add test for style extraction in preview |

---

### Task 1: Backend schema — add new fields

**Files:**
- Modify: `backend/src/schemas.py:24-48`

- [ ] **Step 1: Add `style` to `CellData`, `colWidths` and `rowHeights` to `TemplateSheet`**

```python
class CellData(BaseModel):
    coord: str
    row: int
    col: int
    value: str | None = None
    font: dict[str, int | bool | None] | None = None
    style: dict[str, str] | None = None


class TemplateSheet(BaseModel):
    name: str
    cells: list[CellData]
    images: list[ImageData]
    merged: list[dict] = []
    col_widths: dict[str, float] | None = None
    row_heights: dict[int, float] | None = None
```

- [ ] **Step 2: Run backend type check**

```bash
uv run pyright src/schemas.py
```
Expected: PASS (0 errors)

- [ ] **Step 3: Commit**

```bash
git add backend/src/schemas.py
git commit -m "feat: add style, colWidths, rowHeights fields to template schema"
```

---

### Task 2: Backend — write failing test for style extraction

**Files:**
- Modify: `backend/tests/unit/test_preview_service.py:32-65`

- [ ] **Step 1: Add helper to create a styled template xlsx**

```python
def _create_styled_template_xlsx() -> bytes:
    from openpyxl.styles import Font, PatternFill, Alignment, Border, Side

    wb = Workbook()
    ws = wb.active
    ws["A1"] = "Header"
    ws["A1"].font = Font(bold=True, size=14, color="FF0000", name="Arial")
    ws["A1"].fill = PatternFill(start_color="FFFF00", end_color="FFFF00", fill_type="solid")
    ws["A1"].alignment = Alignment(horizontal="center", vertical="center")
    ws["A1"].border = Border(
        left=Side(style="thin", color="000000"),
        right=Side(style="thin", color="000000"),
        top=Side(style="thin", color="000000"),
        bottom=Side(style="thin", color="000000"),
    )
    ws.merge_cells("A1:C1")
    ws.column_dimensions["A"].width = 15
    ws.row_dimensions[1].height = 30
    buffer = io.BytesIO()
    wb.save(buffer)
    buffer.seek(0)
    return buffer.read()
```

- [ ] **Step 2: Add test for style extraction**

```python
def test_preview_template_styles():
    data = _create_styled_template_xlsx()
    result = preview_template(data, "template.xlsx")
    sheet = result.sheets[0]

    header_cell = next(c for c in sheet.cells if c.value == "Header")

    assert header_cell.style is not None
    assert header_cell.style.get("font-weight") == "bold"
    assert header_cell.style.get("font-size") == "14pt"
    assert header_cell.style.get("color") == "#FF0000"
    assert header_cell.style.get("font-family") == "Arial"
    assert header_cell.style.get("background-color") == "#FFFF00"
    assert header_cell.style.get("text-align") == "center"
    assert header_cell.style.get("vertical-align") == "center"
    assert "border" in header_cell.style.get("border-right", "")
```

- [ ] **Step 3: Add test for merged cells**

```python
def test_preview_template_merged_cells():
    data = _create_styled_template_xlsx()
    result = preview_template(data, "template.xlsx")
    sheet = result.sheets[0]

    assert len(sheet.merged) == 1
    m = sheet.merged[0]
    assert m["min_col"] == 1
    assert m["max_col"] == 3
    assert m["min_row"] == 1
    assert m["max_row"] == 1
```

- [ ] **Step 4: Add test for column widths and row heights**

```python
def test_preview_template_dimensions():
    data = _create_styled_template_xlsx()
    result = preview_template(data, "template.xlsx")
    sheet = result.sheets[0]

    assert sheet.col_widths is not None
    assert sheet.col_widths.get("A") == 15
    assert sheet.row_heights is not None
    assert sheet.row_heights.get(1) == 30
```

- [ ] **Step 5: Add test for theme/auto color (fallback to None — no crash)**

```python
def test_preview_template_auto_colors():
    from openpyxl.styles import PatternFill, Font

    wb = Workbook()
    ws = wb.active
    ws["A1"] = "Auto"
    ws["A1"].fill = PatternFill(fill_type=None)  # no fill
    ws["A1"].font = Font(color=None)  # auto color
    buffer = io.BytesIO()
    wb.save(buffer)
    buffer.seek(0)

    result = preview_template(buffer.read(), "auto.xlsx")
    cell = next(c for c in result.sheets[0].cells if c.value == "Auto")
    assert cell.style is not None
    assert "background-color" not in cell.style
    assert "color" not in cell.style
```

- [ ] **Step 6: Run tests to verify they fail**

```bash
uv run pytest tests/unit/test_preview_service.py::test_preview_template_styles tests/unit/test_preview_service.py::test_preview_template_merged_cells tests/unit/test_preview_service.py::test_preview_template_dimensions tests/unit/test_preview_service.py::test_preview_template_auto_colors -v
```
Expected: all 4 FAIL (style extraction not implemented)

- [ ] **Step 7: Commit**

```bash
git add backend/tests/unit/test_preview_service.py
git commit -m "test: add failing tests for template style extraction"
```

---

### Task 3: Backend — implement style extraction in template.py

**Files:**
- Modify: `backend/src/excel/template.py:86-130`

- [ ] **Step 1: Add `_cell_style` helper function after `_read_image_data`**

```python
_BORDER_STYLE_MAP = {
    "thin": "1px solid",
    "hair": "1px solid",
    "medium": "2px solid",
    "thick": "3px solid",
    "double": "3px double",
    "dashed": "1px dashed",
    "dotted": "1px dotted",
}


def _cell_style(cell) -> dict[str, str]:
    style: dict[str, str] = {}

    try:
        fill = cell.fill
        if fill and fill.patternType and fill.fgColor:
            rgb = fill.fgColor.rgb
            if rgb and rgb not in ("00000000", "0"):
                style["background-color"] = f"#{rgb[-6:]}"
    except Exception:
        pass

    try:
        font = cell.font
        if font:
            if font.bold:
                style["font-weight"] = "bold"
            if font.italic:
                style["font-style"] = "italic"
            if font.underline and font.underline != "none":
                style["text-decoration"] = "underline"
            if font.size:
                style["font-size"] = f"{font.size}pt"
            if font.name:
                style["font-family"] = font.name
            if font.color and font.color.rgb:
                rgb = font.color.rgb
                if rgb and rgb not in ("00000000", "0"):
                    style["color"] = f"#{rgb[-6:]}"
    except Exception:
        pass

    try:
        align = cell.alignment
        if align:
            if align.horizontal:
                style["text-align"] = align.horizontal
            if align.vertical:
                style["vertical-align"] = align.vertical
            if align.wrapText:
                style["white-space"] = "pre-wrap"
    except Exception:
        pass

    try:
        border = cell.border
        if border:
            for side_name, css_prop in [
                ("left", "border-left"),
                ("right", "border-right"),
                ("top", "border-top"),
                ("bottom", "border-bottom"),
            ]:
                side = getattr(border, side_name, None)
                if side and side.style:
                    base = _BORDER_STYLE_MAP.get(side.style)
                    if base:
                        color = "#000000"
                        try:
                            if side.color and side.color.rgb:
                                rgb = side.color.rgb
                                if rgb and rgb not in ("00000000", "0"):
                                    color = f"#{rgb[-6:]}"
                        except Exception:
                            pass
                        style[css_prop] = f"{base} {color}"
    except Exception:
        pass

    return style
```

- [ ] **Step 2: Update `preview_template` to use `_cell_style`, populate merged/colWidths/rowHeights**

Replace the cell loop (lines 96-109) and sheet append (line 127):

```python
        cells = []
        for row in ws.iter_rows():
            for cell in row:
                font_info = None
                if cell.font:
                    font_info = {"bold": cell.font.bold, "size": cell.font.size}
                cells.append(
                    CellData(
                        coord=cell.coordinate or "",
                        row=cell.row or 0,
                        col=cell.column or 0,
                        value=str(cell.value) if cell.value is not None else None,
                        font=font_info,
                        style=_cell_style(cell) or None,
                    )
                )

        merged = []
        for r in ws.merged_cells.ranges:
            merged.append({
                "min_col": r.min_col,
                "max_col": r.max_col,
                "min_row": r.min_row,
                "max_row": r.max_row,
            })

        col_widths = {}
        for col_letter, dim in ws.column_dimensions.items():
            if dim.width:
                col_widths[col_letter] = dim.width

        row_heights = {}
        for row_num, dim in ws.row_dimensions.items():
            if dim.height:
                row_heights[row_num] = dim.height
```

And replace the sheet append:

```python
        all_sheets.append(TemplateSheet(
            name=ws.title,
            cells=cells,
            images=images,
            merged=merged,
            col_widths=col_widths or None,
            row_heights=row_heights or None,
        ))
```

- [ ] **Step 3: Run tests to verify they pass**

```bash
uv run pytest tests/unit/test_preview_service.py -v
```
Expected: all tests PASS

- [ ] **Step 4: Run all backend tests to ensure no regressions**

```bash
uv run pytest tests/ -v
```
Expected: all tests PASS

- [ ] **Step 5: Run backend type check**

```bash
uv run pyright src/excel/template.py
```
Expected: PASS (0 errors)

- [ ] **Step 6: Commit**

```bash
git add backend/src/excel/template.py
git commit -m "feat: extract cell styles, merged cells, column/row dimensions from template"
```

---

### Task 4: Frontend — update types

**Files:**
- Modify: `frontend/src/types.ts:30-48`

- [ ] **Step 1: Add `style`, `colWidths`, `rowHeights` to TypeScript types**

```typescript
export type CellData = {
  coord: string;
  row: number;
  col: number;
  value: string | null;
  font: { bold: boolean | null; size: number | null } | null;
  style: Record<string, string> | null;
};

export type ImageData = {
  b64: string;
  position: Record<string, number>;
};

export type TemplateSheet = {
  name: string;
  cells: CellData[];
  images: ImageData[];
  merged: Record<string, unknown>[];
  colWidths: Record<string, number> | null;
  rowHeights: Record<number, number> | null;
};
```

- [ ] **Step 2: Run frontend type check**

```bash
cd frontend && npm run lint
```
May show errors in TemplatePreviewGrid — that's expected for next task.

- [ ] **Step 3: Commit**

```bash
git add frontend/src/types.ts
git commit -m "feat: add style, colWidths, rowHeights to frontend types"
```

---

### Task 5: Frontend — apply styles in TemplatePreviewGrid

**Files:**
- Modify: `frontend/src/components/templatepreview/TemplatePreviewGrid.tsx:57-159`

- [ ] **Step 1: Add colgroup with column widths**

After `interactive` const (line 83), add before the return:

```tsx
  const colWidths = activeSheet.colWidths ?? {};
  const rowHeights = activeSheet.rowHeights ?? {};
```

Replace the `<table>` opening tag and add `<colgroup>` before `<thead>`:

```tsx
      <table
        className="w-full border-collapse text-xs select-none"
        style={{ borderCollapse: "collapse" }}
      >
        <colgroup>
          <col style={{ width: "32px" }} />
          {cols.map((col) => (
            <col
              key={col}
              style={{
                width: colWidths[col] ? `${colWidths[col] * 7}px` : "auto",
              }}
            />
          ))}
        </colgroup>
```

- [ ] **Step 2: Apply row heights on `<tr>`**

```tsx
            <tr
              key={row}
              style={{
                height: rowHeights[row] ? `${rowHeights[row] * 1.35}px` : undefined,
              }}
            >
```

- [ ] **Step 3: Apply merged cells as colspan/rowspan**

Update the cell rendering block. Replace the `<td>` with:

```tsx
                let colSpan = 1;
                let rowSpan = 1;
                let skip = false;

                if (activeSheet.merged.length > 0) {
                  const merged = activeSheet.merged as Array<{
                    min_col: number;
                    max_col: number;
                    min_row: number;
                    max_row: number;
                  }>;
                  const colNum = colToInt(col);
                  for (const m of merged) {
                    if (
                      colNum >= m.min_col &&
                      colNum <= m.max_col &&
                      row >= m.min_row &&
                      row <= m.max_row
                    ) {
                      if (m.min_col === colNum && m.min_row === row) {
                        colSpan = m.max_col - m.min_col + 1;
                        rowSpan = m.max_row - m.min_row + 1;
                      } else {
                        skip = true;
                      }
                      break;
                    }
                  }
                }

                if (skip) return null;
```

Replace the `isMergedCell(...)` check on line 113 with `if (skip) return null;` (already handled above).

- [ ] **Step 4: Apply cell inline style**

Add `style={cellData?.style ?? undefined}` and `colSpan`/`rowSpan` to `<td>`:

```tsx
                  <td
                    key={cellRef}
                    colSpan={colSpan > 1 ? colSpan : undefined}
                    rowSpan={rowSpan > 1 ? rowSpan : undefined}
                    style={cellData?.style ?? undefined}
                    className={`border border-slate-200 p-2 h-8 relative
                      ${hasValue ? 'font-medium text-slate-700' : ''}
                      ${!hasValue && interactive ? 'cursor-pointer hover:bg-indigo-50' : ''}
                      ${isSelected ? 'ring-2 ring-inset ring-[var(--color-primary)] bg-indigo-50' : ''}
                      ${mapping ? 'bg-indigo-50/70' : ''}
                      transition-all duration-150`}
                    onClick={() => {
                      if (interactive && onCellClick && !hasValue) {
                        onCellClick(cellRef);
                      }
                    }}
                  >
```

Note: removed `isBold ? 'font-bold' : ''` from className since `style` handles font-weight.

- [ ] **Step 5: Render images as absolutely positioned**

After the `</table>` closing tag and before the `</div>`:

```tsx
        {activeSheet.images && activeSheet.images.length > 0 && (
          activeSheet.images.map((img, idx) => {
            if (!img.position || img.position.col === undefined || img.position.row === undefined) {
              return null;
            }
            const leftCols = Array.from({ length: img.position.col }, (_, i) => intToCol(i + 1));
            let leftPx = 32;
            for (const lc of leftCols) {
              leftPx += (colWidths[lc] ?? 8.5) * 7;
            }
            let topPx = 0;
            for (let r = 1; r <= img.position.row; r++) {
              topPx += (rowHeights[r] ?? 15) * 1.35;
            }
            return (
              <img
                key={idx}
                src={img.b64}
                alt=""
                style={{
                  position: "absolute",
                  left: `${leftPx}px`,
                  top: `${topPx}px`,
                  maxWidth: "200px",
                  pointerEvents: "none",
                }}
              />
            );
          })
        )}
```

- [ ] **Step 6: Run frontend type check**

```bash
cd frontend && npm run lint
```
Expected: PASS (0 errors)

- [ ] **Step 7: Commit**

```bash
git add frontend/src/components/templatepreview/TemplatePreviewGrid.tsx
git commit -m "feat: apply inline styles, merged cells, column/row dimensions, images to template preview grid"
```

---

### Task 6: Final verification

- [ ] **Step 1: Run all backend tests**

```bash
uv run pytest tests/ -v
```
Expected: all tests PASS

- [ ] **Step 2: Run backend type check**

```bash
uv run pyright src/
```
Expected: PASS (0 errors)

- [ ] **Step 3: Run frontend type check**

```bash
cd frontend && npm run lint
```
Expected: PASS (0 errors)

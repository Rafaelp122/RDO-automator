# Template Preview Styling — Design Spec

**Date:** 2026-06-02
**Status:** Approved

## Goal

Render the template preview with Excel-original formatting (background colors, font colors, borders, alignment, merged cells, column widths, row heights, images) instead of plain-text only.

## Approach

CSS inline — extract style properties from openpyxl, serialize as CSS inline `style` dicts in `CellData`, apply via React `style={{...}}` on `<td>` elements.

## Schema Changes

### `CellData` (backend + frontend)

New field:

| Field | Type | Description |
|---|---|---|
| `style` | `dict[str,str] \| None` | CSS inline properties for the cell (`background-color`, `color`, `font-weight`, `text-align`, `border-right`, etc.) |

`font` field remains unchanged for backward compatibility; `style` supersedes it visually.

### `TemplateSheet` (backend + frontend)

New fields:

| Field | Type | Description |
|---|---|---|
| `colWidths` | `dict[str, float] \| None` | Column letter → width (Excel units) |
| `rowHeights` | `dict[int, float] \| None` | Row number → height (Excel points) |
| `merged` | `list[dict]` | Now populated from `ws.merged_cells.ranges` (previously hardcoded `[]`) |

## Backend: `template.py`

### `_cell_style(cell) -> dict[str, str]`

Maps openpyxl cell properties to CSS inline:

| openpyxl property | CSS property | Notes |
|---|---|---|
| `cell.fill.fgColor.rgb` | `background-color` | Skip if `None` or `"00000000"` (auto/theme) |
| `cell.font.color.rgb` | `color` | Skip if `None` |
| `cell.font.name` | `font-family` | |
| `cell.font.size` | `font-size` | Append `"pt"` |
| `cell.font.bold` | `font-weight: bold` | Only if truthy |
| `cell.font.italic` | `font-style: italic` | Only if truthy |
| `cell.font.underline` | `text-decoration: underline` | Only if not `"none"` |
| `cell.alignment.horizontal` | `text-align` | |
| `cell.alignment.vertical` | `vertical-align` | |
| `cell.border.left.style` | `border-left` | Convert style name → px width + color |
| `cell.border.right.style` | `border-right` | Same |
| `cell.border.top.style` | `border-top` | Same |
| `cell.border.bottom.style` | `border-bottom` | Same |

All `getattr` failures silently skip the property — defensive by design.

### Border width mapping

| Excel style | CSS |
|---|---|
| `"thin"`, `"hair"` | `1px solid` |
| `"medium"` | `2px solid` |
| `"thick"` | `3px solid` |
| `"double"` | `3px double` |
| `"dashed"` | `1px dashed` |
| `"dotted"` | `1px dotted` |
| Other / None | skipped |

### Merged cells

Iterate `ws.merged_cells.ranges`, serialize each as:
```python
{"min_col": r.min_col, "max_col": r.max_col, "min_row": r.min_row, "max_row": r.max_row}
```

### Column widths and row heights

- `col_widths`: iterate `ws.column_dimensions`, key = column letter from `col_idx`
- `row_heights`: iterate `ws.row_dimensions`, key = row number

### Images

Current extraction logic unchanged. Images now rendered in frontend.

## Frontend Changes

### `types.ts`

Mirror new backend fields as described in Schema Changes.

### `TemplatePreviewGrid.tsx`

**Table structure:**
- `<colgroup>` with `<col>` per column, width = `colWidths[col] * 7 + "px"` (approx char width)
- `<tr>` with `style={{ height: rowHeights[row] * 1.35 + "px" }}`
- `<td style={cellData.style}>` applies CSS inline directly

**Merged cells:**
- First cell of a merged range gets `colSpan={max_col - min_col + 1}` and `rowSpan={max_row - min_row + 1}`
- Internal cells skipped (existing `isMergedCell` logic reused, now with real data)

**Images:**
- Container div with `position: relative`
- `<img>` with `position: absolute` at `top: anchor._from.row * rowHeight`, `left: anchor._from.col * colWidth`
- Fallback: skip image if anchor data is incomplete

**Interactivity preservation:**
- `className` keeps `cursor-pointer`, hover, selection ring
- Style inline takes precedence over Tailwind classes for visual properties only (bg, font, border)

**Border overlap mitigation:**
Apply all 4 borders per cell via inline `style`. Use `border-collapse: collapse` on `<table>`. CSS collapses adjacent borders automatically — sufficient for preview fidelity.

## Edge Cases

| Case | Handling |
|---|---|
| Theme/auto color returns `None` or `"00000000"` | Skip that CSS property |
| `cell.fill.patternType` is `None` | Skip `background-color` |
| Font size is `None` | Skip `font-size` |
| Anchor has no `_from` attr | Skip image rendering |
| Column has no explicit width | Skip that column in `colWidths` |
| Row has no explicit height | Skip that row in `rowHeights` |
| Source preview endpoint | Unchanged (pandas strips formatting, out of scope) |

## Files Modified

| File | Change |
|---|---|
| `backend/src/schemas.py` | `CellData.style`, `TemplateSheet.colWidths`, `TemplateSheet.rowHeights` |
| `backend/src/excel/template.py` | `_cell_style()`, merged cells extraction, column/row dimension extraction |
| `frontend/src/types.ts` | Mirror schema changes |
| `frontend/src/components/templatepreview/TemplatePreviewGrid.tsx` | Apply styles, dimensions, merged cells, images |

## Out of Scope

- Source file preview (pandas data, no formatting available)
- Number format rendering (values already stringified)
- Conditional formatting
- Charts, shapes beyond images

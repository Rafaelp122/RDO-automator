import type { TemplateSheet, MappingData } from '../../types';

interface TemplatePreviewGridProps {
  sheets: TemplateSheet[];
  onCellClick?: (cellRef: string) => void;
  mappedCells?: Record<string, MappingData>;
  selectedCell?: string | null;
}

function isMergedCell(coord: string, merged: TemplateSheet['merged']): boolean {
  if (!merged || merged.length === 0) return false;
  const match = /^([A-Z]+)(\d+)$/.exec(coord);
  if (!match) return false;
  const col = match[1];
  const row = parseInt(match[2], 10);
  for (const m of merged) {
    const mr = m as Record<string, unknown>;
    if (
      typeof mr.min_col === 'number' &&
      typeof mr.max_col === 'number' &&
      typeof mr.min_row === 'number' &&
      typeof mr.max_row === 'number'
    ) {
      const colNum = colToInt(col);
      if (
        colNum >= (mr.min_col as number) &&
        colNum <= (mr.max_col as number) &&
        row >= (mr.min_row as number) &&
        row <= (mr.max_row as number)
      ) {
        if (mr.min_col === colNum && mr.min_row === row) return false;
        return true;
      }
    }
  }
  return false;
}

function colToInt(col: string): number {
  let n = 0;
  for (let i = 0; i < col.length; i++) {
    n = n * 26 + (col.charCodeAt(i) - 64);
  }
  return n;
}

function intToCol(n: number): string {
  let s = '';
  while (n > 0) {
    n--;
    s = String.fromCharCode(65 + (n % 26)) + s;
    n = Math.floor(n / 26);
  }
  return s;
}

export function TemplatePreviewGrid({
  sheets,
  onCellClick,
  mappedCells = {},
  selectedCell = null,
}: TemplatePreviewGridProps) {
  const activeSheet = sheets[0];

  if (!activeSheet) {
    return (
      <div className="border border-dashed border-slate-300 rounded-lg p-8 text-center text-slate-400 text-sm">
        Carregue um template para visualizar
      </div>
    );
  }

  const maxRow = Math.max(...activeSheet.cells.map((c) => c.row), 8);
  const maxCol = Math.max(...activeSheet.cells.map((c) => c.col), 6);
  const rows = Array.from({ length: Math.min(maxRow, 50) }, (_, i) => i + 1);
  const cols = Array.from({ length: Math.min(maxCol, 26) }, (_, i) => intToCol(i + 1));

  const cellMap = new Map<string, (typeof activeSheet.cells)[0]>();
  for (const c of activeSheet.cells) {
    cellMap.set(c.coord, c);
  }

  const interactive = !!onCellClick;

  const colWidths = activeSheet.colWidths ?? {};
  const rowHeights = activeSheet.rowHeights ?? {};

  return (
    <div
      className={`overflow-x-auto border border-slate-200 rounded ${
        interactive ? 'bg-white shadow-sm' : ''
      } excel-grid relative`}
    >
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
        <thead>
          <tr>
            <th className="w-8 border border-slate-200 bg-slate-100 p-1"></th>
            {cols.map((col) => (
              <th
                key={col}
                className="border border-slate-200 bg-slate-100 font-normal p-1 px-4 text-center text-slate-500"
              >
                {col}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.map((row) => (
            <tr
              key={row}
              style={{
                height: rowHeights[row] ? `${rowHeights[row] * 1.35}px` : undefined,
              }}
            >
              <td className="border border-slate-200 bg-slate-100 text-center text-slate-500 p-1">
                {row}
              </td>
              {cols.map((col) => {
                const cellRef = `${col}${row}`;

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

                const cellData = cellMap.get(cellRef);
                const mapping = mappedCells[cellRef];
                const isSelected = selectedCell === cellRef;
                const hasValue = cellData?.value;

                return (
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
                    <div className="flex items-center justify-between w-full h-full relative z-10">
                      <span className="truncate max-w-[120px]">{cellData?.value ?? ''}</span>
                      {mapping && !hasValue && (
                        <div className="absolute inset-0 flex items-center justify-center p-1">
                          <div
                            className="bg-[var(--color-primary)] text-white text-[9px] px-1.5 py-0.5 rounded shadow-sm cursor-default flex items-center gap-1 w-full justify-center max-w-full overflow-hidden"
                            title={mapping.formatTemplate}
                          >
                            <span className="truncate max-w-[50px]">{mapping.formatTemplate}</span>
                          </div>
                        </div>
                      )}
                    </div>
                  </td>
                );
              })}
            </tr>
          ))}
        </tbody>
      </table>
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
                  zIndex: 10,
                }}
            />
          );
        })
      )}
    </div>
  );
}

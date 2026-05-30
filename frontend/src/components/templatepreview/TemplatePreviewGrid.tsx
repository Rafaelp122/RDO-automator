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

  return (
    <div
      className={`overflow-x-auto border border-slate-200 rounded ${
        interactive ? 'bg-white shadow-sm' : ''
      } excel-grid relative`}
    >
      <table className="w-full border-collapse text-xs select-none">
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
            <tr key={row}>
              <td className="border border-slate-200 bg-slate-100 text-center text-slate-500 p-1">
                {row}
              </td>
              {cols.map((col) => {
                const cellRef = `${col}${row}`;
                if (isMergedCell(cellRef, activeSheet.merged)) return null;

                const cellData = cellMap.get(cellRef);
                const mapping = mappedCells[cellRef];
                const isSelected = selectedCell === cellRef;
                const hasValue = cellData?.value;
                const isBold = cellData?.font?.bold;

                return (
                  <td
                    key={cellRef}
                    className={`border border-slate-200 p-2 h-8 relative
                      ${hasValue ? 'font-medium text-slate-700' : ''}
                      ${isBold ? 'font-bold' : ''}
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
    </div>
  );
}

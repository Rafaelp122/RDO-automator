import { useState, useMemo, use } from 'react';
import { DataSourceContext } from './DataSourceProvider';

export function DataPreview() {
  const {
    state: { sheets, headerRow },
    actions: { toggleSheet, toggleColumn, confirm, changeHeaderRow },
  } = use(DataSourceContext)!;

  const [activeTabName, setActiveTabName] = useState<string>(() => sheets[0]?.name ?? '');

  const activeSheet = useMemo(
    () => sheets.find((s) => s.name === activeTabName) ?? sheets[0],
    [sheets, activeTabName],
  );

  const selectedColumnsSet = useMemo(
    () => new Set(activeSheet?.selectedColumns ?? []),
    [activeSheet?.selectedColumns],
  );

  const selectedSheetsCount = sheets.filter((s) => s.selected).length;
  const totalSelectedColumns = sheets.reduce(
    (acc, s) => acc + (s.selected ? s.selectedColumns.length : 0),
    0,
  );

  if (!activeSheet) return null;

  return (
    <div className="mt-6 animate-in fade-in slide-in-from-bottom-2 duration-500">
      <div className="flex items-center justify-between mb-4">
        <div>
          <h3 className="font-semibold text-[var(--color-text-primary)]">Preview dos Dados</h3>
          <p className="text-[var(--color-text-secondary)] mt-1">Selecione as abas e colunas que deseja extrair</p>
        </div>
        <div className="bg-indigo-50 text-[var(--color-primary)] px-3 py-1.5 rounded-full text-xs font-bold flex items-center gap-2">
          <span>{selectedSheetsCount} {selectedSheetsCount === 1 ? 'aba selecionada' : 'abas selecionadas'}</span>
          <span className="w-1 h-1 bg-[var(--color-primary)] rounded-full"></span>
          <span>{totalSelectedColumns} colunas</span>
        </div>
      </div>

      <div className="flex items-center gap-2 mb-4">
        <label className="text-xs text-[var(--color-text-secondary)] font-medium">
          Linha do cabeçalho:
        </label>
        <select
          className="text-xs border border-slate-300 rounded px-2 py-1 bg-white text-[var(--color-text-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
          value={headerRow}
          onChange={(e) => changeHeaderRow(Number(e.target.value))}
        >
          {Array.from({ length: 11 }, (_, i) => (
            <option key={i} value={i}>
              {i + 1} {i === 0 ? '(padrão)' : ''}
            </option>
          ))}
        </select>
      </div>

      <div className="flex border-b border-[var(--color-card-border)] mb-4 overflow-x-auto">
        {sheets.map((sheet) => (
          <div
            key={sheet.name}
            className={`flex items-center gap-2 px-4 py-2 cursor-pointer border-b-2 transition-colors ${
              activeTabName === sheet.name
                ? 'border-[var(--color-primary)] bg-indigo-50/50'
                : 'border-transparent hover:bg-slate-50'
            }`}
            onClick={() => setActiveTabName(sheet.name)}
          >
            <input
              type="checkbox"
              className="rounded border-slate-300 text-[var(--color-primary)] focus:ring-[var(--color-primary)] cursor-pointer mt-0.5"
              checked={sheet.selected}
              onChange={() => toggleSheet(sheet.name)}
              onClick={(e) => e.stopPropagation()}
            />
            <span
              className={`text-sm font-medium ${
                activeTabName === sheet.name || sheet.selected
                  ? 'text-[var(--color-primary)]'
                  : 'text-slate-500'
              }`}
            >
              {sheet.name}
            </span>
          </div>
        ))}
      </div>

      <div className="border border-[var(--color-card-border)] rounded-lg overflow-hidden mb-5">
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="bg-slate-50 border-b border-[var(--color-card-border)]">
                {activeSheet.columns.map((header, idx) => (
                  <th key={idx} className="p-3">
                    <label className="flex items-center gap-2 cursor-pointer group">
                      <input
                        type="checkbox"
                        className="rounded border-slate-300 text-[var(--color-primary)] focus:ring-[var(--color-primary)] cursor-pointer"
                        checked={selectedColumnsSet.has(header)}
                        onChange={() => toggleColumn(activeSheet.name, header)}
                        disabled={!activeSheet.selected}
                      />
                      <span
                        className={`text-xs font-semibold transition-colors ${
                          !activeSheet.selected
                            ? 'text-slate-400'
                            : 'text-[var(--color-text-primary)] group-hover:text-[var(--color-primary)]'
                        }`}
                      >
                        {header}
                      </span>
                    </label>
                  </th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-[var(--color-card-border)]">
              {activeSheet.data.map((row, rowIdx) => (
                <tr key={rowIdx} className={activeSheet.selected ? 'hover:bg-slate-50' : 'bg-slate-50/50'}>
                  {row.map((cell, cellIdx) => {
                    const header = activeSheet.columns[cellIdx];
                    const isColSelected = header ? selectedColumnsSet.has(header) : false;
                    return (
                      <td
                        key={cellIdx}
                        className={`p-3 text-xs ${
                          activeSheet.selected && isColSelected
                            ? 'text-[var(--color-text-general)]'
                            : 'text-slate-300'
                        }`}
                      >
                        {cell}
                      </td>
                    );
                  })}
                </tr>
              ))}
              {activeSheet.data.length === 0 && (
                <tr>
                  <td colSpan={activeSheet.columns.length} className="p-4 text-center text-slate-400 text-xs">
                    Nenhum dado encontrado nesta aba
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
        {!activeSheet.selected && (
          <div className="bg-slate-100 text-slate-500 text-xs text-center py-2 border-t border-[var(--color-card-border)]">
            Selecione a aba acima para extrair dados desta planilha
          </div>
        )}
      </div>

      <div className="flex justify-end">
        <button
          className="btn-primary"
          onClick={confirm}
          disabled={totalSelectedColumns === 0}
        >
          Confirmar Seleção Extraída
        </button>
      </div>
    </div>
  );
}

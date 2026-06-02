import { use, useMemo } from 'react';
import XIcon from 'lucide-react/dist/esm/icons/x';
import AlertCircle from 'lucide-react/dist/esm/icons/alert-circle';
import FileText from 'lucide-react/dist/esm/icons/file-text';
import { MappingContext } from './MappingProvider';
import { DataSourceContext } from '../datasource/DataSourceProvider';
import { TemplatePreviewInteractive } from '../templatepreview/TemplatePreviewInteractive';

function escapeHtml(s: string): string {
  return s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
}

export function MappingSection() {
  const {
    state: { mappings, selectedCell, formatTemplate, listSeparator, listConnector },
    actions: { addColumnToFormat, updateFormat, addMapping, removeMapping, setSeparator, setConnector },
    meta: { textareaRef },
  } = use(MappingContext)!;

  const dataSource = use(DataSourceContext);
  const availableColumns = useMemo(
    () => dataSource
      ? dataSource.state.sheets.flatMap((s) => s.selected ? s.selectedColumns : [])
      : ([] as string[]),
    [dataSource?.state.sheets],
  );
  const availableColumnsSet = useMemo(
    () => new Set(availableColumns),
    [availableColumns],
  );

  const generatePreview = () => {
    if (!formatTemplate)
      return <span className="text-slate-400 italic">Preview do texto resultante...</span>;

    const escaped = escapeHtml(formatTemplate);
    const previewHtml = escaped.replace(/\{([^}]+)\}/g, (_match, col) => {
      if (availableColumnsSet.has(col)) {
        return `<mark class="bg-indigo-100 text-indigo-800 px-1 rounded not-italic">[Dado de ${col}]</mark>`;
      }
      return _match;
    });

    return <span dangerouslySetInnerHTML={{ __html: previewHtml }} />;
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-[5fr_7fr] gap-8">
      <div className="flex flex-col h-full">
        <h3 className="font-semibold text-[var(--color-text-primary)] mb-4">Adicionar Mapeamento</h3>

        <div className="bg-slate-50 border border-slate-200 rounded-lg p-4 mb-6 shadow-sm">
          <div className="mb-4">
            <label className="text-label block mb-2">1. Selecione as Variáveis</label>
            <div className="flex flex-wrap gap-2">
              {availableColumns.length === 0 ? (
                <span className="text-xs text-slate-400">Nenhuma coluna selecionada na Etapa 1.</span>
              ) : (
                availableColumns.map((col) => (
                  <button
                    key={col}
                    onClick={() => addColumnToFormat(col)}
                    className="text-[10px] font-bold px-2.5 py-1 bg-white border border-slate-300 text-slate-600 rounded-full hover:border-[var(--color-primary)] hover:text-[var(--color-primary)] transition-colors shadow-sm"
                  >
                    + {col}
                  </button>
                ))
              )}
            </div>
          </div>

          <div className="mb-4">
            <label className="text-label block mb-2 text-slate-500">2. Formato do Texto</label>
            <textarea
              ref={textareaRef}
              className="w-full bg-white border border-slate-300 rounded px-3 py-2 text-xs focus:ring-1 focus:ring-[var(--color-primary)] outline-none min-h-[60px] resize-y font-mono"
              placeholder="Ex: Serviços Realizados: {Atividade}. No Bairro: {Bairro}"
              value={formatTemplate}
              onChange={(e) => updateFormat(e.target.value)}
            />

            <div className="mt-2 text-[11px] bg-white border border-dashed border-slate-300 p-2 rounded">
              <span className="text-[10px] font-bold text-slate-400 block mb-1">PREVIEW:</span>
              {generatePreview()}
            </div>

            <div className="mt-3 grid grid-cols-2 gap-3">
              <div>
                <label className="text-[10px] font-medium text-slate-500 block mb-1">Separador de lista</label>
                <input
                  type="text"
                  className="w-full bg-white border border-slate-300 rounded px-2 py-1.5 text-xs focus:ring-1 focus:ring-[var(--color-primary)] outline-none"
                  value={listSeparator}
                  onChange={(e) => setSeparator(e.target.value)}
                  placeholder=", "
                />
              </div>
              <div>
                <label className="text-[10px] font-medium text-slate-500 block mb-1">Conector final</label>
                <input
                  type="text"
                  className="w-full bg-white border border-slate-300 rounded px-2 py-1.5 text-xs focus:ring-1 focus:ring-[var(--color-primary)] outline-none"
                  value={listConnector}
                  onChange={(e) => setConnector(e.target.value)}
                  placeholder=" e "
                />
              </div>
            </div>
          </div>

          <div className="mb-4 flex gap-4 items-end">
            <div className="flex-1">
              <label className="text-label block mb-1">3. Célula Destino (Template)</label>
              <div
                className={`w-full bg-white border rounded px-3 py-2 text-xs h-[34px] flex items-center shadow-sm ${
                  selectedCell
                    ? 'border-[var(--color-primary)] ring-1 ring-[var(--color-primary)]'
                    : 'border-slate-300'
                }`}
              >
                {selectedCell || (
                  <span className="text-slate-400">Clique na célula desejada no preview ao lado ➔</span>
                )}
              </div>
            </div>

            <button
              className="btn-primary flex-shrink-0 h-[34px] px-4 text-xs tracking-wide"
              onClick={addMapping}
              disabled={!selectedCell || !formatTemplate.trim()}
            >
              Confirmar
            </button>
          </div>

          {(!selectedCell || !formatTemplate.trim()) && (
            <div className="mt-2 flex items-start gap-2 text-[10px] text-slate-500 bg-white p-2 rounded border border-slate-100">
              <AlertCircle size={12} className="text-amber-500 shrink-0 mt-0.5" />
              <p>Escreva o formato desejado e clique em uma célula no preview para criar o vínculo.</p>
            </div>
          )}
        </div>

        <h3 className="font-semibold text-[var(--color-text-primary)] mb-3">
          Mapeamentos Ativos ({mappings.length})
        </h3>

        {mappings.length === 0 ? (
          <div className="text-center py-8 text-slate-400 border border-dashed border-slate-200 rounded-lg flex-1">
            Nenhum mapeamento configurado
          </div>
        ) : (
          <div className="space-y-2 overflow-y-auto pr-2 max-h-[400px]">
            {mappings.map((mapping) => (
              <div
                key={mapping.id}
                className="flex flex-col bg-white border border-slate-200 p-3 rounded shadow-sm hover:border-slate-300 transition-colors"
              >
                <div className="flex items-center justify-between mb-2">
                  <div className="flex flex-wrap gap-1">
                    {mapping.sourceColumns.length === 0 ? (
                      <span className="text-[10px] font-medium text-slate-400 bg-slate-100 px-2 py-0.5 rounded">
                        Texto Fixo
                      </span>
                    ) : (
                      mapping.sourceColumns.map((col, idx) => (
                        <span
                          key={idx}
                          className="font-medium text-white bg-[var(--color-primary)] px-2 py-0.5 rounded-full text-[9px]"
                        >
                          {col}
                        </span>
                      ))
                    )}
                  </div>

                  <div className="flex items-center gap-2">
                    <span className="text-slate-400 text-xs">➔</span>
                    <span className="font-bold text-slate-700 font-mono text-xs bg-indigo-50 border border-indigo-100 px-2 py-1 rounded flex items-center justify-center min-w-[32px]">
                      {mapping.templateCell}
                    </span>
                    <button
                      onClick={() => removeMapping(mapping.id)}
                      className="text-slate-400 hover:text-red-500 transition-colors p-1 ml-1"
                      title="Remover mapeamento"
                    >
                      <XIcon size={14} />
                    </button>
                  </div>
                </div>

                <div
                  className="text-[11px] text-slate-600 bg-slate-50 p-1.5 rounded border border-slate-100 font-mono line-clamp-2"
                  title={mapping.formatTemplate}
                >
                  <FileText size={10} className="inline mr-1 text-slate-400" />
                  {mapping.formatTemplate}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      <TemplatePreviewInteractive />
    </div>
  );
}

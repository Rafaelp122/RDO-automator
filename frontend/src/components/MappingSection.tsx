import React, { useState } from 'react';
import { X, Check, AlertCircle, FileText } from 'lucide-react';
import { TemplatePreview } from './TemplatePreview';
import { MappingData } from '../types';

interface MappingSectionProps {
  mappings: MappingData[];
  onMappingsChange: (mappings: MappingData[]) => void;
  availableColumns: string[];
}

export function MappingSection({ mappings, onMappingsChange, availableColumns }: MappingSectionProps) {
  const [selectedCell, setSelectedCell] = useState<string | null>(null);
  const [formatTemplate, setFormatTemplate] = useState<string>('');

  // Derived state to quickly check mapped cells and pass to TemplatePreview
  const mappedCellsMap = mappings.reduce((acc, curr) => {
    acc[curr.templateCell] = curr;
    return acc;
  }, {} as Record<string, MappingData>);

  const handleCellSelect = (cellRef: string) => {
    setSelectedCell(cellRef);
  };

  const handleColumnChipClick = (col: string) => {
    const textarea = document.getElementById('format-template-textarea') as HTMLTextAreaElement;
    if (textarea) {
      const start = textarea.selectionStart;
      const text = formatTemplate;
      const newText = text.substring(0, start) + `{${col}}` + text.substring(start);
      setFormatTemplate(newText);
      
      // Attempt to restore focus and cursor position after React re-renders
      setTimeout(() => {
        textarea.focus();
        textarea.setSelectionRange(start + col.length + 2, start + col.length + 2);
      }, 0);
    } else {
      setFormatTemplate(prev => prev ? `${prev} {${col}}` : `{${col}}`);
    }
  };

  const extractUsedColumns = (format: string) => {
    const matches = format.match(/\{([^}]+)\}/g);
    if (!matches) return [];
    
    const cols = matches.map(m => m.slice(1, -1));
    return [...new Set(cols)]; // return unique
  };

  const addMapping = () => {
    if (!selectedCell || !formatTemplate.trim()) return;
    
    // Check if cell is already mapped, if so replace it
    const existingIndex = mappings.findIndex(m => m.templateCell === selectedCell);
    const sourceColumns = extractUsedColumns(formatTemplate);
    
    const newMapping: MappingData = {
      id: Math.random().toString(36).substr(2, 9),
      templateCell: selectedCell,
      formatTemplate: formatTemplate.trim(),
      sourceColumns
    };

    if (existingIndex >= 0) {
      const newMappings = [...mappings];
      newMappings[existingIndex] = newMapping;
      onMappingsChange(newMappings);
    } else {
      onMappingsChange([...mappings, newMapping]);
    }
    
    // Reset selection after mapping
    setSelectedCell(null);
    setFormatTemplate('');
  };

  const removeMapping = (id: string) => {
    onMappingsChange(mappings.filter(m => m.id !== id));
  };

  // Generate a dynamic preview
  const generatePreview = () => {
    if (!formatTemplate) return <span className="text-slate-400 italic">Preview do texto resultante...</span>;
    
    const previewText = formatTemplate.replace(/\{([^}]+)\}/g, (match, col) => {
      // Check if it's a valid column, if so, show a mock value, otherwise keep the placeholder
      if (availableColumns.includes(col)) {
        return `<mark class="bg-indigo-100 text-indigo-800 px-1 rounded not-italic">[Dado de ${col}]</mark>`;
      }
      return match;
    });

    return <span dangerouslySetInnerHTML={{ __html: previewText }} />;
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
      {/* List of mappings and actions */}
      <div className="flex flex-col h-full">
        <h3 className="font-semibold text-[var(--color-text-primary)] mb-4">Adicionar Mapeamento</h3>
        
        <div className="bg-slate-50 border border-slate-200 rounded-lg p-4 mb-6 shadow-sm">
          
          <div className="mb-4">
            <label className="text-label block mb-2">1. Selecione as Variáveis</label>
            <div className="flex flex-wrap gap-2">
              {availableColumns.length === 0 ? (
                <span className="text-xs text-slate-400">Nenhuma coluna selecionada na Etapa 1.</span>
              ) : (
                availableColumns.map(col => (
                  <button
                    key={col}
                    onClick={() => handleColumnChipClick(col)}
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
              id="format-template-textarea"
              className="w-full bg-white border border-slate-300 rounded px-3 py-2 text-xs focus:ring-1 focus:ring-[var(--color-primary)] outline-none min-h-[60px] resize-y font-mono"
              placeholder="Ex: Serviços Realizados: {Atividade}. No Bairro: {Bairro}"
              value={formatTemplate}
              onChange={(e) => setFormatTemplate(e.target.value)}
            />
            
            <div className="mt-2 text-[11px] bg-white border border-dashed border-slate-300 p-2 rounded">
              <span className="text-[10px] font-bold text-slate-400 block mb-1">PREVIEW:</span>
              {generatePreview()}
            </div>
          </div>
          
          <div className="mb-4 flex gap-4 items-end">
            <div className="flex-1">
              <label className="text-label block mb-1">3. Célula Destino (Template)</label>
              <div 
                className={`w-full bg-white border rounded px-3 py-2 text-xs h-[34px] flex items-center shadow-sm ${selectedCell ? 'border-[var(--color-primary)] ring-1 ring-[var(--color-primary)]' : 'border-slate-300'}`}
              >
                {selectedCell || <span className="text-slate-400">Clique na célula desejada no preview ao lado ➔</span>}
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

        <h3 className="font-semibold text-[var(--color-text-primary)] mb-3">Mapeamentos Ativos ({mappings.length})</h3>
        
        {mappings.length === 0 ? (
          <div className="text-center py-8 text-slate-400 border border-dashed border-slate-200 rounded-lg flex-1">
            Nenhum mapeamento configurado
          </div>
        ) : (
          <div className="space-y-2 overflow-y-auto pr-2 max-h-[400px]">
            {mappings.map(mapping => (
              <div key={mapping.id} className="flex flex-col bg-white border border-slate-200 p-3 rounded shadow-sm hover:border-slate-300 transition-colors">
                <div className="flex items-center justify-between mb-2">
                  <div className="flex flex-wrap gap-1">
                    {mapping.sourceColumns.length === 0 ? (
                      <span className="text-[10px] font-medium text-slate-400 bg-slate-100 px-2 py-0.5 rounded">Texto Fixo</span>
                    ) : (
                      mapping.sourceColumns.map((col, idx) => (
                        <span key={idx} className="font-medium text-white bg-[var(--color-primary)] px-2 py-0.5 rounded-full text-[9px]">
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
                      <X size={14} />
                    </button>
                  </div>
                </div>
                
                <div className="text-[11px] text-slate-600 bg-slate-50 p-1.5 rounded border border-slate-100 font-mono line-clamp-2" title={mapping.formatTemplate}>
                  <FileText size={10} className="inline mr-1 text-slate-400" />
                  {mapping.formatTemplate}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Interactive Template Preview */}
      <div className="flex flex-col">
        <h3 className="font-semibold text-[var(--color-text-primary)] mb-4 flex items-center justify-between">
          <span>Template Interativo</span>
          <span className="text-[10px] bg-indigo-50 text-[var(--color-primary)] px-2 py-1 rounded font-bold">
            Clique numa célula para selecionar
          </span>
        </h3>
        <TemplatePreview 
          isInteractive={true} 
          onComplete={() => {}} 
          onCellSelect={handleCellSelect}
          mappedCells={mappedCellsMap as any} 
          selectedCell={selectedCell}
        />
      </div>
    </div>
  );
}

import React, { useState } from 'react';
import { Type } from 'lucide-react';
import { MappingData } from '../types';

interface TemplatePreviewProps {
  onComplete: () => void;
  isInteractive?: boolean;
  onCellSelect?: (cellRef: string) => void;
  mappedCells?: Record<string, MappingData>;
  selectedCell?: string | null;
}

// Generate a simple Excel-like grid
const COLS = ['A', 'B', 'C', 'D', 'E', 'F'];
const ROWS = Array.from({ length: 8 }, (_, i) => i + 1);

export function TemplatePreview({ 
  onComplete, 
  isInteractive = false, 
  onCellSelect,
  mappedCells = {},
  selectedCell = null
}: TemplatePreviewProps) {
  
  // Fake template structure
  const templateStructure: Record<string, {label?: string, merges?: number}> = {
    'A1': { label: 'RDO - RELATÓRIO DIÁRIO DE OBRA', merges: 6 },
    'A3': { label: 'Data:' },
    'C3': { label: 'Equipe:' },
    'A5': { label: 'Atividades Executadas', merges: 6 },
    'A6': { label: 'Item' },
    'B6': { label: 'Descrição' },
    'D6': { label: 'Qtd' },
    'E6': { label: 'Unid' },
  };

  const interactiveClasses = isInteractive ? "cursor-pointer hover:bg-indigo-50" : "";

  return (
    <div className="mt-6 animate-in fade-in duration-500 w-full">
      {!isInteractive && (
        <div className="flex items-center justify-between mb-3">
          <h3 className="font-semibold text-[var(--color-text-primary)]">Preview do Template</h3>
          <span className="text-[10px] bg-slate-100 text-slate-500 px-2 py-1 rounded">Visualização Simplificada</span>
        </div>
      )}
      
      <div className={`overflow-x-auto border border-slate-200 rounded ${isInteractive ? 'bg-white shadow-sm' : ''} excel-grid relative`}>
        <table className="w-full border-collapse text-xs select-none">
          <thead>
            <tr>
              <th className="w-8 border border-slate-200 bg-slate-100 p-1"></th>
              {COLS.map(col => (
                <th key={col} className="border border-slate-200 bg-slate-100 font-normal p-1 px-4 text-center text-slate-500">
                  {col}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {ROWS.map(row => (
              <tr key={row}>
                <td className="border border-slate-200 bg-slate-100 text-center text-slate-500 p-1">
                  {row}
                </td>
                {COLS.map(col => {
                  const cellRef = `${col}${row}`;
                  const mapping = mappedCells[cellRef];
                  const isSelected = selectedCell === cellRef;
                  
                  // Skip rendered cells due to merge (simulated simply for UI look)
                  if (row === 1 && col !== 'A') return null;
                  if (row === 5 && col !== 'A') return null;
                  
                  const isMergedRow = row === 1 || row === 5;
                  
                  return (
                    <td 
                      key={cellRef}
                      colSpan={isMergedRow ? COLS.length : 1}
                      className={`
                        border border-slate-200 p-2 h-8 relative
                        ${isMergedRow ? 'bg-slate-50 font-bold text-center' : 'text-left'}
                        ${templateStructure[cellRef] ? 'font-medium text-slate-700' : ''}
                        ${!isMergedRow && !templateStructure[cellRef] ? interactiveClasses : ''}
                        ${isSelected ? 'ring-2 ring-inset ring-[var(--color-primary)] bg-indigo-50' : ''}
                        ${mapping ? 'bg-indigo-50/70' : ''}
                        transition-all duration-150
                      `}
                      onClick={() => {
                        if (isInteractive && onCellSelect && !isMergedRow && !templateStructure[cellRef]) {
                          onCellSelect(cellRef);
                        }
                      }}
                    >
                      <div className="flex items-center justify-between w-full h-full relative z-10">
                        <span>{templateStructure[cellRef]?.label}</span>
                        
                        {mapping && !templateStructure[cellRef] && !isMergedRow && (
                          <div className="absolute inset-0 flex items-center justify-center p-1">
                            <div className="bg-[var(--color-primary)] text-white text-[9px] px-1.5 py-0.5 rounded shadow-sm cursor-default flex items-center gap-1 w-full justify-center max-w-full overflow-hidden" title={mapping.formatTemplate}>
                              <Type size={10} className="shrink-0" />
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

      {!isInteractive && (
        <div className="flex justify-end mt-5">
          <button className="btn-primary" onClick={onComplete}>
            Confirmar Template
          </button>
        </div>
      )}
    </div>
  );
}

import { use, useState } from 'react';
import { MappingContext } from '../mapping/MappingProvider';
import { TemplateSourceContext } from '../templatesource/TemplateSourceProvider';
import { TemplatePreviewGrid } from './TemplatePreviewGrid';
import type { MappingData } from '../../types';

const ZOOM_LEVELS = [50, 75, 100, 125, 150];

export function TemplatePreviewInteractive() {
  const {
    state: { selectedCell },
    actions: { selectCell },
  } = use(MappingContext)!;

  const {
    state: { sheets },
  } = use(TemplateSourceContext)!;

  const [zoom, setZoom] = useState(100);

  const { mappings } = use(MappingContext)!.state;
  const mappedCellsMap = mappings.reduce(
    (acc, curr) => {
      acc[curr.templateCell] = curr;
      return acc;
    },
    {} as Record<string, MappingData>,
  );

  return (
    <div className="flex flex-col">
      <h3 className="font-semibold text-[var(--color-text-primary)] mb-2 flex items-center justify-between">
        <span>Template Interativo</span>
        <span className="text-[10px] bg-indigo-50 text-[var(--color-primary)] px-2 py-1 rounded font-bold">
          Clique numa célula para selecionar
        </span>
      </h3>
      <div className="flex items-center gap-1 mb-2">
        {ZOOM_LEVELS.map((level) => (
          <button
            key={level}
            onClick={() => setZoom(level)}
            className={`text-[10px] px-1.5 py-0.5 rounded border transition-colors ${
              zoom === level
                ? 'border-[var(--color-primary)] bg-indigo-50 text-[var(--color-primary)] font-bold'
                : 'border-slate-200 text-slate-500 hover:border-slate-300'
            }`}
          >
            {level}%
          </button>
        ))}
      </div>
      <TemplatePreviewGrid
        sheets={sheets}
        onCellClick={selectCell}
        mappedCells={mappedCellsMap}
        selectedCell={selectedCell}
        zoom={zoom}
      />
    </div>
  );
}

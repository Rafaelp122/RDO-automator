import { use } from 'react';
import { MappingContext } from '../mapping/MappingProvider';
import { TemplateSourceContext } from '../templatesource/TemplateSourceProvider';
import { TemplatePreviewGrid } from './TemplatePreviewGrid';
import type { MappingData } from '../../types';

export function TemplatePreviewInteractive() {
  const {
    state: { selectedCell },
    actions: { selectCell },
  } = use(MappingContext)!;

  const {
    state: { sheets },
  } = use(TemplateSourceContext)!;

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
      <h3 className="font-semibold text-[var(--color-text-primary)] mb-4 flex items-center justify-between">
        <span>Template Interativo</span>
        <span className="text-[10px] bg-indigo-50 text-[var(--color-primary)] px-2 py-1 rounded font-bold">
          Clique numa célula para selecionar
        </span>
      </h3>
      <TemplatePreviewGrid
        sheets={sheets}
        onCellClick={selectCell}
        mappedCells={mappedCellsMap}
        selectedCell={selectedCell}
      />
    </div>
  );
}

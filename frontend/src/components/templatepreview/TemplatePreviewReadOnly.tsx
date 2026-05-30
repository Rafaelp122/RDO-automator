import { use } from 'react';
import { TemplateSourceContext } from '../templatesource/TemplateSourceProvider';
import { TemplatePreviewGrid } from './TemplatePreviewGrid';

export function TemplatePreviewReadOnly() {
  const {
    state: { sheets, isComplete },
    actions: { confirm },
  } = use(TemplateSourceContext)!;

  if (isComplete) return null;

  return (
    <div className="mt-6 animate-in fade-in duration-500 w-full">
      <div className="flex items-center justify-between mb-3">
        <h3 className="font-semibold text-[var(--color-text-primary)]">Preview do Template</h3>
        <span className="text-[10px] bg-slate-100 text-slate-500 px-2 py-1 rounded">Visualização</span>
      </div>

      <TemplatePreviewGrid sheets={sheets} />

      <div className="flex justify-end mt-5">
        <button className="btn-primary" onClick={confirm}>
          Confirmar Template
        </button>
      </div>
    </div>
  );
}

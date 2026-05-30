import { createContext, useState, useCallback, type ReactNode } from 'react';
import { use } from 'react';
import type { TemplateSourceContextValue, TemplateSourceState } from '../../types';
import { previewTemplate } from '../../services/api';
import { WizardContext } from '../wizard/WizardProvider';

export const TemplateSourceContext = createContext<TemplateSourceContextValue | null>(null);

const initialState: TemplateSourceState = {
  fileName: null,
  file: null,
  sheets: [],
  isComplete: false,
};

export function TemplateSourceProvider({ children }: { children: ReactNode }) {
  const [state, setState] = useState<TemplateSourceState>(initialState);
  const wizard = use(WizardContext);

  const upload = useCallback(async (name: string, f: File) => {
    setState((prev) => ({ ...prev, fileName: name, file: f, isComplete: false }));
    try {
      const result = await previewTemplate(f);
      setState((prev) => ({ ...prev, sheets: result.sheets }));
    } catch (err) {
      alert((err as Error).message);
      setState((prev) => ({ ...prev, fileName: null, file: null }));
    }
  }, []);

  const clear = useCallback(() => {
    setState({ ...initialState });
  }, []);

  const confirm = useCallback(() => {
    setState((prev) => ({ ...prev, isComplete: true }));
    wizard?.actions.completeStep(2);
  }, [wizard]);

  return (
    <TemplateSourceContext
      value={{
        state,
        actions: { upload, clear, confirm },
        meta: {},
      }}
    >
      {children}
    </TemplateSourceContext>
  );
}

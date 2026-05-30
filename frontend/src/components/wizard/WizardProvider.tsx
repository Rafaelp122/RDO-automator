import { createContext, useState, useCallback, type ReactNode } from 'react';
import type { WizardContextValue, WizardState } from '../../types';

export const WizardContext = createContext<WizardContextValue | null>(null);

const initialState: WizardState = {
  activeSegment: 1,
  completedSteps: new Set<number>(),
};

export function WizardProvider({ children }: { children: ReactNode }) {
  const [state, setState] = useState<WizardState>(initialState);

  const openStep = useCallback((n: number) => {
    setState((prev) => ({
      ...prev,
      activeSegment: prev.activeSegment === n ? 0 : n,
    }));
  }, []);

  const closeAll = useCallback(() => {
    setState((prev) => ({ ...prev, activeSegment: 0 }));
  }, []);

  const completeStep = useCallback((n: number) => {
    setState((prev) => {
      const next = new Set(prev.completedSteps);
      next.add(n);
      const nextActive = n < 2 ? n + 1 : 3;
      return {
        ...prev,
        completedSteps: next,
        activeSegment: nextActive,
      };
    });
  }, []);

  return (
    <WizardContext value={{ state, actions: { openStep, closeAll, completeStep }, meta: {} }}>
      {children}
    </WizardContext>
  );
}

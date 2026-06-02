import { createContext, useState, useCallback, useRef, type ReactNode } from 'react';
import { use } from 'react';
import type { DataSourceContextValue, DataSourceState, Sheet } from '../../types';
import { previewSource } from '../../services/api';
import { WizardContext } from '../wizard/WizardProvider';

export const DataSourceContext = createContext<DataSourceContextValue | null>(null);

const initialState: DataSourceState = {
  fileName: null,
  file: null,
  sheets: [],
  isComplete: false,
  headerRow: 0,
};

export function DataSourceProvider({ children }: { children: ReactNode }) {
  const [state, setState] = useState<DataSourceState>(initialState);
  const wizard = use(WizardContext);
  const currentFile = useRef<File | null>(null);

  const upload = useCallback(async (name: string, f: File) => {
    currentFile.current = f;
    setState((prev) => ({ ...prev, fileName: name, file: f, isComplete: false, headerRow: 0 }));
    try {
      const result = await previewSource(f, 0);
      const sheets: Sheet[] = result.sheets.map((s) => ({
        name: s.name,
        selected: false,
        columns: s.columns,
        selectedColumns: [],
        data: s.data,
      }));
      setState((prev) => ({ ...prev, sheets }));
    } catch (err) {
      alert((err as Error).message);
      setState((prev) => ({ ...prev, fileName: null, file: null }));
    }
  }, []);

  const changeHeaderRow = useCallback(async (headerRow: number) => {
    const f = currentFile.current;
    if (!f) return;
    setState((prev) => ({ ...prev, headerRow, isComplete: false }));
    try {
      const result = await previewSource(f, headerRow);
      const sheets: Sheet[] = result.sheets.map((s) => ({
        name: s.name,
        selected: false,
        columns: s.columns,
        selectedColumns: [],
        data: s.data,
      }));
      setState((prev) => ({ ...prev, sheets }));
    } catch (err) {
      alert((err as Error).message);
    }
  }, []);

  const clear = useCallback(() => {
    setState({ ...initialState });
  }, []);

  const toggleSheet = useCallback((name: string) => {
    setState((prev) => ({
      ...prev,
      sheets: prev.sheets.map((s) =>
        s.name === name ? { ...s, selected: !s.selected } : s,
      ),
    }));
  }, []);

  const toggleColumn = useCallback((sheetName: string, col: string) => {
    setState((prev) => ({
      ...prev,
      sheets: prev.sheets.map((s) => {
        if (s.name !== sheetName) return s;
        const alreadySelected = s.selectedColumns.includes(col);
        return {
          ...s,
          selectedColumns: alreadySelected
            ? s.selectedColumns.filter((c) => c !== col)
            : [...s.selectedColumns, col],
        };
      }),
    }));
  }, []);

  const confirm = useCallback(() => {
    setState((prev) => ({ ...prev, isComplete: true }));
    wizard?.actions.completeStep(1);
  }, [wizard]);

  return (
    <DataSourceContext
      value={{
        state,
        actions: { upload, clear, toggleSheet, toggleColumn, confirm, changeHeaderRow },
        meta: {},
      }}
    >
      {children}
    </DataSourceContext>
  );
}

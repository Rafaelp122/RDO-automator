import { createContext, useState, useCallback, useRef, type ReactNode } from 'react';
import type { MappingContextValue, MappingState, MappingData } from '../../types';

export const MappingContext = createContext<MappingContextValue | null>(null);

const initialState: MappingState = {
  mappings: [],
  selectedCell: null,
  formatTemplate: '',
  listSeparator: ', ',
  listConnector: ' e ',
};

export function MappingProvider({ children }: { children: ReactNode }) {
  const [state, setState] = useState<MappingState>(initialState);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const selectCell = useCallback((ref: string) => {
    setState((prev) => ({ ...prev, selectedCell: ref }));
  }, []);

  const addColumnToFormat = useCallback((col: string) => {
    const textarea = textareaRef.current;
    if (textarea) {
      const start = textarea.selectionStart;
      const newText = state.formatTemplate.substring(0, start) + `{${col}}` + state.formatTemplate.substring(start);
      setState((prev) => ({ ...prev, formatTemplate: newText }));
      setTimeout(() => {
        textarea.focus();
        textarea.setSelectionRange(start + col.length + 2, start + col.length + 2);
      }, 0);
    } else {
      setState((prev) => ({
        ...prev,
        formatTemplate: prev.formatTemplate ? `${prev.formatTemplate} {${col}}` : `{${col}}`,
      }));
    }
  }, [state.formatTemplate]);

  const updateFormat = useCallback((text: string) => {
    setState((prev) => ({ ...prev, formatTemplate: text }));
  }, []);

  const addMapping = useCallback(() => {
    setState((prev) => {
      const { selectedCell, formatTemplate, mappings } = prev;
      if (!selectedCell || !formatTemplate.trim()) return prev;

      const matches = formatTemplate.match(/\{([^}]+)\}/g);
      const sourceColumns = matches ? [...new Set(matches.map((m) => m.slice(1, -1)))] as string[] : [];

      const newMapping: MappingData = {
        id: Math.random().toString(36).substring(2, 11),
        templateCell: selectedCell,
        formatTemplate: formatTemplate.trim(),
        sourceColumns,
      };

      const existingIndex = mappings.findIndex((m) => m.templateCell === selectedCell);
      const updatedMappings = existingIndex >= 0
        ? mappings.map((m, i) => i === existingIndex ? newMapping : m)
        : [...mappings, newMapping];

      return {
        ...prev,
        mappings: updatedMappings,
        selectedCell: null,
        formatTemplate: '',
      };
    });
  }, []);

  const removeMapping = useCallback((id: string) => {
    setState((prev) => ({
      ...prev,
      mappings: prev.mappings.filter((m) => m.id !== id),
    }));
  }, []);

  const setSeparator = useCallback((v: string) => {
    setState((prev) => ({ ...prev, listSeparator: v }));
  }, []);

  const setConnector = useCallback((v: string) => {
    setState((prev) => ({ ...prev, listConnector: v }));
  }, []);

  return (
    <MappingContext
      value={{
        state,
        actions: {
          selectCell,
          addColumnToFormat,
          updateFormat,
          addMapping,
          removeMapping,
          setSeparator,
          setConnector,
        },
        meta: { textareaRef },
      }}
    >
      {children}
    </MappingContext>
  );
}

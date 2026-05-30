# Vercel Composition Patterns Refactor — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Refactor the React 19 frontend to follow all vercel-composition-patterns rules: compound components, context providers with `state/actions/meta` interfaces, explicit variants, state decoupling, and React 19 `use()` API.

**Architecture:** 4 context providers (`Wizard`, `DataSource`, `TemplateSource`, `Mapping`) replace 13 `useState` calls in App.tsx. `TemplatePreview` splits into `ReadOnly` and `Interactive` explicit variants sharing a `TemplatePreviewGrid`. `AccordionSection` replaced by `Wizard.Step` compound component. `App.tsx` reduces from 269 to ~50 lines of provider composition.

**Tech Stack:** React 19.0.1, TypeScript 5.8, Motion (Framer Motion), Lucide React, Tailwind CSS 4, Vite 6

---

### Task 1: Update types.ts with context interfaces

**Files:**
- Modify: `frontend/src/types.ts`

- [ ] **Step 1: Add context value interfaces to types.ts**

```typescript
// ... existing types remain ...

// ---- Context value types (state/actions/meta pattern) ----

export interface WizardState {
  activeSegment: number;
  completedSteps: Set<number>;
}

export interface WizardActions {
  openStep: (n: number) => void;
  closeAll: () => void;
  completeStep: (n: number) => void;
}

export interface WizardContextValue {
  state: WizardState;
  actions: WizardActions;
  meta: Record<string, never>;
}

export interface DataSourceState {
  fileName: string | null;
  file: File | null;
  sheets: Sheet[];
  isComplete: boolean;
}

export interface DataSourceActions {
  upload: (name: string, f: File) => Promise<void>;
  clear: () => void;
  toggleSheet: (name: string) => void;
  toggleColumn: (sheetName: string, col: string) => void;
  confirm: () => void;
}

export interface DataSourceContextValue {
  state: DataSourceState;
  actions: DataSourceActions;
  meta: Record<string, never>;
}

export interface TemplateSourceState {
  fileName: string | null;
  file: File | null;
  sheets: TemplateSheet[];
  isComplete: boolean;
}

export interface TemplateSourceActions {
  upload: (name: string, f: File) => Promise<void>;
  clear: () => void;
  confirm: () => void;
}

export interface TemplateSourceContextValue {
  state: TemplateSourceState;
  actions: TemplateSourceActions;
  meta: Record<string, never>;
}

export interface MappingState {
  mappings: MappingData[];
  selectedCell: string | null;
  formatTemplate: string;
  listSeparator: string;
  listConnector: string;
}

export interface MappingActions {
  selectCell: (ref: string) => void;
  addColumnToFormat: (col: string) => void;
  updateFormat: (text: string) => void;
  addMapping: () => void;
  removeMapping: (id: string) => void;
  setSeparator: (v: string) => void;
  setConnector: (v: string) => void;
}

export interface MappingMeta {
  textareaRef: React.RefObject<HTMLTextAreaElement | null>;
}

export interface MappingContextValue {
  state: MappingState;
  actions: MappingActions;
  meta: MappingMeta;
}
```

- [ ] **Step 2: Run lint to verify**

```
npm run lint --prefix frontend
```

Expected: PASS (new types don't break anything yet, they're additive)

- [ ] **Step 3: Commit**

```bash
git add frontend/src/types.ts
git commit -m "feat: add context interface types for composition refactor"
```

---

### Task 2: Create WizardProvider and WizardStep compound component

**Files:**
- Create: `frontend/src/components/wizard/WizardProvider.tsx`
- Create: `frontend/src/components/wizard/WizardStep.tsx`
- Delete later: `frontend/src/components/AccordionSection.tsx`

- [ ] **Step 1: Create WizardProvider.tsx**

```typescript
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
```

- [ ] **Step 2: Create WizardStep.tsx**

```typescript
import { use, type ReactNode } from 'react';
import { ChevronDown, ChevronUp, Lock } from 'lucide-react';
import { motion, AnimatePresence } from 'motion/react';
import { WizardContext } from './WizardProvider';

interface WizardStepProps {
  step: number;
  title: string;
  children: ReactNode;
}

function Step({ step, title, children }: WizardStepProps) {
  const {
    state: { activeSegment, completedSteps },
    actions: { openStep },
  } = use(WizardContext)!;

  const isExpanded = activeSegment === step;
  const isCompleted = completedSteps.has(step);
  const isLocked = step === 3 && (!completedSteps.has(1) || !completedSteps.has(2));

  return (
    <div className={`bg-white border border-[var(--color-card-border)] rounded-[12px] shadow-sm mb-4 flex flex-col overflow-hidden transition-all duration-300 ${isLocked ? 'opacity-50 grayscale select-none' : ''}`}>
      <StepHeader
        step={step}
        title={title}
        isExpanded={isExpanded}
        isCompleted={isCompleted}
        isLocked={isLocked}
        onToggle={() => { if (!isLocked) openStep(step); }}
      />
      <StepContent isExpanded={isExpanded && !isLocked}>
        {children}
      </StepContent>
    </div>
  );
}

interface StepHeaderProps {
  step: number;
  title: string;
  isExpanded: boolean;
  isCompleted: boolean;
  isLocked: boolean;
  onToggle: () => void;
}

function StepHeader({ step, title, isExpanded, isCompleted, isLocked, onToggle }: StepHeaderProps) {
  return (
    <button
      className={`w-full p-4 flex items-center justify-between transition-colors ${isLocked ? 'cursor-not-allowed' : 'cursor-pointer hover:bg-slate-50'}`}
      onClick={onToggle}
      title={isLocked ? 'Conclua os passos 1 e 2 acima para liberar o mapeamento de células' : undefined}
    >
      <div className="flex items-center gap-3">
        <div className={`w-6 h-6 rounded-full flex items-center justify-center mr-1 ${isLocked ? 'bg-slate-200' : isCompleted ? 'bg-green-500' : 'border-2 border-[var(--color-primary)] bg-white'}`}>
          {isLocked ? (
            <Lock size={12} className="text-slate-500" />
          ) : isCompleted ? (
            <svg className="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="3" d="M5 13l4 4L19 7"></path></svg>
          ) : (
            <span className="text-[11px] font-bold text-[var(--color-primary)]">0{step}</span>
          )}
        </div>
        <h2 className={`text-[14px] font-bold ${isLocked ? 'text-slate-500' : 'text-[var(--color-primary)]'}`}>
          {title} {isLocked && <span className="opacity-70 font-normal ml-1">(Bloqueado)</span>}
        </h2>
      </div>
      <div className="flex items-center gap-4">
        <div className="text-[var(--color-text-secondary)]">
          {!isLocked && (isExpanded ? <ChevronUp size={20} /> : <ChevronDown size={20} />)}
        </div>
      </div>
    </button>
  );
}

function StepContent({ children, isExpanded }: { children: ReactNode; isExpanded: boolean }) {
  return (
    <AnimatePresence initial={false}>
      {isExpanded && (
        <motion.div
          initial={{ height: 0, opacity: 0 }}
          animate={{ height: 'auto', opacity: 1 }}
          exit={{ height: 0, opacity: 0 }}
          transition={{ duration: 0.3, ease: 'easeInOut' }}
        >
          <div className="px-6 pb-6 pt-2 border-t border-[var(--color-card-border)] bg-white h-full relative z-0">
            {children}
          </div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}

export const Wizard = { Step, StepHeader, StepContent };
```

- [ ] **Step 3: Run lint**

```
npm run lint --prefix frontend
```

Expected: PASS

- [ ] **Step 4: Commit**

```bash
git add frontend/src/components/wizard/
git commit -m "feat: add WizardProvider and Wizard.Step compound component"
```

---

### Task 3: Create DataSourceProvider and SourceFileUpload

**Files:**
- Create: `frontend/src/components/datasource/DataSourceProvider.tsx`
- Create: `frontend/src/components/datasource/SourceFileUpload.tsx`

- [ ] **Step 1: Create DataSourceProvider.tsx**

```typescript
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
};

export function DataSourceProvider({ children }: { children: ReactNode }) {
  const [state, setState] = useState<DataSourceState>(initialState);
  const wizard = use(WizardContext);

  const upload = useCallback(async (name: string, f: File) => {
    setState((prev) => ({ ...prev, fileName: name, file: f, isComplete: false }));
    try {
      const result = await previewSource(f);
      const sheets: Sheet[] = result.sheets.map((s) => ({
        name: s.name,
        selected: true,
        columns: s.columns,
        selectedColumns: [...s.columns],
        data: s.data,
      }));
      setState((prev) => ({ ...prev, sheets }));
    } catch (err) {
      alert((err as Error).message);
      setState((prev) => ({ ...prev, fileName: null, file: null }));
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
        actions: { upload, clear, toggleSheet, toggleColumn, confirm },
        meta: {},
      }}
    >
      {children}
    </DataSourceContext>
  );
}
```

- [ ] **Step 2: Create SourceFileUpload.tsx**

```typescript
import { use } from 'react';
import { DataSourceContext } from './DataSourceProvider';
import { FileUpload } from '../FileUpload';

export function SourceFileUpload() {
  const {
    state: { fileName },
    actions: { upload, clear },
  } = use(DataSourceContext)!;

  const handleFileSelect = async (name: string | null, file?: File | null) => {
    if (!name || !file) {
      clear();
      return;
    }
    await upload(name, file);
  };

  return (
    <FileUpload
      label="Planilha de Origem"
      selectedFileName={fileName}
      accept=".xlsx,.xls"
      onFileSelect={handleFileSelect}
    />
  );
}
```

- [ ] **Step 3: Run lint**

```
npm run lint --prefix frontend
```

Expected: PASS

- [ ] **Step 4: Commit**

```bash
git add frontend/src/components/datasource/
git commit -m "feat: add DataSourceProvider and SourceFileUpload wrapper"
```

---

### Task 4: Rewrite DataPreview to read from DataSourceContext

**Files:**
- Modify: `frontend/src/components/datasource/DataPreview.tsx` (move and rewrite from `components/DataPreview.tsx`)

- [ ] **Step 1: Create rewritten DataPreview.tsx in datasource/ directory**

```typescript
import { useState, useEffect, use, type ChangeEvent } from 'react';
import { DataSourceContext } from './DataSourceProvider';

export function DataPreview() {
  const {
    state: { sheets },
    actions: { toggleSheet, toggleColumn, confirm },
  } = use(DataSourceContext)!;

  const [activeTabName, setActiveTabName] = useState<string>(sheets[0]?.name ?? '');

  useEffect(() => {
    if (!sheets.find((s) => s.name === activeTabName)) {
      setActiveTabName(sheets[0]?.name ?? '');
    }
  }, [sheets, activeTabName]);

  const activeSheet = sheets.find((s) => s.name === activeTabName) ?? sheets[0];

  const selectedSheetsCount = sheets.filter((s) => s.selected).length;
  const totalSelectedColumns = sheets.reduce(
    (acc, s) => acc + (s.selected ? s.selectedColumns.length : 0),
    0,
  );

  if (!activeSheet) return null;

  return (
    <div className="mt-6 animate-in fade-in slide-in-from-bottom-2 duration-500">
      <div className="flex items-center justify-between mb-4">
        <div>
          <h3 className="font-semibold text-[var(--color-text-primary)]">Preview dos Dados</h3>
          <p className="text-[var(--color-text-secondary)] mt-1">Selecione as abas e colunas que deseja extrair</p>
        </div>
        <div className="bg-indigo-50 text-[var(--color-primary)] px-3 py-1.5 rounded-full text-xs font-bold flex items-center gap-2">
          <span>{selectedSheetsCount} {selectedSheetsCount === 1 ? 'aba selecionada' : 'abas selecionadas'}</span>
          <span className="w-1 h-1 bg-[var(--color-primary)] rounded-full"></span>
          <span>{totalSelectedColumns} colunas</span>
        </div>
      </div>

      <div className="flex border-b border-[var(--color-card-border)] mb-4 overflow-x-auto">
        {sheets.map((sheet) => (
          <div
            key={sheet.name}
            className={`flex items-center gap-2 px-4 py-2 cursor-pointer border-b-2 transition-colors ${
              activeTabName === sheet.name
                ? 'border-[var(--color-primary)] bg-indigo-50/50'
                : 'border-transparent hover:bg-slate-50'
            }`}
            onClick={() => setActiveTabName(sheet.name)}
          >
            <input
              type="checkbox"
              className="rounded border-slate-300 text-[var(--color-primary)] focus:ring-[var(--color-primary)] cursor-pointer mt-0.5"
              checked={sheet.selected}
              onChange={(e) => {
                e.stopPropagation();
                toggleSheet(sheet.name);
              }}
              onClick={(e) => e.stopPropagation()}
            />
            <span
              className={`text-sm font-medium ${
                activeTabName === sheet.name || sheet.selected
                  ? 'text-[var(--color-primary)]'
                  : 'text-slate-500'
              }`}
            >
              {sheet.name}
            </span>
          </div>
        ))}
      </div>

      <div className="border border-[var(--color-card-border)] rounded-lg overflow-hidden mb-5">
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="bg-slate-50 border-b border-[var(--color-card-border)]">
                {activeSheet.columns.map((header, idx) => (
                  <th key={idx} className="p-3">
                    <label className="flex items-center gap-2 cursor-pointer group">
                      <input
                        type="checkbox"
                        className="rounded border-slate-300 text-[var(--color-primary)] focus:ring-[var(--color-primary)] cursor-pointer"
                        checked={activeSheet.selectedColumns.includes(header)}
                        onChange={() => toggleColumn(activeSheet.name, header)}
                        disabled={!activeSheet.selected}
                      />
                      <span
                        className={`text-xs font-semibold transition-colors ${
                          !activeSheet.selected
                            ? 'text-slate-400'
                            : 'text-[var(--color-text-primary)] group-hover:text-[var(--color-primary)]'
                        }`}
                      >
                        {header}
                      </span>
                    </label>
                  </th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-[var(--color-card-border)]">
              {activeSheet.data.map((row, rowIdx) => (
                <tr key={rowIdx} className={activeSheet.selected ? 'hover:bg-slate-50' : 'bg-slate-50/50'}>
                  {row.map((cell, cellIdx) => {
                    const header = activeSheet.columns[cellIdx];
                    const isColSelected = header ? activeSheet.selectedColumns.includes(header) : false;
                    return (
                      <td
                        key={cellIdx}
                        className={`p-3 text-xs ${
                          activeSheet.selected && isColSelected
                            ? 'text-[var(--color-text-general)]'
                            : 'text-slate-300'
                        }`}
                      >
                        {cell}
                      </td>
                    );
                  })}
                </tr>
              ))}
              {activeSheet.data.length === 0 && (
                <tr>
                  <td colSpan={activeSheet.columns.length} className="p-4 text-center text-slate-400 text-xs">
                    Nenhum dado encontrado nesta aba
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
        {!activeSheet.selected && (
          <div className="bg-slate-100 text-slate-500 text-xs text-center py-2 border-t border-[var(--color-card-border)]">
            Selecione a aba acima para extrair dados desta planilha
          </div>
        )}
      </div>

      <div className="flex justify-end">
        <button
          className="btn-primary"
          onClick={confirm}
          disabled={totalSelectedColumns === 0}
        >
          Confirmar Seleção Extraída
        </button>
      </div>
    </div>
  );
}
```

- [ ] **Step 2: Run lint**

```
npm run lint --prefix frontend
```

Expected: PASS

- [ ] **Step 3: Commit**

Note: the old `components/DataPreview.tsx` is not yet deleted; it stays as a ghost import until App.tsx is rewritten.

```bash
git add frontend/src/components/datasource/DataPreview.tsx
git commit -m "feat: rewrite DataPreview to read from DataSourceContext"
```

---

### Task 5: Create TemplateSourceProvider and TemplateFileUpload

**Files:**
- Create: `frontend/src/components/templatesource/TemplateSourceProvider.tsx`
- Create: `frontend/src/components/templatesource/TemplateFileUpload.tsx`

- [ ] **Step 1: Create TemplateSourceProvider.tsx**

```typescript
import { createContext, useState, useCallback, type ReactNode } from 'react';
import { use } from 'react';
import type { TemplateSourceContextValue, TemplateSourceState, TemplateSheet } from '../../types';
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
```

- [ ] **Step 2: Create TemplateFileUpload.tsx**

```typescript
import { use } from 'react';
import { TemplateSourceContext } from './TemplateSourceProvider';
import { FileUpload } from '../FileUpload';

export function TemplateFileUpload() {
  const {
    state: { fileName },
    actions: { upload, clear },
  } = use(TemplateSourceContext)!;

  const handleFileSelect = async (name: string | null, file?: File | null) => {
    if (!name || !file) {
      clear();
      return;
    }
    await upload(name, file);
  };

  return (
    <FileUpload
      label="Planilha de Destino (Template)"
      selectedFileName={fileName}
      accept=".xlsx"
      onFileSelect={handleFileSelect}
    />
  );
}
```

- [ ] **Step 3: Run lint**

```
npm run lint --prefix frontend
```

Expected: PASS

- [ ] **Step 4: Commit**

```bash
git add frontend/src/components/templatesource/
git commit -m "feat: add TemplateSourceProvider and TemplateFileUpload wrapper"
```

---

### Task 6: Create shared TemplatePreviewGrid

**Files:**
- Create: `frontend/src/components/templatepreview/TemplatePreviewGrid.tsx`

- [ ] **Step 1: Create TemplatePreviewGrid.tsx — extracted shared grid rendering**

```typescript
import type { TemplateSheet, MappingData } from '../../types';

interface TemplatePreviewGridProps {
  sheets: TemplateSheet[];
  onCellClick?: (cellRef: string) => void;
  mappedCells?: Record<string, MappingData>;
  selectedCell?: string | null;
}

function isMergedCell(coord: string, merged: TemplateSheet['merged']): boolean {
  if (!merged || merged.length === 0) return false;
  const match = /^([A-Z]+)(\d+)$/.exec(coord);
  if (!match) return false;
  const col = match[1];
  const row = parseInt(match[2], 10);
  for (const m of merged) {
    const mr = m as Record<string, unknown>;
    if (
      typeof mr.min_col === 'number' &&
      typeof mr.max_col === 'number' &&
      typeof mr.min_row === 'number' &&
      typeof mr.max_row === 'number'
    ) {
      const colNum = colToInt(col);
      if (
        colNum >= (mr.min_col as number) &&
        colNum <= (mr.max_col as number) &&
        row >= (mr.min_row as number) &&
        row <= (mr.max_row as number)
      ) {
        if (mr.min_col === colNum && mr.min_row === row) return false;
        return true;
      }
    }
  }
  return false;
}

function colToInt(col: string): number {
  let n = 0;
  for (let i = 0; i < col.length; i++) {
    n = n * 26 + (col.charCodeAt(i) - 64);
  }
  return n;
}

function intToCol(n: number): string {
  let s = '';
  while (n > 0) {
    n--;
    s = String.fromCharCode(65 + (n % 26)) + s;
    n = Math.floor(n / 26);
  }
  return s;
}

export function TemplatePreviewGrid({
  sheets,
  onCellClick,
  mappedCells = {},
  selectedCell = null,
}: TemplatePreviewGridProps) {
  const activeSheet = sheets[0];

  if (!activeSheet) {
    return (
      <div className="border border-dashed border-slate-300 rounded-lg p-8 text-center text-slate-400 text-sm">
        Carregue um template para visualizar
      </div>
    );
  }

  const maxRow = Math.max(...activeSheet.cells.map((c) => c.row), 8);
  const maxCol = Math.max(...activeSheet.cells.map((c) => c.col), 6);
  const rows = Array.from({ length: Math.min(maxRow, 50) }, (_, i) => i + 1);
  const cols = Array.from({ length: Math.min(maxCol, 26) }, (_, i) => intToCol(i + 1));

  const cellMap = new Map<string, (typeof activeSheet.cells)[0]>();
  for (const c of activeSheet.cells) {
    cellMap.set(c.coord, c);
  }

  const interactive = !!onCellClick;

  return (
    <div
      className={`overflow-x-auto border border-slate-200 rounded ${
        interactive ? 'bg-white shadow-sm' : ''
      } excel-grid relative`}
    >
      <table className="w-full border-collapse text-xs select-none">
        <thead>
          <tr>
            <th className="w-8 border border-slate-200 bg-slate-100 p-1"></th>
            {cols.map((col) => (
              <th
                key={col}
                className="border border-slate-200 bg-slate-100 font-normal p-1 px-4 text-center text-slate-500"
              >
                {col}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.map((row) => (
            <tr key={row}>
              <td className="border border-slate-200 bg-slate-100 text-center text-slate-500 p-1">
                {row}
              </td>
              {cols.map((col) => {
                const cellRef = `${col}${row}`;
                if (isMergedCell(cellRef, activeSheet.merged)) return null;

                const cellData = cellMap.get(cellRef);
                const mapping = mappedCells[cellRef];
                const isSelected = selectedCell === cellRef;
                const hasValue = cellData?.value;
                const isBold = cellData?.font?.bold;

                return (
                  <td
                    key={cellRef}
                    className={`border border-slate-200 p-2 h-8 relative
                      ${hasValue ? 'font-medium text-slate-700' : ''}
                      ${isBold ? 'font-bold' : ''}
                      ${!hasValue && interactive ? 'cursor-pointer hover:bg-indigo-50' : ''}
                      ${isSelected ? 'ring-2 ring-inset ring-[var(--color-primary)] bg-indigo-50' : ''}
                      ${mapping ? 'bg-indigo-50/70' : ''}
                      transition-all duration-150`}
                    onClick={() => {
                      if (interactive && onCellClick && !hasValue) {
                        onCellClick(cellRef);
                      }
                    }}
                  >
                    <div className="flex items-center justify-between w-full h-full relative z-10">
                      <span className="truncate max-w-[120px]">{cellData?.value ?? ''}</span>
                      {mapping && !hasValue && (
                        <div className="absolute inset-0 flex items-center justify-center p-1">
                          <div
                            className="bg-[var(--color-primary)] text-white text-[9px] px-1.5 py-0.5 rounded shadow-sm cursor-default flex items-center gap-1 w-full justify-center max-w-full overflow-hidden"
                            title={mapping.formatTemplate}
                          >
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
  );
}
```

- [ ] **Step 2: Run lint**

```
npm run lint --prefix frontend
```

Expected: PASS

- [ ] **Step 3: Commit**

```bash
git add frontend/src/components/templatepreview/TemplatePreviewGrid.tsx
git commit -m "feat: extract shared TemplatePreviewGrid from TemplatePreview"
```

---

### Task 7: Create TemplatePreview.ReadOnly and TemplatePreview.Interactive variants

**Files:**
- Create: `frontend/src/components/templatepreview/TemplatePreviewReadOnly.tsx`
- Create: `frontend/src/components/templatepreview/TemplatePreviewInteractive.tsx`

- [ ] **Step 1: Create TemplatePreviewReadOnly.tsx**

```typescript
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
```

- [ ] **Step 2: Create TemplatePreviewInteractive.tsx**

```typescript
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
```

- [ ] **Step 3: Run lint**

```
npm run lint --prefix frontend
```

Expected: PASS — but will fail due to `MappingContext` import from not-yet-created `mapping/MappingProvider.tsx`. Acceptable; will resolve in next task.

- [ ] **Step 4: Commit**

```bash
git add frontend/src/components/templatepreview/TemplatePreviewReadOnly.tsx frontend/src/components/templatepreview/TemplatePreviewInteractive.tsx
git commit -m "feat: create TemplatePreview.ReadOnly and Interactive explicit variants"
```

---

### Task 8: Create MappingProvider

**Files:**
- Create: `frontend/src/components/mapping/MappingProvider.tsx`

- [ ] **Step 1: Create MappingProvider.tsx**

```typescript
import { createContext, useState, useCallback, useRef, useMemo, type ReactNode } from 'react';
import type { MappingContextValue, MappingState, MappingData } from '../../types';
import { DataSourceContext } from '../datasource/DataSourceProvider';

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
      const text = state.formatTemplate;
      const newText = text.substring(0, start) + `{${col}}` + text.substring(start);
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
    const { selectedCell, formatTemplate, mappings } = state;
    if (!selectedCell || !formatTemplate.trim()) return;

    const matches = formatTemplate.match(/\{([^}]+)\}/g);
    const sourceColumns = matches ? [...new Set(matches.map((m) => m.slice(1, -1)))] : [];

    const newMapping: MappingData = {
      id: Math.random().toString(36).substring(2, 11),
      templateCell: selectedCell,
      formatTemplate: formatTemplate.trim(),
      sourceColumns,
    };

    const existingIndex = mappings.findIndex((m) => m.templateCell === selectedCell);
    if (existingIndex >= 0) {
      const newMappings = [...mappings];
      newMappings[existingIndex] = newMapping;
      setState((prev) => ({ ...prev, mappings: newMappings, selectedCell: null, formatTemplate: '' }));
    } else {
      setState((prev) => ({
        ...prev,
        mappings: [...prev.mappings, newMapping],
        selectedCell: null,
        formatTemplate: '',
      }));
    }
  }, [state.selectedCell, state.formatTemplate, state.mappings]);

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
```

Note: `DataSourceContext` is imported but not used inline. It is available for components inside this provider that need `availableColumns` derivation (handled in MappingSection).

- [ ] **Step 2: Run lint**

```
npm run lint --prefix frontend
```

Expected: PASS (unused import warning for DataSourceContext is acceptable; it will be consumed by child components at runtime)

- [ ] **Step 3: Commit**

```bash
git add frontend/src/components/mapping/MappingProvider.tsx
git commit -m "feat: add MappingProvider with state/actions/meta context"
```

---

### Task 9: Rewrite MappingSection to read from MappingContext

**Files:**
- Modify: `frontend/src/components/mapping/MappingSection.tsx` (move and rewrite from `components/MappingSection.tsx`)

- [ ] **Step 1: Create rewritten MappingSection.tsx in mapping/ directory**

```typescript
import { use } from 'react';
import { X, AlertCircle, FileText } from 'lucide-react';
import { MappingContext } from './MappingProvider';
import { DataSourceContext } from '../datasource/DataSourceProvider';
import { TemplatePreviewInteractive } from '../templatepreview/TemplatePreviewInteractive';

function escapeHtml(s: string): string {
  return s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
}

export function MappingSection() {
  const {
    state: { mappings, selectedCell, formatTemplate, listSeparator, listConnector },
    actions: { selectCell, addColumnToFormat, updateFormat, addMapping, removeMapping, setSeparator, setConnector },
    meta: { textareaRef },
  } = use(MappingContext)!;

  const dataSource = use(DataSourceContext);
  const availableColumns = dataSource
    ? dataSource.state.sheets.filter((s) => s.selected).flatMap((s) => s.selectedColumns)
    : ([] as string[]);

  const generatePreview = () => {
    if (!formatTemplate)
      return <span className="text-slate-400 italic">Preview do texto resultante...</span>;

    const escaped = escapeHtml(formatTemplate);
    const previewHtml = escaped.replace(/\{([^}]+)\}/g, (match, col) => {
      if (availableColumns.includes(col)) {
        return `<mark class="bg-indigo-100 text-indigo-800 px-1 rounded not-italic">[Dado de ${col}]</mark>`;
      }
      return match;
    });

    return <span dangerouslySetInnerHTML={{ __html: previewHtml }} />;
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
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
                      <X size={14} />
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
```

- [ ] **Step 2: Run lint**

```
npm run lint --prefix frontend
```

Expected: PASS

- [ ] **Step 3: Commit**

```bash
git add frontend/src/components/mapping/MappingSection.tsx
git commit -m "feat: rewrite MappingSection to read from MappingContext and DataSourceContext"
```

---

### Task 10: Create GenerateFooter

**Files:**
- Create: `frontend/src/components/GenerateFooter.tsx`

- [ ] **Step 1: Create GenerateFooter.tsx**

```typescript
import { useState, use } from 'react';
import { DataSourceContext } from './datasource/DataSourceProvider';
import { TemplateSourceContext } from './templatesource/TemplateSourceProvider';
import { MappingContext } from './mapping/MappingProvider';
import type { GenerateConfig } from '../types';
import { generateReport } from '../services/api';

interface GenerateFooterProps {
  contract: {
    startDate: string;
    prazo: number;
    mes: number;
    ano: number;
  };
}

export function GenerateFooter({ contract }: GenerateFooterProps) {
  const [isGenerating, setIsGenerating] = useState(false);

  const dataSource = use(DataSourceContext);
  const templateSource = use(TemplateSourceContext);
  const mappingCtx = use(MappingContext);

  const isFormComplete =
    dataSource?.state.isComplete &&
    templateSource?.state.isComplete &&
    (mappingCtx?.state.mappings.length ?? 0) > 0;

  const handleGenerate = async () => {
    const sourceFile = dataSource?.state.file;
    const templateFile = templateSource?.state.file;
    if (!sourceFile || !templateFile) {
      alert('Arquivos não carregados. Recarregue a página.');
      return;
    }
    setIsGenerating(true);
    try {
      const config: GenerateConfig = {
        contract: {
          start_date: contract.startDate,
          prazo_dias: contract.prazo,
          mes: contract.mes,
          ano: contract.ano,
        },
        mappings: (mappingCtx?.state.mappings ?? []).map((m) => ({
          formatTemplate: m.formatTemplate,
          templateCell: m.templateCell,
          sourceColumns: m.sourceColumns,
        })),
        listSeparator: mappingCtx?.state.listSeparator ?? ', ',
        listConnector: mappingCtx?.state.listConnector ?? ' e ',
      };

      const blob = await generateReport(sourceFile, templateFile, config);
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `Diario_Consolidado_${String(contract.mes).padStart(2, '0')}_${contract.ano}.xlsx`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    } catch (err) {
      alert((err as Error).message);
    } finally {
      setIsGenerating(false);
    }
  };

  return (
    <footer className="h-20 bg-white border-t border-[var(--color-card-border)] flex items-center px-8 shrink-0 justify-between">
      <div className="flex items-center gap-2">
        <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse"></div>
        <span className="text-[12px] font-semibold text-[var(--color-text-secondary)]">
          {isFormComplete ? 'Pronto para gerar' : 'Aguardando configuração'}
        </span>
      </div>
      <button
        className="btn-primary flex items-center gap-2 shadow-lg shadow-indigo-200 transition-all hover:scale-[1.02] active:scale-[0.98]"
        onClick={handleGenerate}
        disabled={!isFormComplete || isGenerating}
      >
        {!isGenerating && (
          <svg className="w-5 h-5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth="2"
              d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
            ></path>
          </svg>
        )}
        {isGenerating ? (
          <span className="flex items-center gap-2">
            <svg
              className="animate-spin -ml-1 mr-2 h-4 w-4 text-white"
              xmlns="http://www.w3.org/2000/svg"
              fill="none"
              viewBox="0 0 24 24"
            >
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
              <path
                className="opacity-75"
                fill="currentColor"
                d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
              ></path>
            </svg>
            GERANDO...
          </span>
        ) : (
          'GERAR RELATÓRIO XLSX'
        )}
      </button>
    </footer>
  );
}
```

- [ ] **Step 2: Run lint**

```
npm run lint --prefix frontend
```

Expected: PASS

- [ ] **Step 3: Commit**

```bash
git add frontend/src/components/GenerateFooter.tsx
git commit -m "feat: add GenerateFooter reading from 3 contexts"
```

---

### Task 11: Rewrite App.tsx as thin provider composition

**Files:**
- Modify: `frontend/src/App.tsx`

- [ ] **Step 1: Rewrite App.tsx**

```typescript
import { useState } from 'react';
import { Header } from './components/Header';
import { ContractFields } from './components/ContractFields';
import { WizardProvider, WizardContext } from './components/wizard/WizardProvider';
import { Wizard } from './components/wizard/WizardStep';
import { DataSourceProvider } from './components/datasource/DataSourceProvider';
import { SourceFileUpload } from './components/datasource/SourceFileUpload';
import { DataPreview } from './components/datasource/DataPreview';
import { TemplateSourceProvider } from './components/templatesource/TemplateSourceProvider';
import { TemplateFileUpload } from './components/templatesource/TemplateFileUpload';
import { TemplatePreviewReadOnly } from './components/templatepreview/TemplatePreviewReadOnly';
import { MappingProvider } from './components/mapping/MappingProvider';
import { MappingSection } from './components/mapping/MappingSection';
import { GenerateFooter } from './components/GenerateFooter';

export default function App() {
  const [contractStart, setContractStart] = useState('2026-01-01');
  const [contractPrazo, setContractPrazo] = useState(30);
  const [contractMes, setContractMes] = useState(1);
  const [contractAno, setContractAno] = useState(2026);

  const contract = {
    startDate: contractStart,
    prazo: contractPrazo,
    mes: contractMes,
    ano: contractAno,
  };

  return (
    <WizardProvider>
      <DataSourceProvider>
        <TemplateSourceProvider>
          <MappingProvider>
            <div className="h-screen flex flex-col font-sans text-[var(--color-text-primary)] overflow-hidden bg-[var(--color-page-bg)]">
              <Header />

              <main className="flex-1 overflow-y-auto">
                <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 mt-6">
                  <p className="text-slate-500 mb-6 text-sm">
                    Siga os passos abaixo para mapear os dados da sua planilha para o arquivo de template final do RDO.
                  </p>

                  <Wizard.Step step={1} title="1. Dados da Medição">
                    <div className="py-2">
                      <ContractFields
                        startDate={contractStart}
                        prazo={contractPrazo}
                        mes={contractMes}
                        ano={contractAno}
                        onChange={(field, value) => {
                          if (field === 'startDate') setContractStart(value as string);
                          else if (field === 'prazo') setContractPrazo(value as number);
                          else if (field === 'mes') setContractMes(value as number);
                          else if (field === 'ano') setContractAno(value as number);
                        }}
                      />
                      <SourceFileUpload />
                      <ConditionalDataPreview />
                    </div>
                  </Wizard.Step>

                  <Wizard.Step step={2} title="2. Template do Relatório">
                    <div className="py-2">
                      <TemplateFileUpload />
                      <ConditionalTemplatePreview />
                    </div>
                  </Wizard.Step>

                  <Wizard.Step step={3} title="3. Mapeamento de Células">
                    <div className="py-2">
                      <MappingSection />
                    </div>
                  </Wizard.Step>
                </div>
              </main>

              <GenerateFooter contract={contract} />
            </div>
          </MappingProvider>
        </TemplateSourceProvider>
      </DataSourceProvider>
    </WizardProvider>
  );
}

function ConditionalDataPreview() {
  const {
    state: { fileName, isComplete },
  } = use(WizardContext) ? { state: { fileName: null, isComplete: false } } : { state: { fileName: null, isComplete: false } };
  // Simple approach: always render DataPreview; it handles the "no data" state internally.
  // We gate on having a file but not yet complete.
  const dsCtx = use(DataSourceContext);
  if (!dsCtx?.state.fileName || dsCtx.state.isComplete) return null;
  return <DataPreview />;
}

function ConditionalTemplatePreview() {
  const tsCtx = use(TemplateSourceContext);
  if (!tsCtx?.state.fileName || tsCtx.state.isComplete) return null;
  return <TemplatePreviewReadOnly />;
}
```

Wait — the conditional components have issues. `use(WizardContext)` outside a provider would throw. Let me fix this: use `DataSourceContext` and `TemplateSourceContext` respectively:

```typescript
import { useState } from 'react';
import { use } from 'react';
import { Header } from './components/Header';
import { ContractFields } from './components/ContractFields';
import { WizardProvider } from './components/wizard/WizardProvider';
import { Wizard } from './components/wizard/WizardStep';
import { DataSourceProvider, DataSourceContext } from './components/datasource/DataSourceProvider';
import { SourceFileUpload } from './components/datasource/SourceFileUpload';
import { DataPreview } from './components/datasource/DataPreview';
import { TemplateSourceProvider, TemplateSourceContext } from './components/templatesource/TemplateSourceProvider';
import { TemplateFileUpload } from './components/templatesource/TemplateFileUpload';
import { TemplatePreviewReadOnly } from './components/templatepreview/TemplatePreviewReadOnly';
import { MappingProvider } from './components/mapping/MappingProvider';
import { MappingSection } from './components/mapping/MappingSection';
import { GenerateFooter } from './components/GenerateFooter';

export default function App() {
  const [contractStart, setContractStart] = useState('2026-01-01');
  const [contractPrazo, setContractPrazo] = useState(30);
  const [contractMes, setContractMes] = useState(1);
  const [contractAno, setContractAno] = useState(2026);

  const contract = {
    startDate: contractStart,
    prazo: contractPrazo,
    mes: contractMes,
    ano: contractAno,
  };

  return (
    <WizardProvider>
      <DataSourceProvider>
        <TemplateSourceProvider>
          <MappingProvider>
            <div className="h-screen flex flex-col font-sans text-[var(--color-text-primary)] overflow-hidden bg-[var(--color-page-bg)]">
              <Header />

              <main className="flex-1 overflow-y-auto">
                <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 mt-6">
                  <p className="text-slate-500 mb-6 text-sm">
                    Siga os passos abaixo para mapear os dados da sua planilha para o arquivo de template final do RDO.
                  </p>

                  <Wizard.Step step={1} title="1. Dados da Medição">
                    <div className="py-2">
                      <ContractFields
                        startDate={contractStart}
                        prazo={contractPrazo}
                        mes={contractMes}
                        ano={contractAno}
                        onChange={(field, value) => {
                          if (field === 'startDate') setContractStart(value as string);
                          else if (field === 'prazo') setContractPrazo(value as number);
                          else if (field === 'mes') setContractMes(value as number);
                          else if (field === 'ano') setContractAno(value as number);
                        }}
                      />
                      <SourceFileUpload />
                      <ConditionalDataPreview />
                    </div>
                  </Wizard.Step>

                  <Wizard.Step step={2} title="2. Template do Relatório">
                    <div className="py-2">
                      <TemplateFileUpload />
                      <ConditionalTemplatePreview />
                    </div>
                  </Wizard.Step>

                  <Wizard.Step step={3} title="3. Mapeamento de Células">
                    <div className="py-2">
                      <MappingSection />
                    </div>
                  </Wizard.Step>
                </div>
              </main>

              <GenerateFooter contract={contract} />
            </div>
          </MappingProvider>
        </TemplateSourceProvider>
      </DataSourceProvider>
    </WizardProvider>
  );
}

function ConditionalDataPreview() {
  const { state } = use(DataSourceContext)!;
  if (!state.fileName || state.isComplete) return null;
  return <DataPreview />;
}

function ConditionalTemplatePreview() {
  const { state } = use(TemplateSourceContext)!;
  if (!state.fileName || state.isComplete) return null;
  return <TemplatePreviewReadOnly />;
}
```

- [ ] **Step 2: Run lint**

```
npm run lint --prefix frontend
```

Expected: FAIL initially — old files still import from `./components/AccordionSection`, `./components/TemplatePreview`, `./components/DataPreview`, `./components/MappingSection`. These are left as stale imports. Delete the old files next.

- [ ] **Step 3: Commit the App.tsx rewrite**

```bash
git add frontend/src/App.tsx
git commit -m "feat: rewrite App.tsx as thin provider composition (~70 lines)"
```

Note: Lint will fail at this step due to remaining stale imports. That's acceptable — resolved in next task.

---

### Task 12: Delete old files and clean up

**Files:**
- Delete: `frontend/src/components/AccordionSection.tsx`
- Delete: `frontend/src/components/TemplatePreview.tsx`
- Delete: `frontend/src/components/DataPreview.tsx`
- Delete: `frontend/src/components/MappingSection.tsx`

- [ ] **Step 1: Delete old files**

```bash
rm frontend/src/components/AccordionSection.tsx
rm frontend/src/components/TemplatePreview.tsx
rm frontend/src/components/DataPreview.tsx
rm frontend/src/components/MappingSection.tsx
```

- [ ] **Step 2: Run lint**

```
npm run lint --prefix frontend
```

Expected: PASS with zero errors

- [ ] **Step 3: Verify the build**

```
npm run build --prefix frontend
```

Expected: Successful production build with no errors

- [ ] **Step 4: Commit**

```bash
git add frontend/src/components/AccordionSection.tsx frontend/src/components/TemplatePreview.tsx frontend/src/components/DataPreview.tsx frontend/src/components/MappingSection.tsx
git commit -m "refactor: delete old components replaced by composition patterns"
```

---

### Verification Checklist

After all tasks complete, verify:

1. **Lint passes:** `npm run lint --prefix frontend` — zero TypeScript errors
2. **Build succeeds:** `npm run build --prefix frontend` — production bundle created
3. **No boolean props remain** in component APIs that customize behavior
4. **All context reads use `use()`** (React 19), never `useContext()`
5. **No `isInteractive`, `disabled` booleans** — replaced by explicit variants and `Wizard.Step` compound component
6. **App.tsx is under 80 lines** — only provider composition and contract state

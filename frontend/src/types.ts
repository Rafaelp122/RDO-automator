import type { RefObject } from 'react';

export type Sheet = {
  name: string;
  selected: boolean;
  columns: string[];
  selectedColumns: string[];
  data: string[][];
};

export type MappingData = {
  id: string;
  sourceColumns: string[];
  templateCell: string;
  formatTemplate: string;
};

export type AppState = {
  dataUploadDone: boolean;
  templateUploadDone: boolean;
  mappings: MappingData[];
  sheets: Sheet[];
};

export type SourcePreviewResponse = {
  sheets: { name: string; columns: string[]; data: string[][] }[];
  filename: string;
};

export type CellData = {
  coord: string;
  row: number;
  col: number;
  value: string | null;
  font: { bold: boolean | null; size: number | null } | null;
};

export type ImageData = {
  b64: string;
  position: Record<string, number>;
};

export type TemplateSheet = {
  name: string;
  cells: CellData[];
  images: ImageData[];
  merged: Record<string, unknown>[];
};

export type TemplatePreviewResponse = {
  sheets: TemplateSheet[];
};

export type ContractConfig = {
  start_date: string;
  prazo_dias: number;
  mes: number;
  ano: number;
};

export type MappingItem = {
  formatTemplate: string;
  templateCell: string;
  sourceColumns: string[];
};

export type GenerateConfig = {
  contract: ContractConfig;
  mappings: MappingItem[];
  listSeparator: string;
  listConnector: string;
};

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
  textareaRef: RefObject<HTMLTextAreaElement | null>;
}

export interface MappingContextValue {
  state: MappingState;
  actions: MappingActions;
  meta: MappingMeta;
}

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
  font: { bold: boolean; size: number } | null;
};

export type ImageData = {
  b64: string;
  position: Record<string, number>;
};

export type TemplateSheet = {
  name: string;
  cells: CellData[];
  images: ImageData[];
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

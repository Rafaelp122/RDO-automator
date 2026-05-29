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

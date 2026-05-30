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

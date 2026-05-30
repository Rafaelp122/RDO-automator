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

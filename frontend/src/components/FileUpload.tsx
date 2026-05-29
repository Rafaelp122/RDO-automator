import { useRef, useState, useCallback, type DragEvent, type ChangeEvent } from 'react';
import { Upload, FileSpreadsheet } from 'lucide-react';

const MAX_FILE_SIZE = 10 * 1024 * 1024;

interface FileUploadProps {
  label: string;
  onFileSelect: (fileName: string | null, file?: File | null) => void;
  selectedFileName?: string | null;
  accept?: string;
}

export function FileUpload({ label, onFileSelect, selectedFileName, accept = ".xlsx,.xls" }: FileUploadProps) {
  const [isDragActive, setIsDragActive] = useState(false);
  const [dragCounter, setDragCounter] = useState(0);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleDragEnter = useCallback((e: DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragCounter(c => c + 1);
    setIsDragActive(true);
  }, []);

  const handleDragLeave = useCallback((e: DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragCounter(c => {
      const next = c - 1;
      if (next === 0) setIsDragActive(false);
      return next;
    });
  }, []);

  const handleDrop = useCallback((e: DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragCounter(0);
    setIsDragActive(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      handleFile(e.dataTransfer.files[0]);
    }
  }, []);

  const handleFileInput = (e: ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      handleFile(e.target.files[0]);
    }
    e.target.value = "";
  };

  const handleFile = (file: File) => {
    if (file.size > MAX_FILE_SIZE) {
      alert('O arquivo excede o limite de 10MB.');
      return;
    }
    const ext = file.name.split('.').pop()?.toLowerCase();
    if (ext === 'xlsx' || ext === 'xls') {
      onFileSelect(file.name, file);
    } else {
      alert('Por favor, selecione um arquivo Excel (.xlsx ou .xls).');
    }
  };

  const handleBrowseClick = () => {
    fileInputRef.current?.click();
  };

  if (selectedFileName) {
    return (
      <div className="flex items-center justify-between p-4 border bg-[var(--color-input-bg)] border-[var(--color-input-border)] rounded-lg">
        <div className="flex items-center gap-3">
          <FileSpreadsheet className="text-[var(--color-primary)]" size={24} />
          <div>
            <p className="font-medium text-[var(--color-text-primary)]">{selectedFileName}</p>
            <p className="text-[10px] text-[var(--color-text-secondary)]">Arquivo carregado</p>
          </div>
        </div>
        <button 
          className="text-xs text-[var(--color-primary)] hover:underline font-medium"
          onClick={() => onFileSelect(null, null)}
        >
          Trocar arquivo
        </button>
      </div>
    );
  }

  return (
    <div className="w-full">
      <label className="text-label block mb-2">{label}</label>
      <div 
        className={`border-2 border-dashed rounded-lg p-8 flex flex-col items-center justify-center transition-colors
          ${isDragActive ? 'border-[var(--color-primary)] bg-[var(--color-input-bg)]' : 'border-[var(--color-input-border)] hover:bg-slate-50'}
        `}
        onDragEnter={handleDragEnter}
        onDragOver={(e) => { e.preventDefault(); e.stopPropagation(); }}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onClick={handleBrowseClick}
      >
        <Upload className="text-[var(--color-text-muted)] mb-3" size={32} />
        <p className="text-[var(--color-text-primary)] font-medium mb-1">
          Arraste e solte seu arquivo aqui
        </p>
        <p className="text-[var(--color-text-secondary)] mb-4 text-center max-w-[250px]">
          Suporta arquivos .xlsx e .xls até 10MB
        </p>
        
        <button className="bg-[var(--color-btn-browse-bg)] text-[var(--color-btn-browse-text)] px-4 py-2 font-medium hover:bg-slate-300 transition-colors rounded-lg">
          Procurar Arquivo
        </button>
        <input 
          type="file" 
          ref={fileInputRef} 
          className="hidden" 
          accept={accept}
          onChange={handleFileInput}
        />
      </div>
    </div>
  );
}
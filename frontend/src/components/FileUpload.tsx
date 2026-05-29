import React, { useRef, useState } from 'react';
import { Upload, FileSpreadsheet } from 'lucide-react';

interface FileUploadProps {
  label: string;
  onFileSelect: (fileName: string) => void;
  selectedFileName?: string | null;
}

export function FileUpload({ label, onFileSelect, selectedFileName }: FileUploadProps) {
  const [isDragActive, setIsDragActive] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleDragEnter = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragActive(true);
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragActive(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragActive(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      handleFile(e.dataTransfer.files[0]);
    }
  };

  const handleFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      handleFile(e.target.files[0]);
    }
  };

  const handleFile = (file: File) => {
    // Basic validation for prototype
    if (file.name.endsWith('.xlsx') || file.name.endsWith('.xls') || file.name.endsWith('.csv')) {
      onFileSelect(file.name);
    } else {
      alert('Por favor, selecione um arquivo Excel (.xlsx, .xls) ou CSV.');
    }
  };

  const handleBrowseClick = () => {
    fileInputRef.current?.click();
  };

  if (selectedFileName) {
    return (
      <div className="flex items-center justify-between p-4 border rounded-8 bg-[var(--color-input-bg)] border-[var(--color-input-border)] rounded-lg">
        <div className="flex items-center gap-3">
          <FileSpreadsheet className="text-[var(--color-primary)]" size={24} />
          <div>
            <p className="font-medium text-[var(--color-text-primary)]">{selectedFileName}</p>
            <p className="text-[10px] text-[var(--color-text-secondary)]">Arquivo carregado</p>
          </div>
        </div>
        <button 
          className="text-xs text-[var(--color-primary)] hover:underline font-medium"
          onClick={() => onFileSelect('')}
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
        onDragOver={handleDragEnter}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onClick={handleBrowseClick}
      >
        <Upload className="text-[var(--color-text-muted)] mb-3" size={32} />
        <p className="text-[var(--color-text-primary)] font-medium mb-1">
          Arraste e solte seu arquivo aqui
        </p>
        <p className="text-[var(--color-text-secondary)] mb-4 text-center max-w-[250px]">
          Suporta arquivos .xlsx, .xls e .csv até 10MB
        </p>
        
        <button className="bg-[var(--color-btn-browse-bg)] text-[var(--color-btn-browse-text)] px-4 py-2 rounded-8 font-medium hover:bg-slate-300 transition-colors rounded-lg">
          Procurar Arquivo
        </button>
        <input 
          type="file" 
          ref={fileInputRef} 
          className="hidden" 
          accept=".xlsx, .xls, .csv" 
          onChange={handleFileInput}
        />
      </div>
    </div>
  );
}

import React, { useState } from 'react';
import { Header } from './components/Header';
import { AccordionSection } from './components/AccordionSection';
import { FileUpload } from './components/FileUpload';
import { DataPreview } from './components/DataPreview';
import { TemplatePreview } from './components/TemplatePreview';
import { MappingSection } from './components/MappingSection';
import { AppState, Sheet } from './types';
import { motion } from 'motion/react';

const MOCK_SHEETS: Sheet[] = [
  {
    name: "Relatorio_Geral",
    selected: true,
    columns: ["Data", "Equipe", "Atividade", "Quantidade", "Unidade", "Horas", "Observação"],
    selectedColumns: ["Data", "Equipe", "Atividade", "Quantidade"],
    data: [
      ["23/05/2026", "A", "Escavação", "150", "m³", "8", "Terreno rochoso"],
      ["23/05/2026", "B", "Concretagem", "45", "m³", "8", "Pilar P1 a P4"],
      ["24/05/2026", "A", "Armação", "1200", "kg", "8", "Laje L1"],
    ]
  },
  {
    name: "Drenagem",
    selected: false,
    columns: ["Data", "Frente", "Tubulação", "Metragem", "Status"],
    selectedColumns: ["Data", "Frente", "Tubulação", "Status"],
    data: [
      ["24/05/2026", "Sul", "Tubo 600mm", "120", "Concluído"],
    ]
  },
  {
    name: "Elétrica",
    selected: false,
    columns: ["Data", "Poste", "Cabo", "Metragem", "Equipe"],
    selectedColumns: ["Poste", "Cabo"],
    data: [
      ["25/05/2026", "P01", "Cabo 10mm", "50", "C"],
    ]
  }
];

export default function App() {
  const [activeSegment, setActiveSegment] = useState<number>(1);
  const [appState, setAppState] = useState<AppState>({
    dataUploadDone: false,
    templateUploadDone: false,
    mappings: [],
    sheets: MOCK_SHEETS
  });

  const [dataSourceFile, setDataSourceFile] = useState<string | null>(null);
  const [templateFile, setTemplateFile] = useState<string | null>(null);
  const [isGenerating, setIsGenerating] = useState(false);

  const handleGenerate = () => {
    setIsGenerating(true);
    // Simulate generation delay
    setTimeout(() => {
      setIsGenerating(false);
      alert('Relatório gerado com sucesso! O download começará em instantes.');
    }, 2000);
  };

  const isMappingUnlocked = appState.dataUploadDone && appState.templateUploadDone;
  const isFormComplete = isMappingUnlocked && appState.mappings.length > 0;

  // Combine all selected columns from all selected sheets for mapping
  const availableColumns = appState.sheets
    .filter(s => s.selected)
    .flatMap(s => s.selectedColumns);

  return (
    <div className="h-screen flex flex-col font-sans text-[var(--color-text-primary)] overflow-hidden bg-[var(--color-page-bg)]">
      <Header />
      
      <main className="flex-1 overflow-y-auto">
        <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 mt-6">
          <p className="text-slate-500 mb-6 text-sm">
            Siga os passos abaixo para mapear os dados da sua planilha para o arquivo de template final do RDO.
          </p>

        {/* Section 1: Dados da Medição */}
        <AccordionSection 
          title="1. Dados da Medição" 
          stepNumber={1}
          isExpanded={activeSegment === 1}
          isCompleted={appState.dataUploadDone}
          onToggle={() => setActiveSegment(activeSegment === 1 ? 0 : 1)}
        >
          <div className="py-2">
            <FileUpload 
              label="Planilha de Origem" 
              selectedFileName={dataSourceFile}
              onFileSelect={(name) => {
                setDataSourceFile(name || null);
                if (!name) {
                  setAppState(prev => ({ ...prev, dataUploadDone: false }));
                }
              }}
            />
            
            {dataSourceFile && !appState.dataUploadDone && (
              <DataPreview 
                sheets={appState.sheets}
                onSheetsChange={(sheets) => setAppState(prev => ({ ...prev, sheets }))}
                onComplete={() => {
                  setAppState(prev => ({ ...prev, dataUploadDone: true }));
                  setActiveSegment(2); // Auto advance to step 2
                }} 
              />
            )}
          </div>
        </AccordionSection>

        {/* Section 2: Template do Relatório */}
        <AccordionSection 
          title="2. Template do Relatório" 
          stepNumber={2}
          isExpanded={activeSegment === 2}
          isCompleted={appState.templateUploadDone}
          onToggle={() => setActiveSegment(activeSegment === 2 ? 0 : 2)}
        >
          <div className="py-2">
            <FileUpload 
              label="Planilha de Destino (Template)" 
              selectedFileName={templateFile}
              onFileSelect={(name) => {
                setTemplateFile(name || null);
                if (!name) {
                  setAppState(prev => ({ ...prev, templateUploadDone: false }));
                }
              }}
            />
            
            {templateFile && !appState.templateUploadDone && (
              <TemplatePreview 
                onComplete={() => {
                  setAppState(prev => ({ ...prev, templateUploadDone: true }));
                  setActiveSegment(3); // Auto advance to step 3
                }} 
              />
            )}
          </div>
        </AccordionSection>

        {/* Section 3: Mapeamento */}
        <motion.div 
          initial={false}
          animate={{ y: isMappingUnlocked ? 0 : 0 }}
          transition={{ duration: 0.5 }}
        >
          <AccordionSection 
            title="3. Mapeamento de Células" 
            stepNumber={3}
            isExpanded={activeSegment === 3 && isMappingUnlocked}
            isCompleted={appState.mappings.length > 0}
            disabled={!isMappingUnlocked}
            disabledMessage="Conclua os passos 1 e 2 acima para liberar o mapeamento de células"
            onToggle={() => setActiveSegment(activeSegment === 3 ? 0 : 3)}
          >
            <div className="py-2">
              <MappingSection 
                mappings={appState.mappings}
                availableColumns={availableColumns}
                onMappingsChange={(mappings) => setAppState(prev => ({ ...prev, mappings }))}
              />
            </div>
          </AccordionSection>
        </motion.div>
        </div>
      </main>

      {/* Final Action / Footer */}
      <footer className="h-20 bg-white border-t border-[var(--color-card-border)] flex items-center px-8 shrink-0 justify-between">
        <div className="flex items-center gap-2">
          <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse"></div>
          <span className="text-[12px] font-semibold text-[var(--color-text-secondary)]">
            {isFormComplete 
              ? 'Sistema Operacional - Pronto para gerar' 
              : 'Sistema Operacional - Aguardando configuração'}
          </span>
        </div>
        <button 
          className="btn-primary flex items-center gap-2 shadow-lg shadow-indigo-200 transition-all hover:scale-[1.02] active:scale-[0.98]"
          onClick={handleGenerate}
          disabled={!isFormComplete || isGenerating}
        >
          {!isGenerating && (
            <svg className="w-5 h-5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
            </svg>
          )}
          {isGenerating ? (
            <span className="flex items-center gap-2">
              <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              GERANDO...
            </span>
          ) : (
            'GERAR RELATÓRIO PDF/XLSX'
          )}
        </button>
      </footer>
    </div>
  );
}

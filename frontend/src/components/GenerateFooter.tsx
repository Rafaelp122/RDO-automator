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
            <div className="animate-spin -ml-1 mr-2 h-4 w-4">
              <svg
                className="text-white"
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
            </div>
            GERANDO...
          </span>
        ) : (
          'GERAR RELATÓRIO XLSX'
        )}
      </button>
    </footer>
  );
}

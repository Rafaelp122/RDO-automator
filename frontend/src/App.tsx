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

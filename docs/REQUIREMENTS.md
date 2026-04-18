# 📋 Levantamento de Requisitos: Report Automator (Diário de Obra)

## 1. Requisitos Funcionais (RF)

- **RF01 - Carregamento de Configuração:** O sistema deve ler um arquivo externo (TOML) para definir mapeamentos de células, caminhos de arquivos e metadados do projeto.
- **RF02 - Seleção de Arquivos:** O usuário deve ser capaz de selecionar, via interface gráfica, a planilha de dados (origem) e o template (base).
- **RF03 - Processamento de Dados (ETL):** O sistema deve extrair dados de múltiplas abas (Manual, Mecânica, Semafórica, etc.), transformar os textos e consolidá-los por data.
- **RF04 - Formatação de Texto Inteligente:** O sistema deve aplicar regras de capitalização (Title Case), mantendo siglas em caixa alta e preposições em caixa baixa.
- **RF05 - Geração de Abas Diárias:** O sistema deve criar automaticamente uma aba para cada dia do mês dentro do arquivo de saída, baseada no layout do template.
- **RF06 - Mapeamento Dinâmico:** O sistema deve inserir os resumos de cada categoria nas células exatas definidas no arquivo de configuração.
- **RF07 - Exportação em Excel:** O sistema deve gerar um novo arquivo .xlsx preservando todas as formatações, fórmulas e elementos visuais do template original.

## 2. Requisitos Não-Funcionais (RNF)

- **RNF01 - Compatibilidade:** O sistema deve ser distribuído como um executável de arquivo único (.exe) para Windows, sem necessidade de instalação do Python na máquina do usuário.
- **RNF02 - Portabilidade (Build):** O processo de compilação do executável deve ser automatizado via CI/CD (GitHub Actions).
- **RNF03 - Desempenho:** O processamento de um mês completo (30/31 dias) não deve ultrapassar 10 segundos.
- **RNF04 - Interface Intuitiva (UX):** A GUI deve utilizar elementos modernos (PySide6) e fornecer feedback visual (barra de progresso ou log) durante a execução.
- **RNF05 - Extensibilidade:** O código deve seguir uma estrutura modular em camadas para permitir a manutenção isolada da interface, do motor de Excel ou das regras de negócio.

## 3. Regras de Negócio (RN)

- **RN01 - Dias sem Dados:** Caso não existam registros para um determinado dia na planilha de origem, a aba correspondente no diário de obra deve ser gerada, porém os campos de serviço permanecerão vazios.
- **RN02 - Prioridade de Configuração:** As configurações definidas no arquivo config.toml sempre sobrescrevem quaisquer valores padrão do sistema.
- **RN03 - Isenção de Responsabilidade:** O software é uma ferramenta de produtividade "AS IS" (como está), sendo a conferência técnica dos dados de total responsabilidade do usuário final.
- **RN04 - Unicidade de Dados:** Serviços duplicados para o mesmo dia e categoria devem ser agrupados, evitando repetições desnecessárias no relatório final.

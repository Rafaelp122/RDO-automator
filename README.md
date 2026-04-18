# Report Automator: Excel Template Engine

Este projeto é uma ferramenta de automação ETL (Extract, Transform, Load) desenvolvida para otimizar a geração de Diários de Obra. Ele extrai dados brutos de planilhas de medição, processa os textos utilizando lógica de capitalização inteligente e consolida as informações em abas diárias dentro de um template Excel pré-formatado.

O grande diferencial deste projeto é sua arquitetura agnóstica: através de um arquivo de configuração TOML, o usuário pode mapear qualquer coluna de origem para qualquer célula de destino, tornando a ferramenta útil para diversas empresas e setores.

## Funcionalidades

*   **Consolidação Multi-Aba:** Lê dados de diferentes categorias (Manual, Mecânica, Semafórica, etc.) simultaneamente.
*   **Geração de Abas Dinâmicas:** Cria automaticamente uma aba formatada para cada dia do mês (ex: "01-04", "02-04").
*   **Processamento de Linguagem Natural (NLP Básico):**
    *   Correção automática de capitalização (Title Case).
    *   Preservação de siglas técnicas em caixa alta (LED, PCD, BHLS).
    *   Padronização de preposições em caixa baixa.
*   **Configuração via TOML:** Flexibilidade total sem necessidade de alterar o código-fonte.
*   **Interface Gráfica (GUI):** Construída com CustomTkinter para uma experiência moderna no Windows.

## Arquitetura do Projeto

O projeto segue uma estrutura de **Arquitetura em Camadas (Layered Architecture)**, garantindo a separação de responsabilidades para facilitar a manutenção:

*   **Core:** Camada de domínio contendo a lógica de negócio pura (processamento de texto e regras de formatação), sem dependências externas de I/O.
*   **Infra:** Camada de infraestrutura responsável pela comunicação com o mundo externo (leitura/escrita de arquivos Excel e gerenciamento de configurações).
*   **UI:** Camada de apresentação que gerencia a interface visual e a interação com o usuário.


## Tecnologias Utilizadas

| Tecnologia | Finalidade |
| :--- | :--- |
| Python 3.11+ | Linguagem principal |
| Pandas | Manipulação e análise de dados brutos |
| Openpyxl | Manipulação de templates e preservação de estilos Excel |
| PySide6 | Interface gráfica nativa e moderna |
| TOML | Gerenciamento de configurações e mapeamento |
| PyInstaller | Empacotamento para executável Windows (.exe) |
| GitHub Actions | CI/CD para build automatizado do binário |

## Como Utilizar

1.  **Prepare o ambiente:** Mantenha o executável, o arquivo `config.toml` e seu `template.xlsx` na mesma pasta.
2.  **Configure o TOML:** Abra o arquivo de configuração e defina quais colunas da sua medição devem ser enviadas para quais células do diário.
3.  **Execute o App:** Abra o `GeradorDiario.exe`, selecione o mês/ano e clique em **Gerar**.
4.  **Resultado:** Um novo arquivo consolidado será gerado com uma aba para cada dia do mês perfeitamente preenchida.

## Licença e Isenção de Responsabilidade

Este software é distribuído sob a Licença MIT.

### Disclaimer (Aviso Legal)

*   **ESTE SOFTWARE É FORNECIDO "COMO ESTÁ" (AS IS)**, sem garantias de qualquer tipo, expressas ou implícitas.
*   O autor não se responsabiliza pela integridade, veracidade ou precisão dos dados inseridos no relatório final.
*   A conferência técnica dos dados e a conformidade com as normas de engenharia são de responsabilidade exclusiva do usuário final.
*   Em nenhum caso o autor será responsável por quaisquer danos decorrentes do uso desta ferramenta.

## Autor

**Rafael Araújo**
Estudante de Análise e Desenvolvimento de Sistemas (ADS) e Técnico em Desenvolvimento de Sistemas.
Focado em backend Python, arquitetura de software e automação de processos.
.

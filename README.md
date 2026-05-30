# RDO Automator — Gerador de Diários de Obra

Aplicação web que transforma planilhas de medição de obras em diários
consolidados formatados em Excel.

**Pipeline ETL**: faz upload de uma planilha de dados de origem e de um
template, mapeia colunas para células do template via interface visual e
gera um arquivo Excel com uma aba para cada dia do mês, preenchida com
os dados formatados.

<sub>**Aviso:** Esta é a versão 2.0 (web), que substituiu a versão
desktop 1.x (PySide6 + config TOML).</sub>

---

## Como funciona

```
Origem (.xlsx) ──┐                    ┌── Preview (abas + colunas)
                  ├── ETL pipeline ────┤
Template (.xlsx)─┘                    └── Diário consolidado (.xlsx)
                        ▲
                   Config JSON
            (contrato + mapeamentos)
```

1. **Upload** — envia a planilha de origem (.xlsx/.xls) e o template (.xlsx)
2. **Preview** — visualiza abas, colunas e células para selecionar o que extrair
3. **Mapeamento** — define templates de texto com placeholders `{Coluna}` e
   vinculação a células do template
4. **Geração** — para cada dia do mês, o sistema clona o template, filtra os
   dados de origem por data e preenche as células mapeadas com o texto
   formatado (capitalização inteligente, pluralização, conectores)

## Funcionalidades

- **Leitura multi-aba** — processa múltiplas abas da planilha de origem
- **Detecção automática de data** — identifica colunas que contêm "data"
  no nome e normaliza os valores
- **Mapeamento visual** — seleção de colunas de origem e células de
  destino via interface gráfica, sem editar arquivos de configuração
- **Template de texto dinâmico** — suporte a placeholders `{Coluna}`,
  pluralização `{Coluna:s}`, `{Coluna:es}`, `{Coluna:nos}` e
  conectores configuráveis
- **Formatação inteligente de texto** — Title Case automático,
  preservação de siglas técnicas (LED, PCD, BHLS), preposições em
  caixa baixa
- **Geração por dia** — uma aba por dia do mês (`01-04`, `02-04`, …)
- **Preview interativo do template** — visualização de células, fontes,
  imagens e regiões mescladas do arquivo de template
- **Tratamento de imagens** — extrai e reinsere imagens do template
  em cada aba clonada

## Tecnologias

### Backend (API)

| Tecnologia | Função |
|---|---|
| Python 3.14 | Linguagem |
| FastAPI | Framework web assíncrono |
| Uvicorn | Servidor ASGI |
| Pandas | Leitura e manipulação de DataFrames |
| Openpyxl | Leitura/escrita de arquivos Excel preservando estilos |
| Pydantic v2 | Validação de schemas de entrada/saída |
| Pillow | Suporte a imagens nos templates Excel |

### Frontend (SPA)

| Tecnologia | Função |
|---|---|
| React 19 | Biblioteca de componentes |
| TypeScript 5.8 | Tipagem estática |
| Vite 6 | Bundler e dev server |
| Tailwind CSS 4 | Estilização utilitária |
| Lucide React | Ícones |
| Motion | Animações |

### Infraestrutura

| Ferramenta | Função |
|---|---|
| uv | Gerenciador de pacotes Python |
| Docker | Containerização do backend |
| Google Cloud Run | Deploy serverless do backend |
| Vercel | Deploy do frontend |
| GitHub Actions | CI/CD (deploy automático no push para master) |
| Pytest | Testes unitários e de integração |

## Estrutura do projeto

```
report_automator/
├── backend/
│   ├── src/
│   │   ├── main.py              # FastAPI app factory + middleware + CORS + handlers
│   │   ├── routes.py             # Rotas HTTP (preview + generate)
│   │   ├── schemas.py            # Modelos Pydantic (request/response)
│   │   ├── config.py             # Configuração centralizada (Settings)
│   │   ├── exceptions.py         # Exceções de domínio (AppError e subclasses)
│   │   ├── logger.py             # Configuração de logging (console + arquivo)
│   │   └── excel/
│   │       ├── __init__.py
│   │       ├── source.py         # ExcelLoader — extração de dados da origem
│   │       ├── template.py       # TemplateManager — manipulação do template
│   │       ├── report.py         # ReportGenerator — geração do relatório consolidado
│   │       └── processor.py      # TextProcessor — formatação de texto (Title Case)
│   ├── pyproject.toml
│   ├── Dockerfile
│   └── uv.lock
├── frontend/
│   ├── src/
│   │   ├── App.tsx               # Estado global + integração com API
│   │   ├── types.ts              # Tipos TypeScript (espelho dos schemas Pydantic)
│   │   ├── services/
│   │   │   └── api.ts            # Cliente HTTP para a API
│   │   └── components/
│   │       ├── AccordionSection.tsx
│   │       ├── ContractFields.tsx
│   │       ├── DataPreview.tsx
│   │       ├── FileUpload.tsx
│   │       ├── Header.tsx
│   │       ├── MappingSection.tsx
│   │       └── TemplatePreview.tsx
│   ├── index.html
│   ├── package.json
│   ├── vite.config.ts
│   └── tsconfig.json
├── tests/
│   ├── unit/                     # Testes de unidade (ETL, processamento)
│   └── integration/              # Testes de integração (API + fluxo completo)
└── .github/
    └── workflows/                 # CI/CD (deploy-backend.yml, deploy-frontend.yml)
```

## API

Todas as rotas estão sob o prefixo `/api`.

| Método | Rota | Descrição |
|---|---|---|
| `POST` | `/api/preview/source` | Preview da planilha de origem (abas, colunas, dados) |
| `POST` | `/api/preview/template` | Preview do template (células, imagens, merges) |
| `POST` | `/api/generate` | Geração do relatório consolidado |
| `GET`  | `/health` | Health check |

### Exemplo: POST /api/preview/source

**Request:** `multipart/form-data` com campo `file` (.xlsx ou .xls)

**Response:**
```json
{
  "sheets": [
    {
      "name": "Obras",
      "columns": ["Data", "Servico", "Bairro"],
      "data": [["2026-01-05", "Pintura", "Centro"], ...]
    }
  ],
  "filename": "medicao.xlsx"
}
```

### Exemplo: POST /api/generate

**Request:** `multipart/form-data` com campos `source`, `template` e `config` (JSON string)

```json
{
  "contract": {
    "start_date": "2026-01-01",
    "prazo_dias": 180,
    "mes": 1,
    "ano": 2026
  },
  "mappings": [
    {
      "formatTemplate": "Servicos Realizados: {Servico}. No Bairro: {Bairro}",
      "templateCell": "B3",
      "sourceColumns": ["Servico", "Bairro"]
    }
  ],
  "listSeparator": ", ",
  "listConnector": " e "
}
```

**Response:** `application/vnd.openxmlformats-officedocument.spreadsheetml.sheet`
(StreamingResponse com download `Diario_Consolidado.xlsx`)

### Erros

Todas as exceções de domínio são capturadas por um handler global e
retornadas como:

```json
{
  "detail": "Arquivo de origem deve ser .xlsx ou .xls",
  "code": "invalid_file_extension",
  "errors": []
}
```

| Código | Significado |
|---|---|
| `invalid_file_extension` | Extensão do arquivo não suportada |
| `invalid_config` | JSON de configuração malformado |
| `report_generation_error` | Falha interna na geração (500) |

## Como executar

### Backend

```bash
cd backend
uv sync
uv run uvicorn src.main:app --reload --port 8000
```

A API fica disponível em `http://localhost:8000`.
Documentação interativa (Swagger) em `http://localhost:8000/docs`.

### Frontend

```bash
cd frontend
npm install
npm run dev
```

O dev server inicia em `http://localhost:3000` e faz proxy das chamadas
de API para `http://localhost:8000` (configurável via `.env`).

### Docker

```bash
cd backend
docker build -t rdo-automator .
docker run -p 8080:8080 rdo-automator
```

## Configuração

O backend utiliza variáveis de ambiente, centralizadas em
`backend/src/config.py`:

| Variável | Padrão | Descrição |
|---|---|---|
| `ALLOWED_ORIGINS` | `http://localhost:3000,http://localhost:5173,https://rdo.vercel.app` | Origens CORS permitidas |
| `MAX_UPLOAD_MB` | `50` | Tamanho máximo de upload |
| `LOG_LEVEL` | `INFO` | Nível de logging |
| `LOG_PATH` | `/tmp/rdo_automator.log` | Caminho do arquivo de log |

O frontend usa `.env` para configurar a URL da API:

```
VITE_API_URL=http://localhost:8000
```

## Testes

```bash
cd backend
uv run pytest ../tests/
```

25 testes cobrindo:

- **Unidade** — text processor (capitalização, pluralização), Excel loader
  (detecção de data), template manager (clonagem de abas)
- **Integração** — endpoints da API (upload, preview, geração),
  fluxo E2E completo (upload → generate → validação do xlsx gerado)

## Deploy

CI/CD configurado via GitHub Actions no push para `master`:

| Pipeline | Gatilho | Destino |
|---|---|---|
| `deploy-backend.yml` | Alterações em `backend/**` | Google Cloud Run |
| `deploy-frontend.yml` | Alterações em `frontend/**` | Vercel |

Secrets necessários:
- Backend: `GCP_SA_KEY`, `GCP_PROJECT_ID`
- Frontend: `VERCEL_TOKEN`, `VERCEL_ORG_ID`, `VERCEL_PROJECT_ID`

## Pipeline ETL (visão interna)

```
ExcelLoader.load_all_sheets()
    ├── pandas.read_excel()          → Extrai todas as abas
    ├── _find_date_column()          → Detecta coluna de data
    └── _normalize_dates()           → Converte datas + cria _dia_aux

TemplateManager
    ├── load()                       → Abre workbook, extrai imagens
    ├── clone_worksheet("01-04")     → Duplica template com título de data
    └── save_to_stream()             → Serializa workbook final

ReportGenerator.generate()
    ├── _validate_filenames()        → Checa .xlsx/.xls
    ├── _parse_configuration()       → JSON → Pydantic → dict
    ├── _load_source_data()          → ExcelLoader
    ├── _load_template()             → TemplateManager
    ├── _build_daily_sheets()        → Loop 1..último_dia
    │   ├── template.clone_worksheet("01-04")
    │   └── _fill_worksheet_cell()
    │       ├── _extract_column_values()   → Filtra por dia, limpa NaN
    │       └── TextProcessor.formatar_resumo() → Formata texto final
    └── _write_output()              → BytesIO
```

## Licença

MIT.

### Aviso legal

Este software é fornecido "como está" (AS IS), sem garantias de qualquer
tipo, expressas ou implícitas. A conferência técnica dos dados e a
conformidade com as normas de engenharia são de responsabilidade
exclusiva do usuário final.

## Autor

**Rafael Araújo** — Estudante de Análise e Desenvolvimento de Sistemas,
focado em backend Python, arquitetura de software e automação de
processos.

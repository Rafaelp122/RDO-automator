# Design Doc: Migração Web — PyQt6 → FastAPI + React

**Data:** 2026-05-28
**Status:** Aprovado

---

## 1. Visão Geral

Migração do RDO Automator de aplicação desktop (PyQt6/PySide6) para aplicação web (FastAPI + React), com deploy desacoplado: backend no Google Cloud Run (serverless) e frontend na Vercel (CDN estático). Eliminação do arquivo de configuração TOML — substituído por interação visual completa no navegador.

### 1.1 Objetivos

- Zero instalação — usuário acessa via URL
- Atualizações automáticas (deploy = todos recebem)
- Portfólio interativo (URL pública)
- Tecnologia alinhada ao mercado (React, FastAPI, Cloud Run)
- Reaproveitar 100% da engine Python existente

### 1.2 O que muda

| Antes | Depois |
|---|---|
| PySide6 (desktop) | React Vite (navegador) |
| TOML config manual | Interação visual (cliques, preview, mapeamento) |
| PyInstaller .exe | Cloud Run + Vercel |
| Atualização manual (download) | Deploy contínuo |
| Acesso local | Qualquer navegador |
| 1 codebase monolítica | 2 codebases (backend + frontend) |

---

## 2. ADRs

### 2.1 ADR-001: Escolha original de PyQt6

**Contexto:** Ferramenta de uso pessoal/equipe pequena para automatização de Diários de Obra.

**Decisão:** PyQt6 (PySide6) como framework de UI desktop.

**Justificativa:**
- Engine de processamento (openpyxl + pandas) é Python nativa
- Mesma linguagem front e back — zero overhead
- Acesso direto ao filesystem
- Empacotamento único via PyInstaller
- Iteração rápida: 1 pessoa, 1 linguagem

**Trade-offs aceitos:** usuário precisa baixar .exe, atualizações manuais, sem acesso remoto, sem portfólio.

### 2.2 ADR-002: Migração para FastAPI + React

**Contexto:** Evolução para aplicação web com deploy serverless.

**Decisão:** FastAPI (backend Python) + React Vite (frontend).

**Justificativa:**
- 100% da engine Python reaproveitada (core/infra copiados com adaptações mínimas)
- FastAPI assíncrono — concorrência nativa
- React padrão de mercado para SPAs interativas
- Deploy desacoplado: Cloud Run (escala a zero) + Vercel (CDN grátis)
- Atualizações automáticas
- Elimina TOML — UI visual substitui configuração manual

**Alternativas rejeitadas:**
- Next.js fullstack → SSR desnecessário para app de formulário
- Tudo no Vercel → timeout insuficiente (10-60s vs 30-60s de processamento Excel)
- Manter PyQt → não resolve os problemas de distribuição e portfólio

**Trade-offs aceitos:** latência de rede, limites de request size no Cloud Run, complexidade de dois deploys (mitigada por CI/CD), sem acesso offline.

---

## 3. Arquitetura

### 3.1 Estrutura do Projeto

```
report_automator/
├── backend/                          # FastAPI (Cloud Run)
│   ├── main.py                       # App, CORS, lifespan
│   ├── routers/
│   │   ├── preview.py                # POST /api/preview/source
│   │   └── generate.py               # POST /api/preview/template
│   │                                 # POST /api/generate
│   ├── models/
│   │   └── api_models.py             # Pydantic: PreviewResponse, GenerateRequest
│   ├── services/
│   │   ├── preview_service.py        # Serializa Excel → JSON
│   │   ├── report_service.py         # ← COPIADO/ADAPTADO
│   │   └── report_builder.py         # ← COPIADO/ADAPTADO
│   ├── utils/
│   │   ├── processor.py              # ← COPIADO (zero mudança)
│   │   ├── validator.py              # ← COPIADO
│   │   ├── excel_loader.py           # ← ADAPTADO (BytesIO)
│   │   ├── template_manager.py       # ← ADAPTADO (BytesIO)
│   │   └── logger.py                 # ← COPIADO
│   └── Dockerfile
│
├── frontend/                         # React Vite (Vercel)
│   ├── src/
│   │   ├── components/
│   │   │   ├── Header.tsx
│   │   │   ├── FileUpload.tsx
│   │   │   ├── AccordionSection.tsx
│   │   │   ├── DataPreview.tsx
│   │   │   ├── TemplatePreview.tsx
│   │   │   └── MappingSection.tsx
│   │   ├── services/
│   │   │   └── api.ts
│   │   ├── hooks/
│   │   │   └── useGenerate.ts
│   │   ├── App.tsx
│   │   └── types.ts
│   └── vite.config.ts
│
├── src/app/                          # Código PyQt original (mantido como referência)
│   ├── core/                         # → copiado/adaptado para backend
│   ├── infra/                        # → copiado/adaptado para backend
│   └── ui/                           # → DESCARTADO
│
└── docs/superpowers/specs/
```

### 3.2 Reaproveitamento de Código

| Original | Destino | Ação |
|---|---|---|
| `core/processor.py` | `backend/utils/` | Copiado (zero mudança) |
| `core/validator.py` | `backend/utils/` | Copiado |
| `core/report_service.py` | `backend/services/` | Adaptado: BytesIO em vez de paths |
| `core/report_builder.py` | `backend/services/` | Adaptado: DataFrames em memória |
| `core/logger.py` | `backend/utils/` | Copiado |
| `infra/excel_loader.py` | `backend/utils/` | Adaptado: `pd.read_excel(BytesIO)` |
| `infra/template_manager.py` | `backend/utils/` | Adaptado: `load_workbook(BytesIO)` |
| `core/config_models.py` | — | Obsoleto (TOML removido) |
| `core/constants.py` | — | Obsoleto (paths desktop) |
| `infra/config_manager.py` | — | Obsoleto (sem TOML) |
| `ui/` (PySide6) | — | Substituído por React |

### 3.3 Fluxo de Dados

```
Browser (React)
  │
  ├── POST /api/preview/source
  │    multipart: source.xlsx
  │    → FastAPI → excel_loader → JSON {sheets, columns, data}
  │
  ├── POST /api/preview/template
  │    multipart: template.xlsx
  │    → FastAPI → template_manager → JSON {cells, images, merged}
  │
  └── POST /api/generate
       multipart: source.xlsx + template.xlsx
       json field: {mappings, contract, listSeparator, listConnector}
       → FastAPI → report_service + report_builder
       → StreamingResponse (.xlsx download)
```

---

## 4. Endpoints da API

### 4.1 POST /api/preview/source

```
Request:  multipart/form-data { file: .xlsx }
Response: {
  sheets: [{
    name: string,
    selected: bool,
    columns: string[],
    selectedColumns: string[],
    data: string[][]
  }],
  filename: string
}
```

### 4.2 POST /api/preview/template

```
Request:  multipart/form-data { file: .xlsx }
Response: {
  sheets: [{
    name: string,
    cells: [{ coord, row, col, value, font }],
    images: [{ b64, position }],
    merged: [{ start, end }]
  }]
}
```

### 4.3 POST /api/generate

```
Request:  multipart/form-data {
  source: .xlsx,
  template: .xlsx,
  config: JSON string {
    contract: {
      start_date: "YYYY-MM-DD",
      prazo_dias: int,
      mes: int,
      ano: int
    },
    mappings: [{
      formatTemplate: "Servicos: {Atividade} no {Bairro}",
      templateCell: "B3",
      sourceColumns: ["Atividade", "Bairro"]
    }],
    listSeparator: ", ",
    listConnector: " e "
  }
}
Response: application/vnd.openxmlformats-officedocument.spreadsheetml.sheet
```

---

## 5. Componentes React

### 5.1 Arvore de Componentes

```
App
├── Header                     # "RDO Automator v2.0"
├── Main (scroll)
│   ├── AccordionSection (1)   # "1. Dados da Medicao"
│   │   ├── ContractFields     # data inicio, prazo, mes, ano
│   │   ├── FileUpload         # source.xlsx
│   │   └── DataPreview        # tabs das abas + selecao colunas
│   │
│   ├── AccordionSection (2)   # "2. Template do Relatorio"
│   │   ├── FileUpload         # template.xlsx
│   │   └── TemplatePreview    # grade + imagens (nao-interativo)
│   │
│   └── AccordionSection (3)   # "3. Mapeamento de Celulas"
│       └── MappingSection
│           ├── [esquerda]
│           │   ├── Chips de colunas
│           │   ├── Textarea formato
│           │   ├── Separador/Conector
│           │   └── Indicador celula destino
│           └── [direita]
│               └── TemplatePreview interativo
│
└── Footer                     # status + "GERAR RELATORIO"
```

### 5.2 Estados por Componente

| Componente | Estados |
|---|---|
| AccordionSection | collapsed, expanded, disabled (lock), completed (check) |
| FileUpload | empty, loaded, dragover |
| DataPreview | loading, ready (tabs+tabela), error |
| TemplatePreview | loading, ready, interactive |
| ContractFields | empty, filled |
| MappingSection | idle: selecionando colunas, escrevendo formato, aguardando celula |
| App (geracao) | idle, generating (spinner), done (download), error |

### 5.3 Servico de API (`api.ts`)

```ts
interface ApiService {
  previewSource(file: File): Promise<SourcePreviewResponse>
  previewTemplate(file: File): Promise<TemplatePreviewResponse>
  generate(
    source: File,
    template: File,
    config: GenerateConfig
  ): Promise<Blob>
}
```

---

## 6. Funcionalidades

### 6.1 Upload + Preview da Planilha de Medicao
- Drag & drop ou browse de arquivo .xlsx/.xls/.csv
- Backend serializa estrutura para JSON
- Frontend renderiza tabs horizontais (uma por aba)
- Checkbox para selecionar/desselecionar abas
- Tabela com checkbox por coluna
- Badge: "N abas selecionadas · M colunas"
- Colunas nao selecionadas aparecem em cinza claro

### 6.2 Dados do Contrato
- Inline na secao 1: data de inicio, prazo (dias), mes, ano
- Inputs compactos, mesma estetica do restante
- Enviados como `contract` no JSON config da geracao

### 6.3 Upload + Preview do Template
- Drag & drop ou browse do arquivo template .xlsx
- Backend serializa celulas + imagens base64 + merged cells
- Frontend renderiza grade fiel ao layout Excel
- Imagens posicionadas absolutamente sobre a grade
- Sem interacao de clique nesta etapa (so visualizacao)

### 6.4 Template de Formato do Texto
- Textarea com placeholder: `"Servicos Realizados: {Atividade}. No Bairro: {Bairro}"`
- Chips de colunas ao clicar insere `{col}` no cursor
- Preview dinamico mostrando resultado com mock data
- Separador de lista (default: `, `) e conector final (default: ` e `)
- Exemplo: 3 atividades → `"Pintura, Concretagem e Escavacao"`

### 6.5 Mapeamento Visual (celula → formato)
- Layout 2 colunas: formulario (esquerda) + template interativo (direita)
- Fluxo: seleciona colunas → escreve formato → clica na celula → confirma
- Cada mapeamento salvo mostra: chips das colunas, formato truncado, badge da celula
- Celulas mapeadas no template mostram badge com icone Type
- Substituicao: clicar em celula ja mapeada sobrescreve

### 6.6 Geracao do Relatorio
- Botao "GERAR RELATORIO" desabilitado ate secoes 1, 2 e 3 concluidas
- Spinner durante processamento
- Download automatico do .xlsx ao concluir
- Feedback de erro com mensagem clara

### 6.7 Secao 3 Bloqueada
- Sempre visivel, nunca escondida
- Estado inicial: icone Lock, opacidade 50%, titulo "(Bloqueado)"
- Ao tentar expandir bloqueada: nao expande
- Libera automaticamente quando dataUploadDone E templateUploadDone
- Transicao suave bloqueado → liberado

---

## 7. Deploy

### 7.1 Backend — Cloud Run

```dockerfile
FROM python:3.14-slim
WORKDIR /app
COPY backend/ .
RUN pip install uv && uv sync --frozen --no-dev
CMD ["uv", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
```

**Configuracao:**
- Memoria: 512MB (openpyxl + pandas)
- Timeout: 60min
- CPU: 1 vCPU
- Max instances: 1
- Min instances: 0 (escala a zero)

### 7.2 Frontend — Vercel

```
Root: frontend/
Framework: Vite
Build: npm run build
Output: dist/
```

**Variaveis de ambiente:**
- `VITE_API_URL=https://api-xxx.a.run.app`
- `CORS_ORIGINS=https://rdo.vercel.app` (backend)

### 7.3 CI/CD (GitHub Actions)

```yaml
backend:
  on push main, paths: backend/**
  - gcloud builds submit --tag gcr.io/...
  - gcloud run deploy

frontend:
  on push main, paths: frontend/**
  - vercel deploy --prod
```

### 7.4 Custos

| Recurso | Mensal |
|---|---|
| Cloud Run (~30 geracoes/mes) | ~$0.50 |
| Vercel Hobby | $0 |
| Artifact Registry | $0 (free tier) |
| **Total** | **~$0.50** |

---

## 8. Esquema de Cores e Tipografia

### Paleta de Cores

| Token | Valor | Uso |
|---|---|---|
| `--color-page-bg` | `#F7F9FC` | Fundo da pagina |
| `--color-card-bg` | `#FFFFFF` | Cards/containers |
| `--color-card-border` | `#E0E6ED` | Bordas de card |
| `--color-primary` | `#3F51B5` | Cor principal (indigo) |
| `--color-primary-hover` | `#303F9F` | Hover |
| `--color-primary-pressed` | `#1A237E` | Pressed |
| `--color-text-primary` | `#1E293B` | Texto principal |
| `--color-text-secondary` | `#5E6C84` | Texto secundario |
| `--color-text-muted` | `#94A3B8` | Texto muted |
| `--color-input-bg` | `#F1F5F9` | Fundo de input |
| `--color-input-border` | `#CBD5E1` | Borda de input |
| `--color-error-base` | `#D32F2F` | Borda de erro |
| `--color-error-bg` | `#FFEBEE` | Fundo de erro |

### Tipografia
- Fonte: Inter (sans), JetBrains Mono (mono/log)
- Titulo: 22px bold (header)
- Titulo de secao: 14px bold, cor #3F51B5
- Rotulo de campo: 11px bold, cor #5E6C84
- Texto geral: 12px, cor #334155

### Bordas e Cantos
- Cards: border-radius 12px
- Inputs: border-radius 8px
- Botao primario: border-radius 22px, altura 44px
- Botao secundario: border-radius 8px
- Chips: border-radius 12px

# RDO Automator v2.0 — Requisitos e Regras de Negócio

## 1. Domínio

**RDO** (Relatório Diário de Obra) é um documento exigido em contratos de
construção civil. Cada dia do mês preenche uma aba com:
- Data, condições climáticas, efetivo
- Serviços realizados (atividades, bairros, quantidades)
- Ocorrências e observações

Os dados brutos vêm de uma **planilha de medição** (fonte) com colunas como
`Data`, `Atividade`, `Bairro`, `Quantidade`. O **template** é um arquivo Excel
pré-formatado com células que recebem os valores extraídos.

O RDO Automator **automatiza** esse preenchimento: o usuário faz upload da fonte
e do template, mapeia colunas para células, e gera o relatório consolidado com
uma aba por dia.

---

## 2. Requisitos Funcionais

### RF01 — Upload da planilha de origem
- Aceita `.xlsx` e `.xls`
- Limite: 10 MB
- Suporta múltiplas abas
- Exibe preview das primeiras 20 linhas de cada aba

### RF02 — Seleção de abas e colunas
- Checkbox para ativar/desativar cada aba
- Checkbox para ativar/desativar cada coluna dentro da aba ativa
- Somente colunas marcadas ficam disponíveis para mapeamento

### RF03 — Contrato (período)
- Data de início, prazo em dias, mês e ano do relatório
- Determina quantos dias serão gerados (1 a 31, conforme `calendar.monthrange`)

### RF04 — Upload do template
- Aceita `.xlsx`
- Limite: 10 MB
- Exibe preview visual das células (grade estilo Excel)
- Mostra células mescladas e formatação (negrito)

### RF05 — Mapeamento de colunas para células
- Cada mapeamento define:
  - **Formato:** template de texto com placeholders `{Coluna}` (ex: `{Atividade} no {Bairro}`)
  - **Célula destino:** coordenada Excel (ex: `B14`) selecionada na grade interativa
  - **Colunas fonte:** nomes extraídos dos `{}` no formato
- Múltiplos mapeamentos por template
- Preview ao vivo do texto formatado

### RF06 — Geração do relatório
- Para cada dia do mês, clona a aba do template e preenche as células mapeadas
- Cada `{Coluna}` é substituída pelos valores daquela coluna no dia corrente
- Múltiplos valores são unidos com separador (`, `) e conector final (` e `)
- Download como `.xlsx` com nome `Diario_Consolidado_MM_AAAA.xlsx`

### RF07 — Detecção de siglas
- Varredura automática de palavras em CAIXA ALTA com 2-4 caracteres
- Sugestões expostas para o frontend (campo não implementado na UI atual)

---

## 3. Fluxo de Uso

```
[Passo 1] Dados da Medição
  ├── Preenche período do contrato (data início, prazo, mês, ano)
  ├── Upload da planilha de origem (.xlsx/.xls)
  ├── Preview das abas e colunas
  └── Confirma seleção → avança para passo 2

[Passo 2] Template do Relatório
  ├── Upload do arquivo template (.xlsx)
  ├── Preview visual das células
  └── Confirma template → avança para passo 3

[Passo 3] Mapeamento de Células
  ├── Seleciona colunas disponíveis (chips com +)
  ├── Escreve formato com {Coluna}
  ├── Clica na célula destino na grade interativa
  ├── Confirma mapeamento
  └── Repete para cada célula a preencher

[Rodapé] GERAR RELATÓRIO XLSX
  └── Download do arquivo gerado
```

---

## 4. Regras de Negócio

### 4.1 Template de formatação

Placeholders `{NomeDaColuna}` são substituídos pelos valores extraídos.

```
Formato: "{Atividade} — {Bairro}"
Dados:   Atividade=["Escavação", "Concretagem"], Bairro=["Centro"]
Resultado: "Escavação, Concretagem — Centro"
```

### 4.2 Junção de múltiplos valores

Quando uma coluna tem mais de um valor no mesmo dia:
- Valores são unidos com **separador de lista** (padrão: `, `)
- O último par usa o **conector final** (padrão: ` e `)

```
Dados: Atividade=["Escavação", "Concretagem", "Pintura"]
Separador: ", "
Conector: " e "
Resultado: "Escavação, Concretagem e Pintura"
```

### 4.3 Colunas com valor único

Se a coluna tem apenas 1 valor no dia, o placeholder é substituído diretamente,
sem separador nem conector.

### 4.4 Células vazias

Se nenhum valor existe para a coluna no dia corrente, a célula destino é
deixada em branco (`None`).

### 4.5 Deduplicação

Valores duplicados na mesma coluna para o mesmo dia são removidos
(`dropna().unique()`).

### 4.6 Células mescladas no template

Células dentro de regiões mescladas são ocultadas no preview. Apenas a célula
âncora (topo-esquerda) é renderizada. Mapeamentos só podem ser feitos em
células vazias (sem valor pré-existente).

### 4.7 Detecção de data

A coluna de data é detectada automaticamente: procura colunas cujo nome contém
"data" e valida 3 amostras com `pd.to_datetime(errors="raise")`. Se nenhuma
coluna de data for encontrada, o campo `_dia_aux` não é criado e a planilha
não participa da geração por dia.

### 4.8 Siglas (acronyms)

Palavras em CAIXA ALTA com 2-4 letras (ex: `RDO`, `BDI`, `ART`) são detectadas
automaticamente. O frontend pode usá-las como sugestão (não implementado na
UI atual).

---

## 5. Restrições Técnicas

| Restrição | Valor |
|---|---|
| Tamanho máximo de upload | 10 MB |
| Formatos de origem aceitos | `.xlsx`, `.xls` |
| Formato de template aceito | `.xlsx` |
| Preview de dados | Primeiras 20 linhas |
| Preview de template | Máximo 50 linhas × 26 colunas |
| Abas no template | Apenas a primeira aba é usada |
| Persistência de dados | **Nenhuma** — processamento 100% em memória |
| Autenticação | Nenhuma (ferramenta interna) |
| Tempo limite de processamento | 60s (Cloud Run) |

---

## 6. Modelo de Dados (resumo)

### SourcePreviewResponse
```
sheets: [{ name, columns, data (string[][]) }]
filename: string
suggestedAcronyms: string[]
```

### TemplatePreviewResponse
```
sheets: [{
  name, cells: [{ coord, row, col, value, font }],
  images: [{ b64, position }],
  merged: [{ min_col, max_col, min_row, max_row }]
}]
```

### GenerateConfig
```
contract: { start_date, prazo_dias, mes, ano }
mappings: [{ formatTemplate, templateCell, sourceColumns }]
listSeparator: string
listConnector: string
siglas: string[]
```

---

## 7. Segurança (LGPD)

- **Nenhum dado é armazenado** — processamento 100% em memória via `BytesIO`
- Arquivos não são escritos em disco, logs não contêm conteúdo de células
- Upload é recebido, processado, e descartado ao fim da request
- Conexão HTTPS forçada (Cloud Run + Vercel)
- CORS configurado com origens explícitas
- Sem banco de dados, sem cookies, sem autenticação de usuário
- **Aviso na interface:** "Nenhum dado é armazenado — processamento 100% em memória"

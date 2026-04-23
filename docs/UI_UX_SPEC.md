# 🎨 Especificação de UI/UX: Report Automator v2.0 (Tela Única)

Esta versão consolida todas as funcionalidades em um Dashboard de Fluxo Contínuo, focado em eficiência e visibilidade total dos parâmetros.

---

## 1. Identidade Visual
- **Paleta de Cores**:
    - Primária: Roxo Real (`#3F51B5`) - Ação, cabeçalhos e progresso.
    - Fundo: Cinza de Superfície (`#F7F9FC`) - Janela principal.
    - Cards: Branco (`#FFFFFF`) - Seções com bordas suaves (`border-radius: 12px`).
    - Texto: Azul Grafite (`#1E293B`).
- **Tipografia**: *Inter/Segoe UI* para interface, *JetBrains Mono* para logs.

---

## 2. Arquitetura do Layout (Dashboard de Fluxo Contínuo)

O layout é organizado em um fluxo vertical de cartões, permitindo que o usuário visualize toda a configuração de uma vez.

### 🔝 Cabeçalho (Header Fixo)
- Esquerda: Logotipo (Planilha + Engrenagem) + Título "Report Automator v2.0".
- Direita: Botões rápidos `[📥 Importar TOML]` e `[📤 Exportar TOML]`.

### 📜 Área Central (Scrollable)

#### Bloco 1: Ingestão de Arquivos
- Cards horizontais para "Planilha de Origem" e "Template Base".
- Feedback visual de "Arquivo Pronto" (ícone verde).
- Input discreto para "Linha do Cabeçalho" (Header Row).

#### Bloco 2: Configuração Estrutural (Grid 1:1)
- **Esquerda (Contrato)**: Inputs de Data Inicial, Prazo e Coordenadas de Metadados.
- **Direita (Mapeamento)**: `MappingTable` para gerenciar Abas -> Células.

#### Bloco 3: Extração Dinâmica
- Seleção de colunas com **Chips/Tags**.
- Editor do Template de Formato Final.

---

## 3. Detalhamento das Interações

### Extração com Chips
- Conversão automática de texto em Chips Roxos ao pressionar `Enter` ou `,`.
- Permite gerenciar múltiplas colunas sem poluir o layout.

### Validação de Metadados
- **Cálculo em tempo real**: Exibição da "Data Final calculada" logo abaixo dos inputs de prazo.
- **Regex Visual**: Bordas em Vermelho Coral para coordenadas Excel inválidas.

---

## 4. Controle e Feedback (Área Fixa Inferior)

### Barra de Status & Ação
- Faixa de status: `🟢 Sistema Pronto` ou `⚠️ Erros encontrados`.
- **Botão [GERAR DIÁRIO]**: Fixo no canto inferior direito.
- **Barra de Progresso**: Surge acima do botão apenas durante o processamento.

### Console de Logs (Terminal Retrátil)
- Gaveta na base da tela para detalhes técnicos.
- Estilo Terminal (fundo preto).
- Agrupamento inteligente de logs repetitivos.

---

## 5. Delighters (Interações Inteligentes)
- **Auto-Save**: Persistência no `config.toml` ao perder o foco do campo (*on blur*).
- **Tooltips**: Explicações rápidas sobre cálculos e campos.
- **Ações de Saída**: Botões `[📁 Abrir Pasta]` e `[📊 Abrir Excel]` após conclusão.

# Roadmap de Funcionalidades: Report Automator

Este documento detalha as funcionalidades planejadas para melhorar a experiência do usuário (UX), a robustez técnica e a facilidade de uso do sistema.

---

## 1. Gestão de Arquivos (Seleção Dinâmica)
O sistema não deve depender de caminhos fixos definidos manualmente no código ou no TOML.

*   **Botões de Browse (Procurar):** Implementação de diálogos nativos do Windows (`QFileDialog`) para que o usuário selecione a planilha de medição e o template visualmente.
*   **Persistent Paths:** O sistema deve salvar os últimos caminhos utilizados no `config.toml`. Ao reabrir o app, os campos já devem vir preenchidos com as seleções anteriores.

## 2. Persistência de Configuração
Permitir que o usuário personalize o mapeamento sem precisar editar arquivos de texto.

*   **Botão "Salvar":** Interface para editar quais colunas da origem vão para quais células do destino, com um botão dedicado para persistir essas escolhas no arquivo `config.toml` local.
*   **Botão "Importar Configuração":** Permite carregar um arquivo `.toml` externo, facilitando a troca rápida entre diferentes perfis de mapeamento ou configurações compartilhadas.
*   **Botão "Exportar Configuração":** Permite salvar o mapeamento atual da interface em um novo arquivo `.toml` em qualquer local do computador, servindo como backup ou template para outros projetos.

## 3. Validação e Segurança (Robustez)
Prevenção de erros comuns que causam o fechamento inesperado (crash) do programa.

*   **Check de Arquivo Aberto:** Antes de iniciar a geração, o sistema deve verificar se o arquivo de destino (ou o template) está aberto no Excel. Caso esteja, emitir um alerta amigável: *"O arquivo está aberto. Por favor, feche-o antes de continuar."*
*   **Validação de Mapeamento:** Verificar se as coordenadas inseridas (ex: "B10", "Z50") são coordenadas válidas do Excel antes de processar, evitando erros de escrita no motor `openpyxl`.

## 4. Feedback e Monitoramento (UX)
Melhorar a percepção de progresso e facilitar o acesso aos resultados.

*   **Barra de Progresso Real:** A barra deve avançar proporcionalmente aos dias do mês processados (ex: se o mês tem 30 dias, cada dia processado avança ~3.3% da barra).
*   **Auto-Scroll no Log:** Garantir que a área de log sempre mostre a mensagem mais recente, rolando automaticamente para o final conforme o processo avança.
*   **Botão "Abrir Pasta de Saída":** Após a conclusão com sucesso, oferecer um botão ou link direto para abrir a pasta `data/output/` no Windows Explorer.

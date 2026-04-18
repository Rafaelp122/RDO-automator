# Lógica de Prioridade de Templates

O Report Automator permite que o usuário utilize seu próprio arquivo de template (`.xlsx`) para gerar os relatórios. 

## Como funciona

O sistema segue a seguinte ordem de prioridade para encontrar o arquivo de template:

1.  **Template do Usuário (`user_template`)**: O sistema verifica se existe um arquivo chamado `user_template.xlsx` dentro da pasta `data/input/`.
2.  **Template Padrão (`default_template`)**: Caso o arquivo do usuário não seja encontrado, o sistema utiliza automaticamente o template base localizado em `assets/template.xlsx`.

## Configuração (config.toml)

As rotas são definidas na seção `[arquivos]`:

```toml
[arquivos]
default_template = "assets/template.xlsx"
user_template = "data/input/user_template.xlsx"
```

## Benefícios
- **Não quebra o sistema**: Se o usuário deletar o próprio template ou enviar um arquivo inválido em outra ocasião, o sistema sempre terá o padrão como fallback.
- **Flexibilidade**: Permite que diferentes contratos ou projetos tenham layouts de diário de obra personalizados sem alterar o código.

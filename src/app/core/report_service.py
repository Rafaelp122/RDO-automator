import os
from src.app.infra.excel_handler import ExcelHandler
from src.app.core.logger import logger

class ReportService:
    """
    Serviço de Domínio para orquestrar a geração de relatórios.
    Lida com a lógica de decisão (templates, caminhos) antes de delegar para infra.
    """

    def generate_report(self, config, progress_callback=None):
        """
        Orquestra o fluxo completo de geração do relatório.
        """
        # 1. Validar existência do arquivo de origem
        dados_origem = config.get('arquivos', {}).get('dados_origem')
        if not dados_origem or not os.path.exists(dados_origem):
            raise FileNotFoundError(f"Arquivo de dados não encontrado: {dados_origem}")
        
        # 2. Lógica de Prioridade de Template
        user_tmpl = config.get('arquivos', {}).get('user_template')
        default_tmpl = config.get('arquivos', {}).get('default_template')
        
        if user_tmpl and os.path.exists(user_tmpl):
            logger.info(f"Usando template customizado: {user_tmpl}")
            config['arquivos']['template_ativo'] = user_tmpl
        else:
            if not default_tmpl or not os.path.exists(default_tmpl):
                raise FileNotFoundError(f"Template padrão não encontrado em: {default_tmpl}")
            logger.info("Usando template padrão do sistema.")
            config['arquivos']['template_ativo'] = default_tmpl

        # 3. Delegar para o ExcelHandler (Infra)
        logger.info("Iniciando processamento Excel via ExcelHandler...")
        handler = ExcelHandler(config)
        arquivo_final = handler.gerar_diario_completo(progress_callback=progress_callback)
        
        return arquivo_final

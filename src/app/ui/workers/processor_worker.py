import os
import tomllib
from PySide6.QtCore import QObject, Signal, Slot
from src.app.infra.excel_handler import ExcelHandler
from src.app.core.logger import logger

class ProcessorWorker(QObject):
    """
    Worker class to handle Excel processing in a background thread.
    Keeps the UI logic clean and decoupled.
    """
    progress_log = Signal(str)
    progress_update = Signal(int)
    finished = Signal(str)
    error = Signal(str)

    @Slot()
    def run(self):
        try:
            msg = "Lendo configurações..."
            logger.info(msg)
            self.progress_log.emit(msg)
            
            if not os.path.exists("config.toml"):
                raise FileNotFoundError("config.toml não encontrado.")

            with open("config.toml", "rb") as f:
                config = tomllib.load(f)

            msg = "Validando arquivos..."
            logger.info(msg)
            self.progress_log.emit(msg)
            
            if not os.path.exists(config['arquivos']['dados_origem']):
                raise FileNotFoundError(f"Arquivo de dados não encontrado: {config['arquivos']['dados_origem']}")
            
            # Lógica de Prioridade de Template
            user_tmpl = config['arquivos'].get('user_template')
            default_tmpl = config['arquivos'].get('default_template')
            
            if user_tmpl and os.path.exists(user_tmpl):
                msg = f"Usando template customizado: {user_tmpl}"
                logger.info(msg)
                self.progress_log.emit(msg)
                config['arquivos']['template_ativo'] = user_tmpl
            else:
                msg = "Usando template padrão do sistema."
                logger.info(msg)
                self.progress_log.emit(msg)
                config['arquivos']['template_ativo'] = default_tmpl

            msg = "Gerando abas diárias..."
            logger.info(msg)
            self.progress_log.emit(msg)
            
            handler = ExcelHandler(config)
            arquivo_final = handler.gerar_diario_completo(progress_callback=self.progress_update.emit)
            
            msg = f"Concluído: {arquivo_final}"
            logger.info(msg)
            self.progress_log.emit(msg)
            self.finished.emit(arquivo_final)
            
        except Exception as e:
            err_msg = f"FALHA: {str(e)}"
            logger.exception(err_msg)
            self.progress_log.emit(err_msg)
            self.error.emit(str(e))

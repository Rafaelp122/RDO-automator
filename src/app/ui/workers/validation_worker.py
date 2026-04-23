from PySide6.QtCore import QObject, Signal, Slot
from src.app.core.logger import logger

class ValidationWorker(QObject):
    """
    Worker para validar a integridade dos dados e mapeamentos.
    Recebe dependências injetadas da MainWindow.
    """
    progress_log = Signal(str)
    validation_finished = Signal(bool, list, dict) # Sucesso, Lista Log, Erros por Campo
    finished = Signal()

    def __init__(self, config, validator):
        super().__init__()
        self.config = config
        self.validator = validator

    @Slot()
    def run(self):
        try:
            msg = "Iniciando validação de mapeamento..."
            logger.info(msg)
            self.progress_log.emit(msg)
            
            # Delegar validação para o Core
            sucesso, erros_log, field_errors = self.validator.validate(self.config)

            for msg_log in erros_log:
                self.progress_log.emit(f"ERRO: {msg_log}")

            if sucesso:
                msg = "Tudo ok! Mapeamento validado."
                logger.info(msg)
                self.progress_log.emit(msg)
                self.validation_finished.emit(True, [], {})
            else:
                logger.warning(f"Validação concluída com {len(erros_log)} erros.")
                self.validation_finished.emit(False, erros_log, field_errors)

        except Exception as e:
            err_msg = f"Erro fatal na validação: {str(e)}"
            logger.exception(err_msg)
            self.progress_log.emit(err_msg)
            self.validation_finished.emit(False, [str(e)], {"geral": str(e)})
        
        finally:
            self.finished.emit()

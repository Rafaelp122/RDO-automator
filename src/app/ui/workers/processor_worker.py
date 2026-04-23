from PySide6.QtCore import QObject, Signal, Slot
from src.app.core.logger import logger

class ProcessorWorker(QObject):
    """
    Worker para processamento Excel em segundo plano.
    Recebe dependências injetadas da MainWindow.
    """
    progress_log = Signal(str)
    progress_update = Signal(int)
    finished = Signal(str)
    error = Signal(str)

    def __init__(self, config, service):
        super().__init__()
        self.config = config
        self.service = service

    @Slot()
    def run(self):
        try:
            self.progress_log.emit("Iniciando serviço de relatório...")
            
            # Delegar para o serviço injetado
            arquivo_final = self.service.generate_report(
                self.config, 
                progress_callback=self.progress_update.emit
            )
            
            self.progress_log.emit(f"Relatório gerado com sucesso: {arquivo_final}")
            self.finished.emit(arquivo_final)
            
        except Exception as e:
            err_msg = f"FALHA: {str(e)}"
            logger.exception(err_msg)
            self.progress_log.emit(err_msg)
            self.error.emit(str(e))

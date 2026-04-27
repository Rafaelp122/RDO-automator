from PySide6.QtCore import QObject, QThread, Slot, QTimer
from src.app.ui.windows.main_window import MainWindow
from src.app.infra.config_manager import ConfigManager
from src.app.ui.workers.validation_worker import ValidationWorker
from src.app.ui.workers.processor_worker import ProcessorWorker
from src.app.core.validator import ReportValidator
from src.app.core.report_service import ReportService
from src.app.core.logger import logger


class MainController(QObject):
    """
    Controlador Principal (MVC):
    Orquestra a lógica de negócio, threads e comunicação entre View e Infra.
    """

    def __init__(self, config_manager: ConfigManager):
        super().__init__()
        self.config_manager = config_manager
        self.config = self.config_manager.config
        
        # Gerenciamento de threads
        self._active_threads = []
        self._val_thread = None
        self._val_worker = None

        # Timer para debounce de salvamento (500ms)
        self._save_timer = QTimer()
        self._save_timer.setSingleShot(True)
        self._save_timer.setInterval(500)
        self._save_timer.timeout.connect(self._save_config_and_validate)
        
        # Inicializa a View
        self.view = MainWindow(self.config)
        self._connect_signals()

    def _connect_signals(self):
        """Conecta os sinais da View aos slots do Controller"""
        self.view.config_changed.connect(self._on_config_changed_debounced)
        self.view.generate_requested.connect(self._start_generation)
        self.view.import_requested.connect(self._import_config)
        self.view.export_requested.connect(self._export_config)

    def show(self):
        """Exibe a janela e inicia a primeira validação"""
        self.view.show()
        self._validate_initial()

    def _on_config_changed_debounced(self):
        """Reinicia o timer sempre que houver uma mudança na config"""
        self._save_timer.start()

    def _save_config_and_validate(self):
        """Salva a configuração atual e dispara validação assíncrona"""
        try:
            self.config_manager.save_config(self.config)
            self._validate_initial()
        except Exception as e:
            logger.error(f"Erro ao salvar configuração: {e}")
            self.view.update_status(f"❌ Erro ao salvar config: {e}", is_error=True)

    def _validate_initial(self):
        """Executa a validação de mapeamento, garantindo que apenas uma ocorra por vez"""
        # Se já houver uma validação rodando, desconecta os sinais para evitar poluição visual
        # mas deixa a thread terminar para evitar crashes (terminate é inseguro)
        if self._val_worker:
            try:
                self._val_worker.progress_log.disconnect()
                self._val_worker.validation_finished.disconnect()
            except (TypeError, RuntimeError):
                pass

        self.view.clear_field_errors()
        
        self._val_thread = QThread()
        self._val_worker = ValidationWorker(self.config, ReportValidator())
        self._val_worker.moveToThread(self._val_thread)
        
        # Manter referência ao worker atrelada à thread
        self._val_thread.worker = self._val_worker
        
        self._val_thread.started.connect(self._val_worker.run)
        self._val_worker.progress_log.connect(self.view.log_message)
        self._val_worker.validation_finished.connect(self._on_validation_finished)
        
        # Cleanup robusto
        self._val_worker.finished.connect(self._val_thread.quit)
        self._val_worker.finished.connect(self._val_worker.deleteLater)
        self._val_thread.finished.connect(self._val_thread.deleteLater)
        self._val_thread.finished.connect(lambda: self._on_thread_finished(self._val_thread))
        
        self._active_threads.append(self._val_thread)
        self._val_thread.start()

    def _on_thread_finished(self, thread):
        """Remove a thread da lista de ativos após a conclusão"""
        if thread in self._active_threads:
            self._active_threads.remove(thread)

    @Slot(bool, list, dict)
    def _on_validation_finished(self, success, errors, field_errors):
        if success:
            self.view.update_status("🟢 Sistema Pronto")
        else:
            self.view.update_status("⚠️ Erros encontrados. Verifique o console.", is_error=True)
            self.view.show_field_errors(field_errors)

    def _start_generation(self):
        """Inicia o processo de geração do relatório em uma thread separada"""
        self.view.set_generating_state(True)
        self.view.log_message("Iniciando geração de relatório...")
        
        thread = QThread()
        worker = ProcessorWorker(self.config, ReportService())
        worker.moveToThread(thread)
        
        # Manter referência ao worker
        thread.worker = worker
        
        thread.started.connect(worker.run)
        worker.progress_log.connect(self.view.log_message)
        worker.progress_update.connect(self.view.update_progress)
        worker.finished.connect(self._on_generation_finished)
        worker.error.connect(self._on_generation_error)
        
        # Cleanup robusto
        worker.finished.connect(thread.quit)
        worker.finished.connect(worker.deleteLater)
        worker.error.connect(thread.quit)
        worker.error.connect(worker.deleteLater)
        thread.finished.connect(thread.deleteLater)
        thread.finished.connect(lambda: self._on_thread_finished(thread))
        
        self._active_threads.append(thread)
        thread.start()

    @Slot(str)
    def _on_generation_finished(self, file_path):
        self.view.set_generating_state(False)
        self.view.update_status("✅ Diário Gerado com Sucesso!")
        self.view.update_progress(100)
        self.view.show_success_dialog("Sucesso", f"Relatório gerado em:\n{file_path}")

    @Slot(str)
    def _on_generation_error(self, error_msg):
        self.view.set_generating_state(False)
        self.view.update_status("❌ Falha na geração", is_error=True)
        self.view.show_error_dialog("Erro", f"Ocorreu um erro:\n{error_msg}")

    def _import_config(self):
        """Lógica de importação de arquivo TOML"""
        file_path = self.view.get_open_file_path("Importar Configuração", "Arquivos TOML (*.toml)")
        if file_path:
            try:
                self.config = self.config_manager.import_config(file_path)
                self.view.show_success_dialog("Sucesso", "Configuração importada! Reinicie o app para aplicar todas as mudanças visuais.")
                self._validate_initial()
            except Exception as e:
                self.view.show_error_dialog("Erro", f"Falha ao importar: {str(e)}")

    def _export_config(self):
        """Lógica de exportação de arquivo TOML"""
        file_path = self.view.get_save_file_path("Exportar Configuração", "config_exportada.toml", "Arquivos TOML (*.toml)")
        if file_path:
            try:
                self.config_manager.export_config(file_path, config_to_export=self.config)
                self.view.show_success_dialog("Sucesso", "Configuração exportada com sucesso!")
            except Exception as e:
                self.view.show_error_dialog("Erro", f"Falha ao exportar: {str(e)}")

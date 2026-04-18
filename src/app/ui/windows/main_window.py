from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QMessageBox
from PySide6.QtCore import Slot

from src.app.ui.workers.processor_worker import ProcessorWorker
from src.app.ui.workers.validation_worker import ValidationWorker
from src.app.ui.components.header import Header
from src.app.ui.components.processing_panel import ProcessingPanel
from src.app.ui.utils.thread_manager import run_worker_thread

class MainWindow(QMainWindow):
    """
    Main Window Refatorada:
    - Uso de lista para manter threads vivas (evita Garbage Collection).
    - Logs duplicados no terminal.
    """
    
    def __init__(self):
        super().__init__()
        print("[MAIN] Inicializando aplicação...")
        
        self.setWindowTitle("Report Automator v1.0")
        self.setFixedSize(600, 560)
        self._load_styles()
        
        # Lista de threads para evitar que o Python as delete prematuramente
        self._threads = []
        self._is_running = False
        
        # UI Setup
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        self.header = Header("Report Automator")
        self.main_layout.addWidget(self.header)

        self.processing_panel = ProcessingPanel()
        self.processing_panel.start_requested.connect(self.iniciar_processamento)
        self.processing_panel.revalidate_requested.connect(self.executar_validacao)
        
        panel_container = QWidget()
        panel_layout = QVBoxLayout(panel_container)
        panel_layout.setContentsMargins(20, 20, 20, 20)
        panel_layout.addWidget(self.processing_panel)
        self.main_layout.addWidget(panel_container)
        
        self._setup_footer()
        print("[MAIN] Interface pronta.")
        self.executar_validacao()

    def _load_styles(self):
        try:
            with open("src/app/ui/styles/main.qss", "r") as f:
                self.setStyleSheet(f.read())
        except Exception as e:
            print(f"[ERROR] Falha ao carregar estilos: {e}")

    def _setup_footer(self):
        footer_container = QWidget()
        footer_layout = QHBoxLayout(footer_container)
        self.footer_label = QLabel("v1.0.0 | Licença MIT")
        self.footer_label.setObjectName("FooterLabel")
        footer_layout.addStretch()
        footer_layout.addWidget(self.footer_label)
        footer_layout.addStretch()
        self.main_layout.addWidget(footer_container)

    def executar_validacao(self):
        if self._is_running:
            return

        print("[VAL] Validando mapeamento...")
        self._is_running = True
        self.processing_panel.clear_log()
        self.processing_panel.set_busy(True, "Validando arquivos...")
        
        worker = ValidationWorker()
        worker.validation_finished.connect(self.processar_resultado_validacao)
        
        # Adicionamos a thread à lista para mantê-la viva
        thread = run_worker_thread(worker, on_log=self._log_both)
        self._threads.append(thread)
        # Limpa a referência da lista quando a thread terminar
        thread.finished.connect(lambda t=thread: self._cleanup_thread(t))

    def _cleanup_thread(self, thread):
        """Remove a thread da lista de persistência após o término"""
        if thread in self._threads:
            self._threads.remove(thread)
            print(f"[DEBUG] Thread encerrada e removida. Ativas: {len(self._threads)}")

    def _log_both(self, message):
        print(f"[LOG] {message}")
        self.processing_panel.log(message)

    @Slot(bool, list)
    def processar_resultado_validacao(self, sucesso, erros):
        self._is_running = False
        if sucesso:
            self.processing_panel.set_validation_state(True, "Pronto para operação.")
        else:
            self.processing_panel.set_validation_state(False)
            for erro in erros:
                self._log_both(f"ERRO: {erro}")
            QMessageBox.critical(self, "Erro de Mapeamento", "Verifique os problemas listados.")

    def iniciar_processamento(self):
        if self._is_running:
            return

        print("[PROC] Iniciando geração...")
        self._is_running = True
        self.processing_panel.clear_log()
        self.processing_panel.set_busy(True, "Gerando relatório...")
        
        worker = ProcessorWorker()
        thread = run_worker_thread(
            worker,
            on_finished=self.finalizar_sucesso,
            on_error=self.finalizar_erro,
            on_log=self._log_both
        )
        self._threads.append(thread)
        thread.finished.connect(lambda t=thread: self._cleanup_thread(t))

    @Slot(str)
    def finalizar_sucesso(self, arquivo):
        self._is_running = False
        self.processing_panel.set_busy(False)
        self.processing_panel.set_progress_success()
        QMessageBox.information(self, "Sucesso", f"Relatório gerado!\n{arquivo}")

    @Slot(str)
    def finalizar_erro(self, msg):
        self._is_running = False
        self.processing_panel.set_validation_state(True)
        QMessageBox.critical(self, "Erro no Processamento", msg)

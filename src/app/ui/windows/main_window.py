from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QScrollArea, QMessageBox, QFileDialog
)
from PySide6.QtCore import Qt, QThread

from src.app.ui.components.layout.header import Header
from src.app.ui.components.panels.ingestion_panel import IngestionPanel
from src.app.ui.components.panels.config_panel import ConfigPanel
from src.app.ui.components.panels.extraction_panel import ExtractionPanel
from src.app.ui.components.panels.control_panel import ControlPanel
from src.app.ui.components.layout.footer import Footer

from src.app.infra.config_manager import ConfigManager
from src.app.ui.workers.validation_worker import ValidationWorker
from src.app.ui.workers.processor_worker import ProcessorWorker
from src.app.core.logger import logger

class MainWindow(QMainWindow):
    """
    Main Window Refatorada (View v2.0):
    Responsável apenas pelo layout, instanciação de componentes e orquestração de sinais.
    """
    
    def __init__(self):
        super().__init__()
        logger.info("Inicializando visual da MainWindow v2.0...")
        
        self.setWindowTitle("Report Automator v2.0")
        self.setMinimumSize(900, 800)
        
        self.config_manager = ConfigManager()
        self.config = self.config_manager.load_config()
        
        self._setup_ui()
        self._load_styles()
        
        self._validate_initial()

    def _setup_ui(self):
        # UI Setup
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        # Header
        self.header = Header("Report Automator v2.0")
        self.main_layout.addWidget(self.header)

        # Scroll Area for the panels
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QScrollArea.NoFrame)
        self.scroll_content = QWidget()
        self.scroll_content.setObjectName("ScrollContent")
        self.scroll_layout = QVBoxLayout(self.scroll_content)
        self.scroll_layout.setContentsMargins(20, 20, 20, 20)
        self.scroll_layout.setSpacing(20)
        
        # 1. Ingestão
        self.ingestion_panel = IngestionPanel(self.config)
        self.ingestion_panel.config_changed.connect(self._save_config_and_validate)
        self.scroll_layout.addWidget(self.ingestion_panel)
        
        # 2. Configuração (Grid)
        self.config_panel = ConfigPanel(self.config)
        self.config_panel.config_changed.connect(self._save_config_and_validate)
        self.scroll_layout.addWidget(self.config_panel)
        
        # 3. Extração Dinâmica
        self.extraction_panel = ExtractionPanel(self.config)
        self.extraction_panel.config_changed.connect(self._save_config_and_validate)
        self.scroll_layout.addWidget(self.extraction_panel)
        
        # 4. Controle e Execução
        self.control_panel = ControlPanel()
        self.control_panel.generate_requested.connect(self._start_generation)
        self.control_panel.import_requested.connect(self._import_config)
        self.control_panel.export_requested.connect(self._export_config)
        self.scroll_layout.addWidget(self.control_panel)
        
        # Spacer
        self.scroll_layout.addStretch()
        self.scroll_area.setWidget(self.scroll_content)
        
        self.main_layout.addWidget(self.scroll_area)
        
        # Footer
        self.footer = Footer(version="v2.0.0", license_info="Licença MIT")
        self.main_layout.addWidget(self.footer)

    def _load_styles(self):
        try:
            styles = []
            for style_file in ["global.qss", "panels.qss"]:
                with open(f"src/app/ui/styles/{style_file}", "r") as f:
                    styles.append(f.read())
            self.setStyleSheet("\n".join(styles))
        except Exception as e:
            logger.error(f"Falha ao carregar estilos: {e}")

    def _save_config_and_validate(self):
        self.config_manager.save_config()
        self._validate_initial()
        
    def _validate_initial(self):
        self.control_panel.log("Iniciando validação...")
        self.val_thread = QThread()
        self.val_worker = ValidationWorker()
        self.val_worker.moveToThread(self.val_thread)
        
        self.val_thread.started.connect(self.val_worker.run)
        self.val_worker.progress_log.connect(self.control_panel.log)
        self.val_worker.validation_finished.connect(self._on_validation_finished)
        self.val_worker.finished.connect(self.val_thread.quit)
        self.val_worker.finished.connect(self.val_worker.deleteLater)
        self.val_thread.finished.connect(self.val_thread.deleteLater)
        
        self.val_thread.start()

    def _on_validation_finished(self, success, errors):
        if success:
            self.control_panel.set_status("🟢 Sistema Pronto")
        else:
            self.control_panel.set_status("⚠️ Erros encontrados. Verifique o console.", is_error=True)

    def _start_generation(self):
        self.control_panel.set_generating(True)
        
        self.proc_thread = QThread()
        self.proc_worker = ProcessorWorker()
        self.proc_worker.moveToThread(self.proc_thread)
        
        self.proc_thread.started.connect(self.proc_worker.run)
        self.proc_worker.progress_log.connect(self.control_panel.log)
        self.proc_worker.progress_update.connect(self.control_panel.set_progress)
        self.proc_worker.finished.connect(self._on_generation_finished)
        self.proc_worker.error.connect(self._on_generation_error)
        
        self.proc_worker.finished.connect(self.proc_thread.quit)
        self.proc_worker.finished.connect(self.proc_worker.deleteLater)
        self.proc_worker.error.connect(self.proc_thread.quit)
        self.proc_worker.error.connect(self.proc_worker.deleteLater)
        self.proc_thread.finished.connect(self.proc_thread.deleteLater)
        
        self.proc_thread.start()

    def _on_generation_finished(self, file_path):
        self.control_panel.set_generating(False)
        self.control_panel.set_status("✅ Diário Gerado com Sucesso!")
        self.control_panel.set_progress(100)
        QMessageBox.information(self, "Sucesso", f"Relatório gerado em:\n{file_path}")

    def _on_generation_error(self, error_msg):
        self.control_panel.set_generating(False)
        self.control_panel.set_status("❌ Falha na geração", is_error=True)
        QMessageBox.critical(self, "Erro", f"Ocorreu um erro:\n{error_msg}")

    def _import_config(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Importar Configuração", "", "Arquivos TOML (*.toml)"
        )
        if file_path:
            try:
                self.config = self.config_manager.import_config(file_path)
                QMessageBox.information(self, "Sucesso", "Configuração importada com sucesso! Reinicie o aplicativo para recarregar as novas configurações.")
                # Opcional: Atualizar toda a UI (reiniciar os painéis)
            except Exception as e:
                QMessageBox.critical(self, "Erro", f"Falha ao importar: {str(e)}")

    def _export_config(self):
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Exportar Configuração", "config_exportada.toml", "Arquivos TOML (*.toml)"
        )
        if file_path:
            try:
                self.config_manager.export_config(file_path)
                QMessageBox.information(self, "Sucesso", "Configuração exportada com sucesso!")
            except Exception as e:
                QMessageBox.critical(self, "Erro", f"Falha ao exportar: {str(e)}")


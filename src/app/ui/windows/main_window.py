from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QScrollArea, QMessageBox, QFileDialog
)
from PySide6.QtCore import Qt, Signal

from src.app.ui.components.layout.header import Header
from src.app.ui.components.panels.ingestion_panel import IngestionPanel
from src.app.ui.components.panels.config_panel import ConfigPanel
from src.app.ui.components.panels.extraction_panel import ExtractionPanel
from src.app.ui.components.panels.control_panel import ControlPanel
from src.app.ui.components.layout.footer import Footer
from src.app.core.logger import logger
from src.app.core.config_models import ReportConfig


class MainWindow(QMainWindow):
    """
    Main Window (View v1.0):
    Responsável apenas pelo layout, montagem da UI e exposição de sinais/métodos visuais.
    Não contém lógica de processamento ou gerenciamento de threads.
    """

    # Sinais repassados para o Controller
    config_changed = Signal()
    generate_requested = Signal()
    import_requested = Signal()
    export_requested = Signal()

    def __init__(self, config: ReportConfig):
        super().__init__()
        logger.info("Inicializando MainWindow (View)...")

        self.config = config
        self.setWindowTitle("RDO Automator v1.0")
        self.setMinimumSize(900, 800)

        self._setup_ui()
        self._load_styles()

    def _setup_ui(self):
        # UI Setup
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        # Header
        self.header = Header("RDO Automator v1.0")
        self.main_layout.addWidget(self.header)

        # Scroll Area for the panels
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QScrollArea.Shape.NoFrame)
        self.scroll_content = QWidget()
        self.scroll_content.setObjectName("ScrollContent")
        self.scroll_layout = QVBoxLayout(self.scroll_content)
        self.scroll_layout.setContentsMargins(20, 20, 20, 20)
        self.scroll_layout.setSpacing(20)
        
        # 1. Ingestão
        self.ingestion_panel = IngestionPanel(self.config)
        self.ingestion_panel.config_changed.connect(self.config_changed.emit)
        self.scroll_layout.addWidget(self.ingestion_panel)
        
        # 2. Configuração (Grid)
        self.config_panel = ConfigPanel(self.config)
        self.config_panel.config_changed.connect(self.config_changed.emit)
        self.scroll_layout.addWidget(self.config_panel)
        
        # 3. Extração Dinâmica
        self.extraction_panel = ExtractionPanel(self.config)
        self.extraction_panel.config_changed.connect(self.config_changed.emit)
        self.scroll_layout.addWidget(self.extraction_panel)
        
        # 4. Controle e Execução
        self.control_panel = ControlPanel()
        self.control_panel.generate_requested.connect(self.generate_requested.emit)
        self.control_panel.import_requested.connect(self.import_requested.emit)
        self.control_panel.export_requested.connect(self.export_requested.emit)
        self.scroll_layout.addWidget(self.control_panel)
        
        # Spacer
        self.scroll_layout.addStretch()
        self.scroll_area.setWidget(self.scroll_content)
        
        self.main_layout.addWidget(self.scroll_area)
        
        # Footer
        self.footer = Footer(version="v1.0.0", license_info="Licença MIT")
        self.main_layout.addWidget(self.footer)

    def _load_styles(self):
        from src.app.core.constants import STYLES_DIR, ASSETS_DIR
        try:
            styles = []
            for style_file in ["global.qss", "panels.qss"]:
                path = STYLES_DIR / style_file
                if path.exists():
                    with open(path, "r") as f:
                        qss = f.read()
                        # Resolve caminhos de ativos dinamicamente
                        assets_path = str(ASSETS_DIR.absolute()).replace("\\", "/")
                        qss = qss.replace("{{ASSETS_DIR}}", assets_path)
                        styles.append(qss)
            self.setStyleSheet("\n".join(styles))
        except Exception as e:
            logger.error(f"Falha ao carregar estilos: {e}")

    # --- Métodos Públicos de Interface (chamados pelo Controller) ---

    def log_message(self, message: str):
        """Adiciona mensagem ao console de log"""
        self.control_panel.log(message)

    def refresh_ui(self):
        """Propaga o comando de atualização para todos os painéis"""
        self.ingestion_panel.refresh_ui()
        self.config_panel.refresh_ui()
        self.extraction_panel.refresh_ui()

    def set_config(self, new_config):
        """Atualiza a referência de configuração em todos os componentes"""
        self.config = new_config
        self.ingestion_panel.set_config(new_config)
        self.config_panel.set_config(new_config)
        self.extraction_panel.set_config(new_config)
        self.refresh_ui()

    def update_status(self, text: str, is_error: bool = False):
        """Atualiza o label de status"""
        self.control_panel.set_status(text, is_error)

    def update_progress(self, value: int):
        """Atualiza a barra de progresso"""
        self.control_panel.set_progress(value)

    def set_generating_state(self, is_generating: bool):
        """Alterna o estado visual de geração (bloqueia botões, mostra spinner/progress)"""
        self.control_panel.set_generating(is_generating)

    def show_success_dialog(self, title: str, message: str):
        """Exibe popup de sucesso"""
        QMessageBox.information(self, title, message)

    def show_error_dialog(self, title: str, message: str):
        """Exibe popup de erro"""
        QMessageBox.critical(self, title, message)

    def get_open_file_path(self, title: str, filter: str) -> str:
        """Abre diálogo de seleção de arquivo"""
        path, _ = QFileDialog.getOpenFileName(self, title, "", filter)
        return path

    def get_save_file_path(self, title: str, default_name: str, filter: str) -> str:
        """Abre diálogo de salvamento de arquivo"""
        path, _ = QFileDialog.getSaveFileName(self, title, default_name, filter)
        return path

    def clear_field_errors(self):
        """Limpa estados de erro de todos os painéis"""
        self.ingestion_panel.clear_errors()
        self.config_panel.clear_errors()
        self.extraction_panel.clear_errors()

    def show_field_errors(self, field_errors: dict):
        """Propaga erros de campo para os painéis correspondentes"""
        self.ingestion_panel.set_field_errors(field_errors)
        self.config_panel.set_field_errors(field_errors)
        self.extraction_panel.set_field_errors(field_errors)

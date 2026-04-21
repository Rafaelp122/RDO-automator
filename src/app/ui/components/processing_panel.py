from PySide6.QtWidgets import QFrame, QVBoxLayout, QProgressBar, QPushButton, QHBoxLayout
from PySide6.QtCore import Qt, Signal, Slot

from src.app.ui.components.log_view import LogView
from src.app.ui.components.file_selector import FileSelector
from src.app.ui.components.mapping_table import MappingTable

class ProcessingPanel(QFrame):
    """
    Painel central que encapsula a lógica visual de processamento e validação.
    Refatorado para usar sub-componentes especializados.
    """
    start_requested = Signal()
    revalidate_requested = Signal()
    config_save_requested = Signal(dict)
    import_config_requested = Signal()
    export_config_requested = Signal(dict)
    origin_selected = Signal(str)
    template_selected = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("MainCard")
        self._in_error_state = False
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(25, 20, 25, 25)
        layout.setSpacing(10)

        # File Selection Area
        self.input_origin = FileSelector("Planilha de Origem (Dados):")
        self.input_origin.file_selected.connect(self.origin_selected.emit)
        
        self.input_template = FileSelector("Template Excel (Visual):")
        self.input_template.file_selected.connect(self.template_selected.emit)

        layout.addWidget(self.input_origin)
        layout.addWidget(self.input_template)

        # Mapping Table
        self.mapping_table = MappingTable()
        layout.addWidget(self.mapping_table)
        
        # Config Buttons Area
        config_btns_layout = QHBoxLayout()
        
        self.btn_save_config = QPushButton("SALVAR")
        self.btn_save_config.setObjectName("SecondaryButton")
        self.btn_save_config.clicked.connect(self._handle_save_config)
        
        self.btn_import_config = QPushButton("IMPORTAR")
        self.btn_import_config.setObjectName("SecondaryButton")
        self.btn_import_config.clicked.connect(self.import_config_requested.emit)
        
        self.btn_export_config = QPushButton("EXPORTAR")
        self.btn_export_config.setObjectName("SecondaryButton")
        self.btn_export_config.clicked.connect(self._handle_export_config)
        
        config_btns_layout.addWidget(self.btn_save_config)
        config_btns_layout.addWidget(self.btn_import_config)
        config_btns_layout.addWidget(self.btn_export_config)
        layout.addLayout(config_btns_layout)

        # Log View
        self.log_console = LogView(initial_text="Aguardando validação inicial...")
        layout.addWidget(self.log_console)

        # Progress Bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setFormat("%p%")
        layout.addWidget(self.progress_bar)

        # Action Button
        self.btn_action = QPushButton("VERIFICANDO DADOS...")
        self.btn_action.setObjectName("ActionButton")
        self.btn_action.setCursor(Qt.PointingHandCursor)
        self.btn_action.setEnabled(False)
        self.btn_action.clicked.connect(self._handle_button_click)
        layout.addWidget(self.btn_action)

    def _handle_save_config(self):
        self.config_save_requested.emit(self._get_current_config_from_ui())

    def _handle_export_config(self):
        self.export_config_requested.emit(self._get_current_config_from_ui())

    def _get_current_config_from_ui(self):
        return {
            "arquivos": {
                "dados_origem": self.input_origin.text(),
                "user_template": self.input_template.text()
            },
            "mapeamento": self.mapping_table.get_mapping()
        }

    def set_config_values(self, origin, template, mapeamento=None):
        self.input_origin.setText(origin)
        self.input_template.setText(template)
        self.mapping_table.set_mapping(mapeamento)

    def update_progress(self, value):
        self.progress_bar.setValue(value)

    def _handle_button_click(self):
        if self._in_error_state:
            self.revalidate_requested.emit()
        else:
            self.start_requested.emit()

    def set_validation_state(self, sucesso: bool, mensagem: str = ""):
        self._in_error_state = not sucesso
        self.btn_action.setText("GERAR RELATÓRIO MENSAL" if sucesso else "REVALIDAR ARQUIVOS")
        self.btn_action.setEnabled(True)
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        if mensagem:
            self.log(mensagem)

    def set_busy(self, busy: bool, message: str = "Processando..."):
        self.btn_action.setEnabled(not busy)
        if busy:
            self.btn_action.setText(message)
            self.progress_bar.setRange(0, 0)

    def set_progress_success(self):
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(100)
        self.btn_action.setText("RELATÓRIO GERADO!")

    def log(self, message: str):
        self.log_console.log(message)

    def clear_log(self):
        self.log_console.clear()

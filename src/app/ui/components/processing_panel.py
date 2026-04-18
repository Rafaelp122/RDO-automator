from PySide6.QtWidgets import QFrame, QVBoxLayout, QProgressBar, QPushButton, QWidget, QHBoxLayout, QLineEdit, QLabel, QFileDialog, QTableWidget, QTableWidgetItem, QHeaderView
from PySide6.QtCore import Qt, Signal, Slot
from src.app.ui.components.log_view import LogView

class ProcessingPanel(QFrame):
    """
    Painel central que encapsula a lógica visual de processamento e validação.
    """
    start_requested = Signal()
    revalidate_requested = Signal()
    config_save_requested = Signal(dict)

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
        file_selection_layout = QVBoxLayout()
        file_selection_layout.setSpacing(5)

        # Origin Data
        self.input_origin = self._create_file_selector("Planilha de Origem (Dados):", file_selection_layout)
        # Template
        self.input_template = self._create_file_selector("Template Excel (Visual):", file_selection_layout)

        layout.addLayout(file_selection_layout)

        # Mapping Table
        layout.addWidget(QLabel("Mapeamento (Aba Origem -> Célula Destino):"))
        self.mapping_table = QTableWidget(0, 2)
        self.mapping_table.setHorizontalHeaderLabels(["Aba na Origem", "Célula no Template"])
        self.mapping_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.mapping_table.setFixedHeight(120)
        layout.addWidget(self.mapping_table)
        
        # Mapping Controls
        mapping_btns = QHBoxLayout()
        btn_add = QPushButton("+ Adicionar")
        btn_add.clicked.connect(self._add_mapping_row)
        btn_remove = QPushButton("- Remover")
        btn_remove.clicked.connect(self._remove_mapping_row)
        mapping_btns.addWidget(btn_add)
        mapping_btns.addWidget(btn_remove)
        layout.addLayout(mapping_btns)

        # Save Config Button
        self.btn_save_config = QPushButton("SALVAR CONFIGURAÇÃO")
        self.btn_save_config.setObjectName("SecondaryButton")
        self.btn_save_config.clicked.connect(self._handle_save_config)
        layout.addWidget(self.btn_save_config)

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

    def _create_file_selector(self, label_text, parent_layout):
        label = QLabel(label_text)
        label.setObjectName("FieldLabel")
        parent_layout.addWidget(label)

        h_layout = QHBoxLayout()
        line_edit = QLineEdit()
        line_edit.setReadOnly(True)
        btn_browse = QPushButton("Procurar")
        btn_browse.setObjectName("BrowseButton")
        btn_browse.setFixedWidth(80)
        btn_browse.clicked.connect(lambda: self._browse_file(line_edit))

        h_layout.addWidget(line_edit)
        h_layout.addWidget(btn_browse)
        parent_layout.addLayout(h_layout)
        return line_edit

    def _browse_file(self, line_edit):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Selecionar Arquivo Excel", "", "Excel Files (*.xlsx *.xls)"
        )
        if file_path:
            line_edit.setText(file_path)

    def _add_mapping_row(self, aba="", celula=""):
        row = self.mapping_table.rowCount()
        self.mapping_table.insertRow(row)
        self.mapping_table.setItem(row, 0, QTableWidgetItem(aba))
        self.mapping_table.setItem(row, 1, QTableWidgetItem(celula))

    def _remove_mapping_row(self):
        row_count = self.mapping_table.rowCount()
        if row_count > 0:
            self.mapping_table.removeRow(row_count - 1)

    def _handle_save_config(self):
        # Coleta mapeamento da tabela
        mapeamento = {}
        for row in range(self.mapping_table.rowCount()):
            item_aba = self.mapping_table.item(row, 0)
            item_celula = self.mapping_table.item(row, 1)
            if item_aba and item_celula:
                aba = item_aba.text().strip()
                celula = item_celula.text().strip()
                if aba and celula:
                    mapeamento[aba] = celula

        config_data = {
            "arquivos": {
                "dados_origem": self.input_origin.text(),
                "user_template": self.input_template.text()
            },
            "mapeamento": mapeamento
        }
        self.config_save_requested.emit(config_data)

    def set_config_values(self, origin, template, mapeamento=None):
        self.input_origin.setText(origin)
        self.input_template.setText(template)
        
        if mapeamento:
            self.mapping_table.setRowCount(0)
            for aba, celula in mapeamento.items():
                self._add_mapping_row(aba, celula)

    def update_progress(self, value):
        self.progress_bar.setValue(value)

    def _handle_button_click(self):
        """Decide qual sinal emitir baseado no estado atual"""
        if self._in_error_state:
            self.revalidate_requested.emit()
        else:
            self.start_requested.emit()

    def set_validation_state(self, sucesso: bool, mensagem: str = ""):
        """Configura o botão e o log baseado no resultado da validação"""
        if sucesso:
            self._in_error_state = False
            self.btn_action.setText("GERAR RELATÓRIO MENSAL")
            self.btn_action.setEnabled(True)
            self.progress_bar.setRange(0, 100)
            self.progress_bar.setValue(0)
        else:
            self._in_error_state = True
            self.btn_action.setText("REVALIDAR ARQUIVOS")
            self.btn_action.setEnabled(True) # Habilita para permitir tentar novamente
            self.progress_bar.setRange(0, 100)
            self.progress_bar.setValue(0)
        
        if mensagem:
            self.log(mensagem)

    def set_busy(self, busy: bool, message: str = "Processando..."):
        """Estado de carregamento (botão desabilitado, barra infinita)"""
        self.btn_action.setEnabled(not busy)
        if busy:
            self.btn_action.setText(message)
            self.progress_bar.setRange(0, 0)
        else:
            # Ao sair do busy, o estado deve ser definido por set_validation_state
            pass

    def set_progress_success(self):
        """Define progresso como 100% no sucesso"""
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(100)
        self.btn_action.setText("RELATÓRIO GERADO!")

    def log(self, message: str):
        self.log_console.log(message)

    def clear_log(self):
        self.log_console.clear()

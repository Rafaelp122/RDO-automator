from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QFileDialog
from PySide6.QtCore import Signal, Qt

class FileSelector(QWidget):
    """
    Componente reutilizável para seleção de arquivos com label, campo de texto e botão procurar.
    """
    file_selected = Signal(str)

    def __init__(self, label_text, parent=None):
        super().__init__(parent)
        self._setup_ui(label_text)

    def _setup_ui(self, label_text):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)

        self.label = QLabel(label_text)
        self.label.setObjectName("FieldLabel")
        layout.addWidget(self.label)

        h_layout = QHBoxLayout()
        self.line_edit = QLineEdit()
        self.line_edit.setReadOnly(True)
        
        self.btn_browse = QPushButton("Procurar")
        self.btn_browse.setObjectName("BrowseButton")
        self.btn_browse.setFixedWidth(80)
        self.btn_browse.setCursor(Qt.PointingHandCursor)
        self.btn_browse.clicked.connect(self._browse_file)

        h_layout.addWidget(self.line_edit)
        h_layout.addWidget(self.btn_browse)
        layout.addLayout(h_layout)

    def _browse_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Selecionar Arquivo Excel", "", "Excel Files (*.xlsx *.xls)"
        )
        if file_path:
            self.file_selected.emit(file_path)

    def text(self):
        return self.line_edit.text()

    def setText(self, text):
        self.line_edit.setText(text)

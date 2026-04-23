from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QTextEdit

class LogView(QWidget):
    def __init__(self, title="LOG DE PROCESSAMENTO", initial_text="Pronto.", parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        self.label = QLabel(title)
        self.label.setObjectName("SectionLabel")
        layout.addWidget(self.label)

        self.text_area = QTextEdit()
        self.text_area.setObjectName("LogArea")
        self.text_area.setReadOnly(True)
        self.text_area.setPlainText(f"{initial_text}\n")
        layout.addWidget(self.text_area)

    def log(self, message):
        """Adiciona uma mensagem ao console de log"""
        self.text_area.append(f"> {message}")
        self.text_area.ensureCursorVisible()

    def clear(self):
        """Limpa o console"""
        self.text_area.clear()

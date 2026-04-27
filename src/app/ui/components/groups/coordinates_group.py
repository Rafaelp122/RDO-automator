from PySide6.QtWidgets import QGroupBox, QFormLayout, QLineEdit
from PySide6.QtCore import Signal, Qt

class CoordinatesGroup(QGroupBox):
    changed = Signal()
    def __init__(self, config):
        super().__init__("📍 Coordenadas das Células")
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.config = config
        self._init_ui()
        
    def _init_ui(self):
        layout = QFormLayout()
        
        self.input_cel_data_inicio = QLineEdit()
        self.input_cel_data_inicio.setPlaceholderText("Ex: R8")
        self.input_cel_data_inicio.editingFinished.connect(self.changed.emit)
        layout.addRow("Data Inicial:", self.input_cel_data_inicio)
        
        self.input_cel_prazo = QLineEdit()
        self.input_cel_prazo.setPlaceholderText("Ex: R9")
        self.input_cel_prazo.editingFinished.connect(self.changed.emit)
        layout.addRow("Prazo (Dias):", self.input_cel_prazo)
        
        self.input_cel_data_final = QLineEdit()
        self.input_cel_data_final.setPlaceholderText("Ex: R10")
        self.input_cel_data_final.editingFinished.connect(self.changed.emit)
        layout.addRow("Data Final:", self.input_cel_data_final)
        
        self.input_cel_data_atual = QLineEdit()
        self.input_cel_data_atual.setPlaceholderText("Ex: E3")
        self.input_cel_data_atual.editingFinished.connect(self.changed.emit)
        layout.addRow("Data (Aba):", self.input_cel_data_atual)
        
        self.input_cel_tempo_decorrido = QLineEdit()
        self.input_cel_tempo_decorrido.setPlaceholderText("Ex: R11")
        self.input_cel_tempo_decorrido.editingFinished.connect(self.changed.emit)
        layout.addRow("Tempo Dec.:", self.input_cel_tempo_decorrido)
        
        self.setLayout(layout)
        self.refresh_ui()

    def refresh_ui(self):
        """Atualiza a interface com os dados atuais da configuração"""
        pos = self.config.posicoes
        self.input_cel_data_inicio.setText(pos.celula_data_inicio)
        self.input_cel_prazo.setText(pos.celula_prazo_dias)
        self.input_cel_data_final.setText(pos.celula_data_final)
        self.input_cel_data_atual.setText(pos.celula_data_atual)
        self.input_cel_tempo_decorrido.setText(pos.celula_tempo_decorrido)

    def set_config(self, config):
        """Atualiza a referência de configuração"""
        self.config = config
        
    def update_config(self, config):
        pos = config.posicoes
        pos.celula_data_inicio = self.input_cel_data_inicio.text().strip().upper()
        pos.celula_prazo_dias = self.input_cel_prazo.text().strip().upper()
        pos.celula_data_final = self.input_cel_data_final.text().strip().upper()
        pos.celula_data_atual = self.input_cel_data_atual.text().strip().upper()
        pos.celula_tempo_decorrido = self.input_cel_tempo_decorrido.text().strip().upper()

    def set_field_errors(self, field_errors: dict):
        """Aplica estilo de erro aos inputs de coordenada"""
        mapping = {
            "celula_data_inicio": self.input_cel_data_inicio,
            "celula_prazo_dias": self.input_cel_prazo,
            "celula_data_final": self.input_cel_data_final,
            "celula_data_atual": self.input_cel_data_atual,
            "celula_tempo_decorrido": self.input_cel_tempo_decorrido
        }
        for field, widget in mapping.items():
            if field in field_errors:
                self._apply_error_style(widget, field_errors[field])

    def clear_errors(self):
        """Limpa erros de todos os inputs"""
        widgets = [
            self.input_cel_data_inicio, self.input_cel_prazo,
            self.input_cel_data_final, self.input_cel_data_atual,
            self.input_cel_tempo_decorrido
        ]
        for w in widgets:
            w.setProperty("error", False)
            w.setToolTip("")
            w.style().unpolish(w)
            w.style().polish(w)

    def _apply_error_style(self, widget, message):
        widget.setProperty("error", True)
        widget.setToolTip(message)
        widget.style().unpolish(widget)
        widget.style().polish(widget)

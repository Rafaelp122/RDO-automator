from PySide6.QtWidgets import QGroupBox, QFormLayout, QLineEdit
from PySide6.QtCore import Signal, Qt

class CoordinatesGroup(QGroupBox):
    changed = Signal()
    def __init__(self, config):
        super().__init__("📍 Coordenadas das Células")
        self.setAlignment(Qt.AlignCenter)
        self.config = config
        self._init_ui()
        
    def _init_ui(self):
        layout = QFormLayout()
        
        self.input_cel_data_inicio = QLineEdit(self.config.get('posicoes', {}).get('celula_data_inicio', ''))
        self.input_cel_data_inicio.setPlaceholderText("Ex: R8")
        self.input_cel_data_inicio.editingFinished.connect(self.changed.emit)
        layout.addRow("Data Inicial:", self.input_cel_data_inicio)
        
        self.input_cel_prazo = QLineEdit(self.config.get('posicoes', {}).get('celula_prazo_dias', ''))
        self.input_cel_prazo.setPlaceholderText("Ex: R9")
        self.input_cel_prazo.editingFinished.connect(self.changed.emit)
        layout.addRow("Prazo (Dias):", self.input_cel_prazo)
        
        self.input_cel_data_final = QLineEdit(self.config.get('posicoes', {}).get('celula_data_final', ''))
        self.input_cel_data_final.setPlaceholderText("Ex: R10")
        self.input_cel_data_final.editingFinished.connect(self.changed.emit)
        layout.addRow("Data Final:", self.input_cel_data_final)
        
        self.input_cel_data_atual = QLineEdit(self.config.get('posicoes', {}).get('celula_data_atual', ''))
        self.input_cel_data_atual.setPlaceholderText("Ex: E3")
        self.input_cel_data_atual.editingFinished.connect(self.changed.emit)
        layout.addRow("Data (Aba):", self.input_cel_data_atual)
        
        self.input_cel_tempo_decorrido = QLineEdit(self.config.get('posicoes', {}).get('celula_tempo_decorrido', ''))
        self.input_cel_tempo_decorrido.setPlaceholderText("Ex: R11")
        self.input_cel_tempo_decorrido.editingFinished.connect(self.changed.emit)
        layout.addRow("Tempo Dec.:", self.input_cel_tempo_decorrido)
        
        self.setLayout(layout)
        
    def update_config(self, config):
        pos = config.setdefault('posicoes', {})
        pos['celula_data_inicio'] = self.input_cel_data_inicio.text().strip().upper()
        pos['celula_prazo_dias'] = self.input_cel_prazo.text().strip().upper()
        pos['celula_data_final'] = self.input_cel_data_final.text().strip().upper()
        pos['celula_data_atual'] = self.input_cel_data_atual.text().strip().upper()
        pos['celula_tempo_decorrido'] = self.input_cel_tempo_decorrido.text().strip().upper()

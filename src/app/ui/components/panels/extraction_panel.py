from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QGroupBox, QPlainTextEdit, QPushButton
)
from PySide6.QtCore import Signal, Qt

class ExtractionPanel(QGroupBox):
    config_changed = Signal()

    def __init__(self, config):
        super().__init__("📝 Extração Dinâmica")
        self.config = config
        self.chips = []
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout()
        
        # Chips Input Area
        layout.addWidget(QLabel("Colunas Dinâmicas (digite e pressione Enter):"))
        self.input_chip = QLineEdit() 
        self.input_chip.setPlaceholderText("Ex: Bairro, Serviço...")
        self.input_chip.returnPressed.connect(self._add_chip)
        layout.addWidget(self.input_chip)
        
        self.chips_layout = QHBoxLayout()
        self.chips_layout.setAlignment(Qt.AlignLeft)
        layout.addLayout(self.chips_layout)
        
        # Load existing chips
        extracao = self.config.get('extração', {})
        for col in extracao.get('colunas', []):
            self._create_chip_widget(col)
        
        # Formato Final
        layout.addWidget(QLabel("Template de Formato Final:"))
        self.text_formato = QPlainTextEdit()
        self.text_formato.setObjectName("TemplateEditor")
        self.text_formato.setPlaceholderText("Ex: {Serviço:nos} serviço{Serviço:s} realizado{Serviço:s}: {Serviço}.")
        self.text_formato.setPlainText(extracao.get('formato_final', ''))
        self.text_formato.textChanged.connect(self._save_config)
        self.text_formato.setMaximumHeight(80)
        layout.addWidget(self.text_formato)
        
        # Separadores
        sep_layout = QHBoxLayout()
        sep_layout.addWidget(QLabel("Separador de lista:"))
        self.input_sep = QLineEdit(extracao.get('separador_lista', ', '))
        self.input_sep.editingFinished.connect(self._save_config)
        sep_layout.addWidget(self.input_sep)
        
        sep_layout.addWidget(QLabel("Conector final:"))
        self.input_con = QLineEdit(extracao.get('conector_final', ' e '))
        self.input_con.editingFinished.connect(self._save_config)
        sep_layout.addWidget(self.input_con)
        
        layout.addLayout(sep_layout)
        self.setLayout(layout)

    def _add_chip(self):
        text = self.input_chip.text().strip()
        parts = [p.strip() for p in text.split(',') if p.strip()]
        for p in parts:
            if p not in self.chips:
                self.chips.append(p)
                self._create_chip_widget(p)
        self.input_chip.clear()
        self._save_config()

    def _create_chip_widget(self, text):
        if text not in self.chips:
            self.chips.append(text)
            
        chip_widget = QWidget()
        chip_widget.setObjectName("Chip")
        chip_widget.setStyleSheet("""
            QWidget#Chip {
                background-color: #3F51B5;
                color: white;
                border-radius: 12px;
            }
            QLabel { color: white; background: transparent; padding: 4px; }
            QPushButton { 
                color: white; background: transparent; 
                border: none; font-weight: bold; padding: 4px;
            }
            QPushButton:hover { color: #FFCDD2; }
        """)
        
        clayout = QHBoxLayout(chip_widget)
        clayout.setContentsMargins(4, 0, 4, 0)
        
        lbl = QLabel(text)
        btn = QPushButton("x")
        btn.setFixedSize(20, 20)
        
        clayout.addWidget(lbl)
        clayout.addWidget(btn)
        
        def remove_chip():
            self.chips.remove(text)
            chip_widget.deleteLater()
            self._save_config()
            
        btn.clicked.connect(remove_chip)
        self.chips_layout.addWidget(chip_widget)

    def _save_config(self):
        extracao = self.config.setdefault('extração', {})
        extracao['colunas'] = self.chips
        extracao['formato_final'] = self.text_formato.toPlainText()
        extracao['separador_lista'] = self.input_sep.text()
        extracao['conector_final'] = self.input_con.text()
        self.config_changed.emit()

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
        self._is_updating = False
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
        self.chips_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        layout.addLayout(self.chips_layout)
        
        # Load existing chips
        for col in self.config.extracao.colunas:
            self._create_chip_widget(col)
        
        # Formato Final
        layout.addWidget(QLabel("Template de Formato Final:"))
        self.text_formato = QPlainTextEdit()
        self.text_formato.setObjectName("TemplateEditor")
        self.text_formato.setPlaceholderText("Ex: {Serviço:nos} serviço{Serviço:s} realizado{Serviço:s}: {Serviço}.")
        self.text_formato.setPlainText(self.config.extracao.formato_final)
        self.text_formato.textChanged.connect(self._save_config)
        self.text_formato.setMaximumHeight(80)
        layout.addWidget(self.text_formato)
        
        # Separadores
        sep_layout = QHBoxLayout()
        sep_layout.addWidget(QLabel("Separador de lista:"))
        self.input_sep = QLineEdit(self.config.extracao.separador_lista)
        self.input_sep.editingFinished.connect(self._save_config)
        sep_layout.addWidget(self.input_sep)
        
        sep_layout.addWidget(QLabel("Conector final:"))
        self.input_con = QLineEdit(self.config.extracao.conector_final)
        self.input_con.editingFinished.connect(self._save_config)
        sep_layout.addWidget(self.input_con)
        
        layout.addLayout(sep_layout)
        self.setLayout(layout)
        self.refresh_ui()

    def refresh_ui(self):
        """Atualiza a interface com os dados atuais da configuração"""
        self._is_updating = True
        # Limpar chips atuais
        self.chips = []
        while self.chips_layout.count():
            item = self.chips_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # Recriar chips
        for col in self.config.extracao.colunas:
            self._create_chip_widget(col)
            
        # Atualizar textos
        self.text_formato.setPlainText(self.config.extracao.formato_final)
        self.input_sep.setText(self.config.extracao.separador_lista)
        self.input_con.setText(self.config.extracao.conector_final)
        self._is_updating = False

    def set_config(self, config):
        """Atualiza a referência de configuração"""
        self.config = config

    def _add_chip(self):
        if self._is_updating:
            return
        text = self.input_chip.text().strip()
        # Removido o strip() interno de cada parte para preservar espaços nos nomes das colunas
        parts = [p for p in text.split(',') if p]
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
        
        clayout = QHBoxLayout(chip_widget)
        clayout.setContentsMargins(8, 0, 4, 0)
        clayout.setSpacing(2)
        
        lbl = QLabel(text)
        btn = QPushButton("x")
        btn.setFixedSize(18, 18)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        
        clayout.addWidget(lbl)
        clayout.addWidget(btn)
        
        def remove_chip():
            if text in self.chips:
                self.chips.remove(text)
            chip_widget.deleteLater()
            self._save_config()
            
        btn.clicked.connect(remove_chip)
        self.chips_layout.addWidget(chip_widget)

    def save_config(self, config=None):
        """Sincroniza os dados da interface com o objeto config fornecido ou interno"""
        target_config = config if config else self.config
        extracao = target_config.extracao
        extracao.colunas = self.chips
        extracao.formato_final = self.text_formato.toPlainText()
        extracao.separador_lista = self.input_sep.text()
        extracao.conector_final = self.input_con.text()

    def _save_config(self):
        if self._is_updating:
            return
        self.save_config()
        self.config_changed.emit()

    def set_field_errors(self, field_errors: dict):
        """Aplica estilo de erro aos campos deste painel"""
        if "formato_final" in field_errors:
            self._apply_error_style(self.text_formato, field_errors["formato_final"])
        
        if "colunas" in field_errors:
            # Destaca a área de input de colunas
            self._apply_error_style(self.input_chip, field_errors["colunas"])

    def clear_errors(self):
        """Remove estilos de erro de todos os campos do painel"""
        for widget in [self.text_formato, self.input_chip, self.input_sep, self.input_con]:
            widget.setProperty("error", False)
            widget.setToolTip("")
            widget.style().unpolish(widget)
            widget.style().polish(widget)

    def _apply_error_style(self, widget, message):
        widget.setProperty("error", True)
        widget.setToolTip(message)
        widget.style().unpolish(widget)
        widget.style().polish(widget)

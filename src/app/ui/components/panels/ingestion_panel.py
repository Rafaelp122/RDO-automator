import os
import shutil
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QFileDialog, QSpinBox, QGroupBox
)
from PySide6.QtCore import Signal
from src.app.core.logger import logger

class IngestionPanel(QGroupBox):
    config_changed = Signal()

    def __init__(self, config):
        super().__init__("📥 Ingestão de Arquivos")
        self.config = config
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout()
        
        # Source File
        src_layout = QHBoxLayout()
        self.lbl_src = QLabel("Planilha de Origem: Não selecionada")
        btn_src = QPushButton("Procurar")
        btn_src.clicked.connect(self._select_source)
        src_layout.addWidget(self.lbl_src)
        src_layout.addWidget(btn_src)
        
        # Template File
        tmpl_layout = QHBoxLayout()
        self.lbl_tmpl = QLabel("Template Base: Padrão do Sistema")
        btn_tmpl = QPushButton("Procurar")
        btn_tmpl.clicked.connect(self._select_template)
        tmpl_layout.addWidget(self.lbl_tmpl)
        tmpl_layout.addWidget(btn_tmpl)
        
        # Header Row
        hdr_layout = QHBoxLayout()
        hdr_layout.addWidget(QLabel("Linha do Cabeçalho (0-index):"))
        self.spin_header = QSpinBox()
        self.spin_header.setMinimum(0)
        self.spin_header.setMaximum(100)
        self.spin_header.setValue(self.config.get('arquivos', {}).get('linha_cabecalho', 0))
        self.spin_header.valueChanged.connect(self._update_header)
        hdr_layout.addWidget(self.spin_header)
        hdr_layout.addStretch()
        
        layout.addLayout(src_layout)
        layout.addLayout(tmpl_layout)
        layout.addLayout(hdr_layout)
        self.setLayout(layout)
        self._update_labels()

    def _truncate(self, text, length=35):
        return (text[:length] + '...') if len(text) > length else text

    def _update_labels(self):
        src = self.config.get('arquivos', {}).get('dados_origem')
        if src:
            name = self._truncate(os.path.basename(src))
            self.lbl_src.setText(f"Planilha de Origem: 🟢 {name}")
            self.lbl_src.setToolTip(src)
            
        tmpl = self.config.get('arquivos', {}).get('user_template')
        if tmpl:
            name = self._truncate(os.path.basename(tmpl))
            self.lbl_tmpl.setText(f"Template Base: 🟢 {name}")
            self.lbl_tmpl.setToolTip(tmpl)

    def _select_source(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Selecionar Planilha", "", "Excel (*.xlsx *.xls)")
        if file_path:
            dest = os.path.join("data", "input", os.path.basename(file_path))
            os.makedirs(os.path.dirname(dest), exist_ok=True)
            try:
                shutil.copy2(file_path, dest)
                logger.info(f"Arquivo importado: {dest}")
                self.config.setdefault('arquivos', {})['dados_origem'] = dest
                self._update_labels()
                self.config_changed.emit()
            except Exception as e:
                logger.error(f"Erro ao copiar: {e}")

    def _select_template(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Selecionar Template", "", "Excel (*.xlsx *.xls)")
        if file_path:
            dest = os.path.join("data", "input", os.path.basename(file_path))
            os.makedirs(os.path.dirname(dest), exist_ok=True)
            try:
                shutil.copy2(file_path, dest)
                logger.info(f"Template importado: {dest}")
                self.config.setdefault('arquivos', {})['user_template'] = dest
                self._update_labels()
                self.config_changed.emit()
            except Exception as e:
                logger.error(f"Erro ao copiar template: {e}")

    def _update_header(self, value):
        self.config.setdefault('arquivos', {})['linha_cabecalho'] = value
        self.config_changed.emit()

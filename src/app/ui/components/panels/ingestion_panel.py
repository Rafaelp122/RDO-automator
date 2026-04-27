import os
import shutil
from pathlib import Path
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QFileDialog, QSpinBox, QGroupBox
)
from PySide6.QtCore import Signal, Qt
from src.app.core.logger import logger
from src.app.core.constants import INPUT_DIR

class IngestionPanel(QGroupBox):
    config_changed = Signal()

    def __init__(self, config):
        super().__init__("📥 Ingestão de Arquivos")
        self.config = config
        self._is_updating = False
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout()
        
        # Source File
        src_layout = QHBoxLayout()
        self.lbl_src = QLabel("Planilha de Origem: Não selecionada")
        btn_src = QPushButton("Procurar")
        btn_src.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_src.clicked.connect(self._select_source)
        src_layout.addWidget(self.lbl_src)
        src_layout.addWidget(btn_src)
        
        # Template File
        tmpl_layout = QHBoxLayout()
        self.lbl_tmpl = QLabel("Template Base: Padrão do Sistema")
        btn_tmpl = QPushButton("Procurar")
        btn_tmpl.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_tmpl.clicked.connect(self._select_template)
        tmpl_layout.addWidget(self.lbl_tmpl)
        tmpl_layout.addWidget(btn_tmpl)
        
        # Header Row
        hdr_layout = QHBoxLayout()
        hdr_layout.addWidget(QLabel("Linha do Cabeçalho (0-index):"))
        self.spin_header = QSpinBox()
        self.spin_header.setMinimum(0)
        self.spin_header.setMaximum(100)
        self.spin_header.setValue(self.config.arquivos.linha_cabecalho)
        self.spin_header.valueChanged.connect(self._update_header)
        hdr_layout.addWidget(self.spin_header)
        hdr_layout.addStretch()
        
        layout.addLayout(src_layout)
        layout.addLayout(tmpl_layout)
        layout.addLayout(hdr_layout)
        self.setLayout(layout)
        self.refresh_ui()

    def refresh_ui(self):
        """Atualiza a interface com os dados atuais da configuração"""
        self._is_updating = True
        self.spin_header.setValue(self.config.arquivos.linha_cabecalho)
        self._update_labels()
        self._is_updating = False

    def set_config(self, config):
        """Atualiza a referência de configuração"""
        self.config = config

    def _truncate(self, text, length=35):
        return (text[:length] + '...') if len(text) > length else text

    def _update_labels(self):
        src = self.config.arquivos.dados_origem
        if src:
            name = self._truncate(Path(src).name)
            self.lbl_src.setText(f"Planilha de Origem: 🟢 {name}")
            self.lbl_src.setToolTip(src)
            
        tmpl = self.config.arquivos.user_template
        if tmpl:
            name = self._truncate(Path(tmpl).name)
            self.lbl_tmpl.setText(f"Template Base: 🟢 {name}")
            self.lbl_tmpl.setToolTip(tmpl)

    def _select_source(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Selecionar Planilha", "", "Excel (*.xlsx *.xls)")
        if file_path:
            try:
                # Calcula caminho relativo à raiz do projeto
                rel_path = os.path.relpath(file_path, os.getcwd())
                self.config.arquivos.dados_origem = rel_path
                logger.info(f"Planilha selecionada: {rel_path}")
                self._update_labels()
                self.config_changed.emit()
            except Exception as e:
                logger.error(f"Erro ao processar caminho da planilha: {e}")

    def _select_template(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Selecionar Template", "", "Excel (*.xlsx *.xls)")
        if file_path:
            try:
                # Calcula caminho relativo à raiz do projeto
                rel_path = os.path.relpath(file_path, os.getcwd())
                self.config.arquivos.user_template = rel_path
                logger.info(f"Template selecionado: {rel_path}")
                self._update_labels()
                self.config_changed.emit()
            except Exception as e:
                logger.error(f"Erro ao processar caminho do template: {e}")

    def _update_header(self, value):
        if self._is_updating:
            return
        self.config.arquivos.linha_cabecalho = value
        self.config_changed.emit()

    def save_config(self, config=None):
        """Sincroniza os dados da interface com o objeto config fornecido ou interno"""
        if self._is_updating:
            return
            
        target_config = config if config else self.config
        target_config.arquivos.linha_cabecalho = self.spin_header.value()

    def _save_config(self):
        if self._is_updating:
            return
        self.save_config()

    def set_field_errors(self, field_errors: dict):
        """Aplica estilo de erro aos campos deste painel"""
        if "dados_origem" in field_errors:
            self._apply_error_style(self.lbl_src, field_errors["dados_origem"])
        
        if "template_ativo" in field_errors or "user_template" in field_errors:
            self._apply_error_style(self.lbl_tmpl, field_errors.get("template_ativo") or field_errors.get("user_template"))

    def clear_errors(self):
        """Remove estilos de erro de todos os campos do painel"""
        for widget in [self.lbl_src, self.lbl_tmpl, self.spin_header]:
            widget.setProperty("error", False)
            widget.setToolTip("")
            widget.style().unpolish(widget)
            widget.style().polish(widget)

    def _apply_error_style(self, widget, message):
        widget.setProperty("error", True)
        widget.setToolTip(message)
        widget.style().unpolish(widget)
        widget.style().polish(widget)

import os
import subprocess
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
    QProgressBar, QGroupBox, QLabel
)
from PySide6.QtCore import Signal
from src.app.ui.components.widgets.log_view import LogView

class ControlPanel(QGroupBox):
    generate_requested = Signal()
    import_requested = Signal()
    export_requested = Signal()

    def __init__(self):
        super().__init__("🚀 Controle e Execução")
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout()
        
        self.status_label = QLabel("🟢 Sistema Pronto")
        self.status_label.setStyleSheet("font-weight: bold; color: #3F51B5;")
        layout.addWidget(self.status_label)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # Terminal Retrátil
        self.log_view = LogView(title="Console")
        self.log_view.setVisible(False)
        self.log_view.setMinimumHeight(250)
        
        self.btn_toggle_log = QPushButton("Mostrar Console")
        self.btn_toggle_log.setObjectName("SecondaryButton")
        self.btn_toggle_log.setCheckable(True)
        self.btn_toggle_log.toggled.connect(self._toggle_log)
        
        self.btn_import = QPushButton("Importar Configuração")
        self.btn_import.setObjectName("SecondaryButton")
        self.btn_import.clicked.connect(self.import_requested.emit)
        
        self.btn_export = QPushButton("Exportar Configuração")
        self.btn_export.setObjectName("SecondaryButton")
        self.btn_export.clicked.connect(self.export_requested.emit)
        
        tools_layout = QHBoxLayout()
        tools_layout.addWidget(self.btn_toggle_log)
        tools_layout.addWidget(self.btn_import)
        tools_layout.addWidget(self.btn_export)
        
        layout.addLayout(tools_layout)
        layout.addWidget(self.log_view)
        
        # Actions
        actions_layout = QHBoxLayout()
        
        self.btn_generate = QPushButton("GERAR DIÁRIO DE OBRA")
        # self.btn_generate.setStyleSheet("background-color: #3F51B5; color: white; font-weight: bold; padding: 10px; border-radius: 6px;")
        self.btn_generate.clicked.connect(self.generate_requested.emit)
        
        self.btn_open_folder = QPushButton("📁 Abrir Pasta")
        self.btn_open_folder.setEnabled(False)
        self.btn_open_folder.clicked.connect(self._open_output_folder)
        
        actions_layout.addWidget(self.btn_generate)
        actions_layout.addWidget(self.btn_open_folder)
        
        layout.addLayout(actions_layout)
        self.setLayout(layout)

    def _toggle_log(self, checked):
        self.log_view.setVisible(checked)
        self.btn_toggle_log.setText("Ocultar Console" if checked else "Mostrar Console")

    def set_status(self, text, is_error=False):
        color = "#D32F2F" if is_error else "#3F51B5"
        self.status_label.setText(text)
        self.status_label.setStyleSheet(f"font-weight: bold; color: {color};")

    def set_progress(self, value):
        if value > 0 and value < 100:
            self.progress_bar.setVisible(True)
        self.progress_bar.setValue(value)
        if value == 100:
            self.btn_open_folder.setEnabled(True)
            self.progress_bar.setVisible(False)

    def log(self, message):
        self.log_view.log(message)

    def set_generating(self, is_generating):
        self.btn_generate.setEnabled(not is_generating)
        if is_generating:
            self.progress_bar.setVisible(True)
            self.progress_bar.setValue(0)
            self.btn_open_folder.setEnabled(False)
            self.set_status("⏳ Processando...")
            self.log_view.clear()

    def _open_output_folder(self):
        output_dir = os.path.join(os.getcwd(), "data", "output")
        if os.path.exists(output_dir):
            if os.name == 'nt':
                os.startfile(output_dir)
            elif os.name == 'posix':
                subprocess.Popen(['xdg-open', output_dir])

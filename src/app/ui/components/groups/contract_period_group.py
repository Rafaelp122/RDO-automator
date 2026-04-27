from PySide6.QtWidgets import QGroupBox, QFormLayout, QDateEdit, QSpinBox
from PySide6.QtCore import Signal, QDate, Qt

class ContractPeriodGroup(QGroupBox):
    changed = Signal()
    def __init__(self, config):
        super().__init__("📋 Dados do Contrato e Período")
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.config = config
        self._init_ui()
        
    def _init_ui(self):
        layout = QFormLayout()
        
        # Data Inicial
        self.date_inicio = QDateEdit()
        self.date_inicio.setCalendarPopup(True)
        self.date_inicio.dateChanged.connect(lambda *a: self.changed.emit())
        layout.addRow("Data Inicial:", self.date_inicio)
        
        # Prazo (Dias)
        self.spin_prazo = QSpinBox()
        self.spin_prazo.setMaximum(9999)
        self.spin_prazo.valueChanged.connect(lambda *a: self.changed.emit())
        layout.addRow("Prazo (Dias):", self.spin_prazo)
        
        # Mês Atual
        self.spin_mes = QSpinBox()
        self.spin_mes.setRange(1, 12)
        self.spin_mes.valueChanged.connect(lambda *a: self.changed.emit())
        layout.addRow("Mês Atual:", self.spin_mes)
        
        # Ano Atual
        self.spin_ano = QSpinBox()
        self.spin_ano.setRange(2000, 2100)
        self.spin_ano.valueChanged.connect(lambda *a: self.changed.emit())
        layout.addRow("Ano Atual:", self.spin_ano)
        
        self.setLayout(layout)
        self.refresh_ui()
        
    def refresh_ui(self):
        """Atualiza a interface com os dados atuais da configuração"""
        iso_data = self.config.contrato.data_inicio
        if iso_data:
            self.date_inicio.setDate(QDate.fromString(iso_data, "yyyy-MM-dd"))
        else:
            self.date_inicio.setDate(QDate.currentDate())
        
        self.spin_prazo.setValue(self.config.contrato.prazo_dias)
        self.spin_mes.setValue(self.config.projeto.mes)
        self.spin_ano.setValue(self.config.projeto.ano)

    def set_config(self, config):
        """Atualiza a referência de configuração"""
        self.config = config

    def update_config(self, config):
        config.contrato.data_inicio = self.date_inicio.date().toString("yyyy-MM-dd")
        config.contrato.prazo_dias = self.spin_prazo.value()
        config.projeto.mes = self.spin_mes.value()
        config.projeto.ano = self.spin_ano.value()

    def set_field_errors(self, field_errors: dict):
        """Aplica estilo de erro aos campos de contrato (se houver)"""
        # Exemplo: se houver erro na data ou prazo
        if "data_inicio" in field_errors:
            self._apply_error_style(self.date_inicio, field_errors["data_inicio"])
        if "prazo_dias" in field_errors:
            self._apply_error_style(self.spin_prazo, field_errors["prazo_dias"])

    def clear_errors(self):
        """Limpa erros dos campos"""
        for w in [self.date_inicio, self.spin_prazo, self.spin_mes, self.spin_ano]:
            w.setProperty("error", False)
            w.setToolTip("")
            w.style().unpolish(w)
            w.style().polish(w)

    def _apply_error_style(self, widget, message):
        widget.setProperty("error", True)
        widget.setToolTip(message)
        widget.style().unpolish(widget)
        widget.style().polish(widget)

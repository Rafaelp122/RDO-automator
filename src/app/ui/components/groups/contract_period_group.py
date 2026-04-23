from PySide6.QtWidgets import QGroupBox, QFormLayout, QDateEdit, QSpinBox
from PySide6.QtCore import Signal, QDate, Qt

class ContractPeriodGroup(QGroupBox):
    changed = Signal()
    def __init__(self, config):
        super().__init__("📋 Dados do Contrato e Período")
        self.setAlignment(Qt.AlignCenter)
        self.config = config
        self._init_ui()
        
    def _init_ui(self):
        layout = QFormLayout()
        
        # Data Inicial
        self.date_inicio = QDateEdit()
        self.date_inicio.setCalendarPopup(True)
        iso_data = self.config.get('contrato', {}).get('data_inicio')
        if iso_data:
            self.date_inicio.setDate(QDate.fromString(iso_data, "yyyy-MM-dd"))
        else:
            self.date_inicio.setDate(QDate.currentDate())
        self.date_inicio.dateChanged.connect(lambda *a: self.changed.emit())
        layout.addRow("Data Inicial:", self.date_inicio)
        
        # Prazo (Dias)
        self.spin_prazo = QSpinBox()
        self.spin_prazo.setMaximum(9999)
        self.spin_prazo.setValue(self.config.get('contrato', {}).get('prazo_dias', 365))
        self.spin_prazo.valueChanged.connect(lambda *a: self.changed.emit())
        layout.addRow("Prazo (Dias):", self.spin_prazo)
        
        # Mês Atual
        self.spin_mes = QSpinBox()
        self.spin_mes.setRange(1, 12)
        self.spin_mes.setValue(self.config.get('projeto', {}).get('mes', QDate.currentDate().month()))
        self.spin_mes.valueChanged.connect(lambda *a: self.changed.emit())
        layout.addRow("Mês Atual:", self.spin_mes)
        
        # Ano Atual
        self.spin_ano = QSpinBox()
        self.spin_ano.setRange(2000, 2100)
        self.spin_ano.setValue(self.config.get('projeto', {}).get('ano', QDate.currentDate().year()))
        self.spin_ano.valueChanged.connect(lambda *a: self.changed.emit())
        layout.addRow("Ano Atual:", self.spin_ano)
        
        self.setLayout(layout)
        
    def update_config(self, config):
        config.setdefault('contrato', {})['data_inicio'] = self.date_inicio.date().toString("yyyy-MM-dd")
        config['contrato']['prazo_dias'] = self.spin_prazo.value()
        config.setdefault('projeto', {})['mes'] = self.spin_mes.value()
        config['projeto']['ano'] = self.spin_ano.value()

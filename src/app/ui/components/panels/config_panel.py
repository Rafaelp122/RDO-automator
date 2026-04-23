from PySide6.QtWidgets import QGroupBox, QHBoxLayout
from PySide6.QtCore import Signal
from src.app.ui.components.groups.mapping_group import MappingGroup
from src.app.ui.components.groups.contract_period_group import ContractPeriodGroup
from src.app.ui.components.groups.coordinates_group import CoordinatesGroup


class ConfigPanel(QGroupBox):
    config_changed = Signal()

    def __init__(self, config):
        super().__init__("⚙️ Configuração Estrutural")
        self.config = config
        self._init_ui()

    def _init_ui(self):
        main_layout = QHBoxLayout()

        self.contract_group = ContractPeriodGroup(self.config)
        self.contract_group.setObjectName("BorderlessGroup")
        self.contract_group.changed.connect(self._save_config)
        main_layout.addWidget(self.contract_group, 1)

        main_layout.addWidget(self._create_separator())

        self.coords_group = CoordinatesGroup(self.config)
        self.coords_group.setObjectName("BorderlessGroup")
        self.coords_group.changed.connect(self._save_config)
        main_layout.addWidget(self.coords_group, 1)

        main_layout.addWidget(self._create_separator())

        self.mapping_group = MappingGroup()
        self.mapping_group.setObjectName("BorderlessGroup")
        self.mapping_group.set_mapping(self.config.get("mapeamento", {}))
        self.mapping_group.changed.connect(self._save_config)
        main_layout.addWidget(self.mapping_group, 1)

        self.setLayout(main_layout)

    def _create_separator(self):
        from PySide6.QtWidgets import QWidget, QVBoxLayout, QFrame

        container = QWidget()
        vbox = QVBoxLayout(container)
        vbox.setContentsMargins(0, 0, 0, 0)
        vbox.addStretch(15)

        line = QFrame()
        line.setFrameShape(QFrame.VLine)
        line.setFrameShadow(QFrame.Sunken)
        line.setStyleSheet("color: #E0E6ED; border: 1px solid #E0E6ED;")
        vbox.addWidget(line, 70)

        vbox.addStretch(15)
        return container

    def _save_config(self, *args):
        self.contract_group.update_config(self.config)
        self.coords_group.update_config(self.config)
        self.mapping_group.update_config(self.config)

        self.config_changed.emit()

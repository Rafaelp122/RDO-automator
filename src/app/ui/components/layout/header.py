from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel

class Header(QFrame):
    def __init__(self, title="Report Automator", parent=None):
        super().__init__(parent)
        self.setObjectName("Header")
        self.setFixedHeight(70)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(30, 0, 30, 0)
        
        self.title_label = QLabel(title)
        self.title_label.setObjectName("TitleLabel")
        layout.addWidget(self.title_label)
        layout.addStretch()

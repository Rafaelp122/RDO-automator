from PySide6.QtWidgets import QFrame, QVBoxLayout, QProgressBar, QPushButton, QWidget
from PySide6.QtCore import Qt, Signal, Slot
from src.app.ui.components.log_view import LogView

class ProcessingPanel(QFrame):
    """
    Painel central que encapsula a lógica visual de processamento e validação.
    """
    start_requested = Signal()
    revalidate_requested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("MainCard")
        self._in_error_state = False
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(25, 20, 25, 25)
        layout.setSpacing(10)

        # Log View
        self.log_console = LogView(initial_text="Aguardando validação inicial...")
        layout.addWidget(self.log_console)

        # Progress Bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        layout.addWidget(self.progress_bar)

        # Action Button
        self.btn_action = QPushButton("VERIFICANDO DADOS...")
        self.btn_action.setObjectName("ActionButton")
        self.btn_action.setCursor(Qt.PointingHandCursor)
        self.btn_action.setEnabled(False)
        self.btn_action.clicked.connect(self._handle_button_click)
        layout.addWidget(self.btn_action)

    def _handle_button_click(self):
        """Decide qual sinal emitir baseado no estado atual"""
        if self._in_error_state:
            self.revalidate_requested.emit()
        else:
            self.start_requested.emit()

    def set_validation_state(self, sucesso: bool, mensagem: str = ""):
        """Configura o botão e o log baseado no resultado da validação"""
        if sucesso:
            self._in_error_state = False
            self.btn_action.setText("GERAR RELATÓRIO MENSAL")
            self.btn_action.setEnabled(True)
            self.progress_bar.setRange(0, 100)
            self.progress_bar.setValue(0)
        else:
            self._in_error_state = True
            self.btn_action.setText("REVALIDAR ARQUIVOS")
            self.btn_action.setEnabled(True) # Habilita para permitir tentar novamente
            self.progress_bar.setRange(0, 100)
            self.progress_bar.setValue(0)
        
        if mensagem:
            self.log(mensagem)

    def set_busy(self, busy: bool, message: str = "Processando..."):
        """Estado de carregamento (botão desabilitado, barra infinita)"""
        self.btn_action.setEnabled(not busy)
        if busy:
            self.btn_action.setText(message)
            self.progress_bar.setRange(0, 0)
        else:
            # Ao sair do busy, o estado deve ser definido por set_validation_state
            pass

    def set_progress_success(self):
        """Define progresso como 100% no sucesso"""
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(100)
        self.btn_action.setText("RELATÓRIO GERADO!")

    def log(self, message: str):
        self.log_console.log(message)

    def clear_log(self):
        self.log_console.clear()

import sys
from PySide6.QtWidgets import QApplication
from src.app.ui.windows.main_window import MainWindow
from src.app.core.logger import setup_logger


def main():
    # Inicializa o logging globalmente
    setup_logger()

    app = QApplication(sys.argv)

    # A MainWindow da V2 já gerencia sua própria configuração e controle de fluxo
    window = MainWindow()

    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()

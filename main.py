import sys
from PySide6.QtWidgets import QApplication
from src.app.ui.controllers.main_controller import MainController
from src.app.infra.config_manager import ConfigManager
from src.app.core.logger import setup_logger


def main():
    # Inicializa o logging globalmente
    setup_logger()

    app = QApplication(sys.argv)

    # Inicializa o gerenciador de configuração
    config_manager = ConfigManager()
    config_manager.load_config()

    # Inicializa o Controller (MVC), que por sua vez cria a MainWindow (View)
    controller = MainController(config_manager)
    controller.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()

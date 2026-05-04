import sys
from pathlib import Path

# Base directories
if getattr(sys, 'frozen', False):
    # Executável via PyInstaller
    BUNDLE_DIR = Path(sys._MEIPASS)
    EXECUTABLE_DIR = Path(sys.executable).parent
else:
    # Rodando do código fonte
    BUNDLE_DIR = Path(__file__).parent.parent.parent.parent
    EXECUTABLE_DIR = BUNDLE_DIR

ROOT_DIR = BUNDLE_DIR
SRC_DIR = BUNDLE_DIR / "src"

# Diretórios que precisam de permissão de escrita ficam junto ao executável
LOG_DIR = EXECUTABLE_DIR / "logs"
DATA_DIR = EXECUTABLE_DIR / "data"
INPUT_DIR = DATA_DIR / "input"
OUTPUT_DIR = DATA_DIR / "output"

# Arquivos empacotados pelo PyInstaller
ASSETS_DIR = BUNDLE_DIR / "assets"
STYLES_DIR = SRC_DIR / "app" / "ui" / "styles"

# Ensure directories exist
for directory in [LOG_DIR, INPUT_DIR, OUTPUT_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# File names
DEFAULT_CONFIG_PATH = EXECUTABLE_DIR / "config.toml"
APP_LOG_PATH = LOG_DIR / "app.log"
DEFAULT_TEMPLATE_PATH = ASSETS_DIR / "template.xlsx"

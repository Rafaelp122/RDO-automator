import tomllib
import tomli_w
from src.app.core.logger import logger

class ConfigManager:
    """Gerencia a leitura e escrita do arquivo config.toml"""
    def __init__(self, config_path="config.toml"):
        self.config_path = config_path
        self.config = {}

    def load_config(self):
        try:
            with open(self.config_path, "rb") as f:
                self.config = tomllib.load(f)
            logger.info(f"Configuração carregada com sucesso de: {self.config_path}")
            return self.config
        except Exception as e:
            logger.error(f"Erro ao carregar configuração ({self.config_path}): {e}")
            raise

    def save_config(self, new_config=None):
        """Persiste a configuração atual no arquivo TOML"""
        if new_config:
            self.config = new_config
            
        try:
            with open(self.config_path, "wb") as f:
                tomli_w.dump(self.config, f)
            logger.info(f"Configuração salva com sucesso em: {self.config_path}")
        except Exception as e:
            logger.error(f"Erro ao salvar configuração: {e}")
            raise

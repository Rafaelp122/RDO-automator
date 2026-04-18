import tomllib

class ConfigManager:
    """Gerencia a leitura do arquivo config.toml"""
    def __init__(self, config_path="config.toml"):
        self.config_path = config_path
        self.config = {}

    def load_config(self):
        with open(self.config_path, "rb") as f:
            self.config = tomllib.load(f)
        return self.config

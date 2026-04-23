import tomllib
import tomli_w
from src.app.core.logger import logger

class ConfigManager:
    """Gerencia a leitura e escrita do arquivo config.toml"""
    def __init__(self, config_path="config.toml"):
        self.config_path = config_path
        self.config = self._get_default_config()

    def _get_default_config(self):
        """Retorna a estrutura base (schema v2.0) caso o arquivo não exista"""
        return {
            "projeto": {
                "nome": "Novo Relatório",
                "mes": 1,
                "ano": 2026
            },
            "arquivos": {
                "linha_cabecalho": 0,
                "dados_origem": "",
                "user_template": ""
            },
            "contrato": {
                "data_inicio": "2026-01-01",
                "prazo_dias": 365
            },
            "extração": {
                "colunas": [],
                "separador_lista": ", ",
                "conector_final": " e ",
                "formato_final": ""
            },
            "posicoes": {
                "celula_data_inicio": "",
                "celula_prazo_dias": "",
                "celula_data_final": "",
                "celula_data_atual": "",
                "celula_tempo_decorrido": ""
            },
            "mapeamento": {}
        }

    def load_config(self):
        try:
            with open(self.config_path, "rb") as f:
                loaded = tomllib.load(f)
                # Opcional: fazer um merge da configuração padrão com a carregada
                self.config.update(loaded)
            logger.info(f"Configuração carregada com sucesso de: {self.config_path}")
            return self.config
        except FileNotFoundError:
            logger.warning(f"Arquivo {self.config_path} não encontrado. Usando configuração padrão (v2.0).")
            self.save_config() # Cria o arquivo padrão
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

    def import_config(self, file_path):
        """Importa configurações de um arquivo externo"""
        try:
            with open(file_path, "rb") as f:
                imported_config = tomllib.load(f)
            self.config = imported_config
            logger.info(f"Configuração importada de: {file_path}")
            return self.config
        except Exception as e:
            logger.error(f"Erro ao importar configuração de {file_path}: {e}")
            raise

    def export_config(self, file_path, config_to_export=None):
        """Exporta a configuração atual para um arquivo externo"""
        config = config_to_export if config_to_export else self.config
        try:
            with open(file_path, "wb") as f:
                tomli_w.dump(config, f)
            logger.info(f"Configuração exportada para: {file_path}")
        except Exception as e:
            logger.error(f"Erro ao exportar configuração para {file_path}: {e}")
            raise

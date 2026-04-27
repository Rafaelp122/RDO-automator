import tomllib
import tomli_w
from pathlib import Path
from src.app.core.logger import logger
from src.app.core.config_models import ReportConfig
from src.app.core.constants import DEFAULT_CONFIG_PATH

class ConfigManager:
    """Gerencia a leitura e escrita do arquivo config.toml usando Pydantic"""
    def __init__(self, config_path=None):
        self.config_path = Path(config_path) if config_path else DEFAULT_CONFIG_PATH
        self.config = ReportConfig()

    def load_config(self) -> ReportConfig:
        """Carrega a configuração e valida via Pydantic (resolve shallow merge)"""
        try:
            if not self.config_path.exists():
                logger.warning(f"Arquivo {self.config_path} não encontrado. Usando padrões.")
                self.save_config()
                return self.config

            with open(self.config_path, "rb") as f:
                data = tomllib.load(f)
                # O Pydantic faz o merge automático com os defaults se chaves estiverem faltando
                self.config = ReportConfig.model_validate(data)
            
            logger.info(f"Configuração carregada com sucesso de: {self.config_path}")
            return self.config
        except (FileNotFoundError, tomllib.TOMLDecodeError) as e:
            logger.error(f"Erro ao carregar configuração ({self.config_path}): {e}")
            # Em caso de erro crítico no arquivo, retorna o padrão para evitar crash
            return self.config
        except Exception as e:
            logger.error(f"Erro inesperado ao carregar configuração: {e}")
            return self.config

    def save_config(self, new_config: ReportConfig = None):
        """Persiste a configuração atual no arquivo TOML"""
        if new_config:
            self.config = new_config
            
        try:
            # by_alias=True garante que "extracao" seja salvo como "extração" no TOML
            data = self.config.model_dump(by_alias=True)
            with open(self.config_path, "wb") as f:
                tomli_w.dump(data, f)
            logger.info(f"Configuração salva com sucesso em: {self.config_path}")
        except PermissionError as e:
            logger.error(f"Sem permissão para salvar configuração: {e}")
            raise
        except Exception as e:
            logger.error(f"Erro inesperado ao salvar configuração: {e}")
            raise

    def import_config(self, file_path):
        """Importa configurações de um arquivo externo"""
        try:
            with open(file_path, "rb") as f:
                data = tomllib.load(f)
            self.config = ReportConfig.model_validate(data)
            logger.info(f"Configuração importada de: {file_path}")
            return self.config
        except (tomllib.TOMLDecodeError, ValueError) as e:
            logger.error(f"Arquivo de configuração inválido: {e}")
            raise
        except Exception as e:
            logger.error(f"Erro inesperado ao importar configuração: {e}")
            raise

    def export_config(self, file_path, config_to_export: ReportConfig = None):
        """Exporta a configuração atual para um arquivo externo, convertendo caminhos para relativo"""
        import os
        config = config_to_export if config_to_export else self.config
        try:
            # model_dump() simples para garantir que mapeamento e posições sejam incluídos
            data = config.model_dump(by_alias=True)
            
            # LOG DE DEPURAÇÃO (Verifique no terminal se os dados aparecem aqui)
            logger.debug(f"Exportando dados: Posições={data.get('posicoes')}, Mapeamento={data.get('mapeamento')}")
            
            # Converter caminhos para relativo se possível
            root = os.getcwd()
            if data.get("arquivos"):
                for key in ["dados_origem", "user_template", "template_ativo"]:
                    path_val = data["arquivos"].get(key)
                    if path_val and os.path.isabs(path_val):
                        try:
                            data["arquivos"][key] = os.path.relpath(path_val, root)
                        except (ValueError, TypeError):
                            pass 

            with open(file_path, "wb") as f:
                tomli_w.dump(data, f)
            logger.info(f"Configuração exportada com sucesso para: {file_path}")
        except Exception as e:
            logger.error(f"Erro ao exportar configuração para {file_path}: {e}")
            raise

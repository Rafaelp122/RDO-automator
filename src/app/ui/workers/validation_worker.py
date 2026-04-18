import os
import pandas as pd
import tomllib
import time
from PySide6.QtCore import QObject, Signal, Slot

class ValidationWorker(QObject):
    """
    Worker para validar a integridade dos dados e mapeamentos.
    """
    progress_log = Signal(str)
    validation_finished = Signal(bool, list)
    finished = Signal() # Sinal técnico para fechar a thread

    @Slot()
    def run(self):
        erros = []
        try:
            self.progress_log.emit("Iniciando validação de mapeamento...")
            time.sleep(0.5) # Pequena pausa para o usuário perceber o início
            
            # 1. Carregar Configurações
            if not os.path.exists("config.toml"):
                erros.append("Arquivo config.toml não encontrado.")
                self.validation_finished.emit(False, erros)
                return

            with open("config.toml", "rb") as f:
                config = tomllib.load(f)

            # 2. Verificar Arquivo de Origem
            caminho_dados = config['arquivos'].get('dados_origem')
            if not caminho_dados or not os.path.exists(caminho_dados):
                erros.append(f"Arquivo de origem não encontrado: {caminho_dados}")
            else:
                self.progress_log.emit(f"Analisando: {os.path.basename(caminho_dados)}")
                
                # 3. Validar Abas e Colunas
                try:
                    with pd.ExcelFile(caminho_dados) as xls:
                        abas_no_arquivo = xls.sheet_names
                        
                        col_data = config['colunas'].get('data')
                        col_servico = config['colunas'].get('servico')
                        
                        self.progress_log.emit(f"Verificando {len(config['mapeamento'])} abas mapeadas...")

                        for nome_aba in config['mapeamento'].keys():
                            if nome_aba not in abas_no_arquivo:
                                erros.append(f"Aba '{nome_aba}' não encontrada.")
                                continue
                            
                            df_header = pd.read_excel(xls, sheet_name=nome_aba, nrows=0)
                            colunas = df_header.columns.tolist()
                            
                            if col_data not in colunas:
                                erros.append(f"Na aba '{nome_aba}', coluna '{col_data}' inexistente.")
                            if col_servico not in colunas:
                                erros.append(f"Na aba '{nome_aba}', coluna '{col_servico}' inexistente.")
                
                except Exception as e:
                    erros.append(f"Falha ao abrir Excel: {str(e)}")

            # 4. Resultado Final
            if erros:
                self.validation_finished.emit(False, erros)
            else:
                self.progress_log.emit("Tudo ok! Mapeamento validado.")
                self.validation_finished.emit(True, [])

        except Exception as e:
            self.progress_log.emit(f"Erro fatal: {str(e)}")
            self.validation_finished.emit(False, [str(e)])
        
        finally:
            self.finished.emit()

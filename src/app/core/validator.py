import os
import re
import pandas as pd
from src.app.core.logger import logger

class ReportValidator:
    """
    Serviço core para validar a integridade dos dados e mapeamentos do relatório.
    Desacoplado de qualquer interface gráfica.
    """

    @staticmethod
    def is_valid_excel_coordinate(coord):
        """Valida se uma string é uma coordenada Excel válida (ex: A1, B10, Z100)"""
        return bool(re.match(r'^[A-Z]{1,3}[1-9][0-9]*$', str(coord).upper()))

    def validate(self, config):
        """
        Executa a validação completa baseada no dicionário de configuração.
        Retorna (sucesso: bool, erros: list[str])
        """
        erros = []
        
        # 1. Validar Coordenada da Data
        cel_data = config.get('posicoes', {}).get('celula_data')
        if not self.is_valid_excel_coordinate(cel_data):
            err_msg = f"Célula da data '{cel_data}' é inválida."
            erros.append(err_msg)
            logger.warning(err_msg)

        # 2. Verificar Arquivo de Origem
        caminho_dados = config.get('arquivos', {}).get('dados_origem')
        if not caminho_dados or not os.path.exists(caminho_dados):
            err_msg = f"Arquivo de origem não encontrado: {caminho_dados}"
            erros.append(err_msg)
            logger.error(err_msg)
            return False, erros

        # 3. Validar Abas e Colunas
        try:
            with pd.ExcelFile(caminho_dados) as xls:
                abas_no_arquivo = xls.sheet_names
                
                col_data = config.get('colunas', {}).get('data')
                col_servico = config.get('colunas', {}).get('servico')
                linha_header = config.get('arquivos', {}).get('linha_cabecalho', 0)
                
                for nome_aba, celula in config.get('mapeamento', {}).items():
                    # Validar Coordenada de Destino
                    if not self.is_valid_excel_coordinate(celula):
                        err_msg = f"Célula de destino '{celula}' para aba '{nome_aba}' é inválida."
                        erros.append(err_msg)
                        logger.warning(err_msg)

                    if nome_aba not in abas_no_arquivo:
                        err_msg = f"Aba '{nome_aba}' não encontrada."
                        erros.append(err_msg)
                        logger.warning(err_msg)
                        continue
                    
                    df_header = pd.read_excel(xls, sheet_name=nome_aba, header=linha_header, nrows=0)
                    colunas = df_header.columns.tolist()
                    
                    if col_data not in colunas:
                        err_msg = f"Na aba '{nome_aba}', coluna '{col_data}' inexistente."
                        erros.append(err_msg)
                        logger.warning(err_msg)
                    if col_servico not in colunas:
                        err_msg = f"Na aba '{nome_aba}', coluna '{col_servico}' inexistente."
                        erros.append(err_msg)
                        logger.warning(err_msg)
        
        except Exception as e:
            err_msg = f"Falha ao abrir Excel: {str(e)}"
            erros.append(err_msg)
            logger.error(err_msg)

        return (len(erros) == 0), erros

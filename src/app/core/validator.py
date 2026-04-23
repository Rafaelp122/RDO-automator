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

    def validate(self, config, output_path=None):
        """
        Executa a validação completa baseada no dicionário de configuração (v2.0).
        Retorna (sucesso: bool, erros: list[str])
        """
        erros = []
        
        # 1. Validar Coordenadas de Posições
        posicoes = config.get('posicoes', {})
        for nome_pos, celula in posicoes.items():
            if celula and not self.is_valid_excel_coordinate(celula):
                err_msg = f"Célula '{celula}' configurada para '{nome_pos}' é inválida."
                erros.append(err_msg)
                logger.warning(err_msg)

        # 2. Verificar Permissão de Escrita no Arquivo de Saída (Bloqueio)
        if output_path and os.path.exists(output_path):
            try:
                # Tenta abrir o arquivo para append (modo a+b)
                with open(output_path, 'a+b'):
                    pass
            except PermissionError:
                err_msg = f"Ação bloqueada: Feche o arquivo {os.path.basename(output_path)} antes de continuar."
                erros.append(err_msg)
                logger.error(err_msg)

        # 3. Validar Extração e Formato Final
        extracao = config.get('extração', {})
        colunas_esperadas = extracao.get('colunas', [])
        formato_final = extracao.get('formato_final', '')
        
        # Encontra todas as tags no formato {NomeColuna} ou {NomeColuna:algo}
        tags_no_formato = re.findall(r'\{([^}:]+)(?::[^}]+)?\}', formato_final)
        for tag in tags_no_formato:
            if tag not in colunas_esperadas:
                err_msg = f"A tag '{{{tag}}}' usada no formato final não está na lista de colunas selecionadas."
                erros.append(err_msg)
                logger.warning(err_msg)

        # 4. Verificar Arquivo de Origem e Abas
        caminho_dados = config.get('arquivos', {}).get('dados_origem')
        if not caminho_dados or not os.path.exists(caminho_dados):
            err_msg = f"Arquivo de origem não encontrado: {caminho_dados}"
            erros.append(err_msg)
            logger.error(err_msg)
            return False, erros

        try:
            with pd.ExcelFile(caminho_dados) as xls:
                abas_no_arquivo = xls.sheet_names
                linha_header = config.get('arquivos', {}).get('linha_cabecalho', 0)
                
                for nome_aba, celula in config.get('mapeamento', {}).items():
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
                    colunas_aba = df_header.columns.tolist()
                    
                    for col in colunas_esperadas:
                        if col not in colunas_aba:
                            err_msg = f"Na aba '{nome_aba}', coluna '{col}' inexistente."
                            erros.append(err_msg)
                            logger.warning(err_msg)
                            
        except Exception as e:
            err_msg = f"Falha ao abrir Excel: {str(e)}"
            erros.append(err_msg)
            logger.error(err_msg)

        return (len(erros) == 0), erros

import os
import pandas as pd
from openpyxl import load_workbook
import calendar
from datetime import datetime
from src.app.core.processor import TextProcessor
from src.app.core.logger import logger

class ExcelHandler:
    """Responsável por ler a origem e escrever no template Excel"""
    
    def __init__(self, config):
        self.config = config

    def gerar_diario_completo(self, progress_callback=None):
        """
        Executa o processo ETL:
        1. Lê dados brutos do Excel de origem.
        2. Carrega o template base (prioriza usuário).
        3. Para cada dia do mês, clona o template e preenche os dados.
        """
        caminho_dados = self.config['arquivos']['dados_origem']
        caminho_template = self.config['arquivos']['template_ativo']
        
        logger.info(f"Lendo dados de: {caminho_dados}")
        # Lê todas as abas de origem de uma vez para performance
        abas_origem = pd.read_excel(caminho_dados, sheet_name=None)
        
        # Carrega o template (preservando estilos e fórmulas)
        if not os.path.exists(caminho_template) or os.path.getsize(caminho_template) == 0:
            logger.error(f"Arquivo de template inválido: {caminho_template}")
            raise FileNotFoundError(f"O arquivo de template está vazio ou não existe: {caminho_template}")
        
        logger.info(f"Carregando template base: {caminho_template}")
        try:
            wb = load_workbook(caminho_template)
        except Exception as e:
            logger.exception("Falha ao abrir template Excel com openpyxl")
            raise ValueError(f"O arquivo de template não é um Excel (.xlsx) válido: {str(e)}")
        
        ws_template = wb.active
        
        ano = self.config['projeto']['ano']
        mes = self.config['projeto']['mes']
        _, ultimo_dia = calendar.monthrange(ano, mes)

        logger.info(f"Iniciando loop diário para o mês {mes}/{ano} ({ultimo_dia} abas)")
        for dia in range(1, ultimo_dia + 1):
            if progress_callback:
                progresso = int((dia / ultimo_dia) * 100)
                progress_callback(progresso)

            data_atual = pd.Timestamp(year=ano, month=mes, day=dia)
            data_str = data_atual.strftime('%d-%m')
            
            # 1. Cria nova aba clonando o layout do template
            nova_ws = wb.copy_worksheet(ws_template)
            nova_ws.title = data_str
            
            # 2. Escreve a data na célula configurada
            celula_data = self.config['posicoes'].get('celula_data', 'A1')
            nova_ws[celula_data] = data_atual.strftime('%d/%m/%Y')

            # 3. Processa cada mapeamento configurado
            for nome_aba_origem, celula_destino in self.config['mapeamento'].items():
                if nome_aba_origem in abas_origem:
                    df = abas_origem[nome_aba_origem]
                    
                    # Normalização da coluna de data
                    col_data = self.config['colunas'].get('data', 'Data')
                    df[col_data] = pd.to_datetime(df[col_data], errors='coerce')
                    
                    # Tratamento de células mescladas (ffill) se configurado
                    col_bairro = self.config['colunas'].get('bairro')
                    if col_bairro:
                        df[col_bairro] = df[col_bairro].ffill()

                    # Filtra os serviços do dia
                    filtro = df[df[col_data].dt.day == dia]
                    
                    if not filtro.empty:
                        col_servico = self.config['colunas'].get('servico', 'Descrição do serviço')
                        servicos = filtro[col_servico].unique()
                        
                        # Usa o processador core para formatar o resumo
                        resumo = TextProcessor.formatar_resumo(servicos)
                        nova_ws[celula_destino] = resumo
        
        # Remove a aba original de exemplo e salva o arquivo final
        wb.remove(ws_template)
        nome_saida = f"Diario_Consolidado_{mes:02d}_{ano}.xlsx"
        caminho_saida = os.path.join("data", "output", nome_saida)
        
        # Garante que o diretório de saída existe
        os.makedirs(os.path.dirname(caminho_saida), exist_ok=True)

        logger.info(f"Tentando salvar arquivo consolidado em: {caminho_saida}")
        
        # Verifica se o arquivo está aberto/bloqueado
        if os.path.exists(caminho_saida):
            try:
                # Tenta renomear o arquivo para ele mesmo. Se falhar, está aberto.
                os.rename(caminho_saida, caminho_saida)
            except OSError:
                logger.error(f"O arquivo {caminho_saida} parece estar aberto no Excel.")
                raise PermissionError(
                    f"O arquivo '{nome_saida}' está aberto. Por favor, feche-o no Excel e tente novamente."
                )

        try:
            wb.save(caminho_saida)
            logger.info("Relatório final gerado com sucesso.")
        except Exception as e:
            logger.exception(f"Erro ao salvar arquivo final: {e}")
            raise
            
        return caminho_saida

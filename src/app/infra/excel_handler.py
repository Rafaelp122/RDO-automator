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
        linha_header = self.config['arquivos'].get('linha_cabecalho', 0)
        
        logger.info(f"Lendo dados de: {caminho_dados} (header na linha {linha_header})")
        # Lê todas as abas de origem de uma vez para performance
        abas_origem = pd.read_excel(caminho_dados, sheet_name=None, header=linha_header)
        
        # Pré-processamento: Normalização de dados
        for nome_aba, df in abas_origem.items():
            col_data_nome = 'Data'
            for col in df.columns:
                if 'data' in str(col).lower():
                    col_data_nome = col
                    break
            if col_data_nome in df.columns:
                df[col_data_nome] = pd.to_datetime(df[col_data_nome], errors='coerce')
        
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
        
        ano = self.config.get('projeto', {}).get('ano', datetime.now().year)
        mes = self.config.get('projeto', {}).get('mes', datetime.now().month)
        _, ultimo_dia = calendar.monthrange(ano, mes)

        # Cálculos de Datas do Contrato
        data_inicio_str = self.config.get('contrato', {}).get('data_inicio')
        if data_inicio_str:
            data_inicio = datetime.strptime(data_inicio_str, '%Y-%m-%d')
        else:
            data_inicio = datetime(ano, mes, 1)
        
        prazo_dias = self.config.get('contrato', {}).get('prazo_dias', 0)
        from datetime import timedelta
        data_final = data_inicio + timedelta(days=prazo_dias)

        logger.info(f"Iniciando loop diário para o mês {mes}/{ano} ({ultimo_dia} abas)")
        for dia in range(1, ultimo_dia + 1):
            if progress_callback:
                progresso = int((dia / ultimo_dia) * 100)
                progress_callback(progresso)

            data_atual = datetime(ano, mes, dia)
            data_str = data_atual.strftime('%d-%m')
            
            # 1. Cria nova aba clonando o layout do template
            nova_ws = wb.copy_worksheet(ws_template)
            nova_ws.title = data_str
            
            # 2. Metadados do Contrato e Posições Fixas
            posicoes = self.config.get('posicoes', {})
            
            if posicoes.get('celula_data_inicio'):
                nova_ws[posicoes['celula_data_inicio']] = data_inicio.strftime('%d/%m/%Y')
            if posicoes.get('celula_prazo_dias'):
                nova_ws[posicoes['celula_prazo_dias']] = f"{prazo_dias} dias"
            if posicoes.get('celula_data_final'):
                nova_ws[posicoes['celula_data_final']] = data_final.strftime('%d/%m/%Y')
            if posicoes.get('celula_data_atual'):
                nova_ws[posicoes['celula_data_atual']] = data_atual.strftime('%d/%m/%Y')
            if posicoes.get('celula_tempo_decorrido'):
                delta = data_atual - data_inicio
                tempo_decorrido = delta.days + 1
                nova_ws[posicoes['celula_tempo_decorrido']] = f"{tempo_decorrido} dias"

            # 3. Processa cada mapeamento configurado
            mapeamentos = self.config.get('mapeamento', {})
            extracao = self.config.get('extração', {})
            colunas_esperadas = extracao.get('colunas', [])
            formato_final = extracao.get('formato_final', '')
            sep = extracao.get('separador_lista', ', ')
            con = extracao.get('conector_final', ' e ')

            for nome_aba_origem, celula_destino in mapeamentos.items():
                if nome_aba_origem in abas_origem:
                    df = abas_origem[nome_aba_origem]
                    
                    col_data_nome = 'Data'
                    for col in df.columns:
                        if 'data' in str(col).lower():
                            col_data_nome = col
                            break
                            
                    if col_data_nome in df.columns:
                        filtro = df[df[col_data_nome].dt.day == dia]
                    else:
                        filtro = pd.DataFrame()
                    
                    if not filtro.empty:
                        dados_extraidos = {}
                        for col in colunas_esperadas:
                            if col in filtro.columns:
                                val_unicos = filtro[col].dropna().unique().tolist()
                                dados_extraidos[col] = val_unicos
                        
                        resumo = TextProcessor.formatar_resumo(dados_extraidos, formato_final, sep, con)
                        nova_ws[celula_destino] = resumo
                    else:
                        # RN01: Se não há dados, garante que a célula mapeada esteja vazia
                        nova_ws[celula_destino] = None
        
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

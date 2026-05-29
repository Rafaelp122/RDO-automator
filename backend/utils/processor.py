import re

class TextProcessor:
    """Lógica de negócio para processamento de texto (Title Case, Siglas, etc.)"""
    
    # Conectores que devem ficar em minúsculo no meio da frase
    PREPOSICOES = ['de', 'da', 'do', 'das', 'dos', 'e', 'em', 'com', 'no', 'na', 'á', 'à', 'a', 'ou', 'para']
    # Siglas que devem permanecer em CAIXA ALTA
    SIGLAS = ['LED', 'RJ', 'BR', 'IP', 'PCD', 'BHLS', 'SOS', 'CNPJ']

    @classmethod
    def corrigir_capitalizacao(cls, texto):
        """
        Padroniza o texto com regras de engenharia:
        1. Siglas técnicas em CAIXA ALTA.
        2. Preposições em minúsculo.
        3. Tratamento de apóstrofos (ex: D'Areia).
        """
        if not isinstance(texto, str) or not texto.strip():
            return ""
        
        palavras = texto.lower().split()
        resultado = []

        for i, p in enumerate(palavras):
            # Limpeza para verificação (remove pontuações comuns)
            p_limpa = re.sub(r'[^\w\']', '', p)
            
            # 1. Caso especial: Nomes com apóstrofo (ex: d'areia -> D'Areia)
            if "d'" in p:
                partes = p.split("'")
                p_corrigida = f"{partes[0].upper()}'{partes[1].capitalize()}"
                resultado.append(p_corrigida)
                continue

            # 2. Verifica se é uma SIGLA
            if p_limpa.upper() in cls.SIGLAS:
                resultado.append(p.upper())
                continue

            # 3. Se for preposição no meio da frase, fica minúscula
            if i > 0 and p_limpa in cls.PREPOSICOES:
                resultado.append(p.lower())
                continue

            # 4. Capitalização Geral (Preserva o primeiro caractere alfabético)
            p_final = ""
            encontrou_letra = False
            for char in p:
                if char.isalpha() and not encontrou_letra:
                    p_final += char.upper()
                    encontrou_letra = True
                else:
                    p_final += char
            resultado.append(p_final)
        
        return " ".join(resultado)

    @classmethod
    def formatar_resumo(cls, dados_extraidos, formato_final, separador_lista=", ", conector_final=" e "):
        """
        Gera a frase final baseada no template, aplicando regras de pluralização.
        """
        if not formato_final or not dados_extraidos:
            return ""

        # Verificação preventiva: Se não houver nenhum serviço real, não gera nada
        # Consideramos 'Serviço' ou 'Descrição do serviço' como âncoras
        tem_servico_valido = False
        
        processados = {}
        for coluna, lista_valores in dados_extraidos.items():
            # Filtro robusto: Ignora valores que são apenas números pequenos (ruído de planilha)
            # ou strings vazias/NAs
            valores_limpos = []
            for v in lista_valores:
                v_str = str(v).strip()
                # Ignora se for vazio, "nan", "0" ou apenas números decimais soltos
                if not v_str or v_str.lower() == 'nan' or v_str == '0':
                    continue
                # Ignora ruídos numéricos típicos de erro de leitura (ex: 0.3, 1.2)
                if re.match(r'^-?\d+(\.\d+)?$', v_str) and float(v_str) < 2:
                    continue
                
                valores_limpos.append(cls.corrigir_capitalizacao(v_str))
            
            # Remove duplicatas mantendo ordem
            valores_limpos = sorted(list(set(valores_limpos)))
            
            if valores_limpos:
                if "serviço" in coluna.lower():
                    tem_servico_valido = True
                
                is_plural = len(valores_limpos) > 1
                string_valores = separador_lista.join(valores_limpos[:-1])
                if string_valores:
                    string_valores += f"{conector_final}{valores_limpos[-1]}"
                else:
                    string_valores = valores_limpos[0]
                
                processados[coluna] = {
                    "texto": string_valores,
                    "plural": is_plural
                }
            else:
                processados[coluna] = {
                    "texto": "",
                    "plural": False
                }

        # Se não encontramos nenhum serviço válido, retornamos vazio para não sujar a planilha
        if not tem_servico_valido:
            return ""

        texto_resultado = formato_final
        for coluna, info in processados.items():
            texto_resultado = texto_resultado.replace(f"{{{coluna}}}", info["texto"])
            texto_resultado = texto_resultado.replace(f"{{{coluna}:s}}", "s" if info["plural"] else "")
            texto_resultado = texto_resultado.replace(f"{{{coluna}:es}}", "es" if info["plural"] else "")
            
            # Lógica inteligente para 'no' vs 'nos' / 'na' vs 'nas'
            # Se for plural, vira 'nos/nas'. O gênero é difícil detectar sem NLP pesado, 
            # então mantemos a lógica de pluralização simples solicitada.
            plural_connector = "s" if info["plural"] else ""
            texto_resultado = texto_resultado.replace(f"{{{coluna}:nos}}", plural_connector)
            
        return texto_resultado

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
        dados_extraidos: dict onde as chaves são as colunas (ex: 'Serviço') e os valores são listas de strings.
        """
        if not formato_final or not dados_extraidos:
            return ""

        texto_resultado = formato_final
        
        for coluna, lista_valores in dados_extraidos.items():
            # Limpa e remove duplicatas
            valores_limpos = sorted(list(set(cls.corrigir_capitalizacao(str(v)) for v in lista_valores if v)))
            
            # Monta a string da lista
            if not valores_limpos:
                string_valores = ""
                is_plural = False
            else:
                string_valores = separador_lista.join(valores_limpos[:-1])
                if string_valores:
                    string_valores += f"{conector_final}{valores_limpos[-1]}"
                else:
                    string_valores = valores_limpos[0]
                is_plural = len(valores_limpos) > 1

            # Substituição dos valores brutos
            texto_resultado = texto_resultado.replace(f"{{{coluna}}}", string_valores)
            
            # Tratamento de plurais (ex: {Chave:s}, {Chave:es}, {Chave:nos})
            texto_resultado = texto_resultado.replace(f"{{{coluna}:s}}", "s" if is_plural else "")
            texto_resultado = texto_resultado.replace(f"{{{coluna}:es}}", "es" if is_plural else "")
            texto_resultado = texto_resultado.replace(f"{{{coluna}:nos}}", "s" if is_plural else "")
            
        return texto_resultado

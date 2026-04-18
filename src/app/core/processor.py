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
    def formatar_resumo(cls, lista_servicos, lista_bairros=None):
        """Consolida serviços e bairros em uma frase natural."""
        servicos_limpos = sorted(list(set(cls.corrigir_capitalizacao(s) for s in lista_servicos if s)))
        
        if not servicos_limpos:
            return ""

        resumo = ", ".join(servicos_limpos[:-1])
        if resumo:
            resumo += f" e {servicos_limpos[-1]}"
        else:
            resumo = servicos_limpos[0]
            
        return resumo

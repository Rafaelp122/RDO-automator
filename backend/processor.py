import re

class TextProcessor:
    PREPOSICOES = ['de', 'da', 'do', 'das', 'dos', 'e', 'em', 'com', 'no', 'na', 'á', 'à', 'a', 'ou', 'para']
    SIGLAS = ['LED', 'RJ', 'BR', 'IP', 'PCD', 'BHLS', 'SOS', 'CNPJ']

    @classmethod
    def corrigir_capitalizacao(cls, texto):
        if not isinstance(texto, str) or not texto.strip():
            return ""
        palavras = texto.lower().split()
        resultado = []
        for i, p in enumerate(palavras):
            p_limpa = re.sub(r'[^\w\']', '', p)
            if "d'" in p:
                partes = p.split("'")
                p_corrigida = f"{partes[0].upper()}'{partes[1].capitalize()}"
                resultado.append(p_corrigida)
                continue
            if p_limpa.upper() in cls.SIGLAS:
                resultado.append(p.upper())
                continue
            if i > 0 and p_limpa in cls.PREPOSICOES:
                resultado.append(p.lower())
                continue
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
        if not formato_final or not dados_extraidos:
            return ""
        tem_servico_valido = False
        processados = {}
        for coluna, lista_valores in dados_extraidos.items():
            valores_limpos = []
            for v in lista_valores:
                v_str = str(v).strip()
                if not v_str or v_str.lower() == 'nan' or v_str == '0':
                    continue
                if re.match(r'^-?\d+(\.\d+)?$', v_str) and float(v_str) < 2:
                    continue
                valores_limpos.append(cls.corrigir_capitalizacao(v_str))
            valores_limpos = list(dict.fromkeys(valores_limpos))
            if valores_limpos:
                if "serviço" in coluna.lower():
                    tem_servico_valido = True
                is_plural = len(valores_limpos) > 1
                string_valores = separador_lista.join(valores_limpos[:-1])
                if string_valores:
                    string_valores += f"{conector_final}{valores_limpos[-1]}"
                else:
                    string_valores = valores_limpos[0]
                processados[coluna] = {"texto": string_valores, "plural": is_plural}
            else:
                processados[coluna] = {"texto": "", "plural": False}
        if not tem_servico_valido:
            return ""
        texto_resultado = formato_final
        for coluna, info in processados.items():
            texto_resultado = texto_resultado.replace(f"{{{coluna}}}", info["texto"])
            texto_resultado = texto_resultado.replace(f"{{{coluna}:s}}", "s" if info["plural"] else "")
            texto_resultado = texto_resultado.replace(f"{{{coluna}:es}}", "es" if info["plural"] else "")
            plural_connector = "s" if info["plural"] else ""
            texto_resultado = texto_resultado.replace(f"{{{coluna}:nos}}", plural_connector)
        return texto_resultado

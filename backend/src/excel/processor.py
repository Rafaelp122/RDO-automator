import re


class TextProcessor:
    PREPOSITIONS = [
        "de",
        "da",
        "do",
        "das",
        "dos",
        "e",
        "em",
        "com",
        "no",
        "na",
        "á",
        "à",
        "a",
        "ou",
        "para",
    ]

    @classmethod
    def fix_capitalization(cls, text, acronyms=None):
        """Aplica Title Case preservando siglas e preposições.

        Args:
            text: String a ser formatada.
            acronyms: Lista de siglas a preservar em maiúsculo.
                      Se ``None`` ou vazia, nenhuma sigla é preservada.
        """
        if not isinstance(text, str) or not text.strip():
            return ""

        acronyms_upper = {a.upper() for a in (acronyms or [])}
        words = text.lower().split()
        result = []
        for i, word in enumerate(words):
            # Remove pontuação (exceto apóstrofo) para poder comparar com
            # siglas e preposições; a palavra original com pontuação é usada
            # na exibição final.
            clean_word = re.sub(r"[^\w']", "", word)

            if "d'" in word:
                parts = word.split("'")
                fixed_word = f"{parts[0].upper()}'{parts[1].capitalize()}"
                result.append(fixed_word)
                continue

            if clean_word.upper() in acronyms_upper:
                result.append(word.upper())
                continue

            if i > 0 and clean_word in cls.PREPOSITIONS:
                result.append(word.lower())
                continue

            # Title Case manual: capitaliza apenas a primeira letra,
            # preservando caracteres não-alfabéticos na posição original
            # (ex: "(led" → "(Led"). str.capitalize() não serviria pois
            # lowerca o resto e remove o contexto posicional.
            final_word = ""
            capitalized = False
            for char in word:
                if char.isalpha() and not capitalized:
                    final_word += char.upper()
                    capitalized = True
                else:
                    final_word += char
            result.append(final_word)

        return " ".join(result)

    @classmethod
    def format_summary(
        cls,
        values_by_column,
        format_template,
        list_separator=", ",
        final_connector=" e ",
        acronyms=None,
    ):
        """Formata valores extraídos aplicando pluralização e Title Case.

        Args:
            values_by_column: Dicionário ``{coluna: [valores]}``.
            format_template: Template de string com placeholders ``{Coluna}``.
            list_separator: Separador entre itens de uma lista.
            final_connector: Conector para o último item (ex: " e ").
            acronyms: Lista de siglas repassada para ``fix_capitalization``.
        """
        if not format_template or not values_by_column:
            return ""

        has_valid_service = False
        processed = {}
        for column, values_list in values_by_column.items():
            clean_values = []
            for value in values_list:
                value_str = str(value).strip()
                if not value_str or value_str.lower() == "nan" or value_str == "0":
                    continue
                if re.match(r"^-?\d+(\.\d+)?$", value_str) and float(value_str) < 2:
                    continue
                clean_values.append(cls.fix_capitalization(value_str, acronyms=acronyms))

            clean_values = list(dict.fromkeys(clean_values))
            if clean_values:
                if "serviço" in column.lower():
                    has_valid_service = True
                is_plural = len(clean_values) > 1
                prefix = list_separator.join(clean_values[:-1])
                if prefix:
                    column_text = f"{prefix}{final_connector}{clean_values[-1]}"
                else:
                    column_text = clean_values[0]
                processed[column] = {"text": column_text, "plural": is_plural}
            else:
                processed[column] = {"text": "", "plural": False}

        if not has_valid_service:
            return ""

        result = format_template
        for column, data in processed.items():
            result = result.replace(f"{{{column}}}", data["text"])
            result = result.replace(f"{{{column}:s}}", "s" if data["plural"] else "")
            result = result.replace(f"{{{column}:es}}", "es" if data["plural"] else "")
            result = result.replace(f"{{{column}:nos}}", "s" if data["plural"] else "")
        return result

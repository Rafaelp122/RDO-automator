import pytest
from src.excel.processor import TextProcessor


class TestTextProcessor:

    @pytest.mark.parametrize("input_text, acronyms, expected", [
        ("INSTALAÇÃO DE LUMINÁRIA LED", ["LED"], "Instalação de Luminária LED"),
        ("MANUTENÇÃO NO RIO DE JANEIRO RJ", ["RJ"], "Manutenção no Rio de Janeiro RJ"),
        ("D'AREIA E PCD", ["PCD"], "D'Areia e PCD"),
        ("sistema bhls e ip", ["BHLS", "IP"], "Sistema BHLS e IP"),
        ("limpeza de caixa de ralo", [], "Limpeza de Caixa de Ralo"),
        ("INSTALAÇÃO DE LUMINÁRIA LED", [], "Instalação de Luminária Led"),
        ("", [], ""),
        (None, None, ""),
    ])
    def test_fix_capitalization(self, input_text, acronyms, expected):
        assert TextProcessor.fix_capitalization(input_text, acronyms=acronyms) == expected

    def test_without_acronyms(self):
        assert TextProcessor.fix_capitalization(
            "INSTALAÇÃO DE LUMINÁRIA LED"
        ) == "Instalação de Luminária Led"

    def test_format_summary_simple(self):
        data = {"Serviço": ["Pintura", "LIMPEZA"]}
        template = "Realizamos o{Serviço:s} serviço{Serviço:s}: {Serviço}."
        result = TextProcessor.format_summary(data, template)
        assert result == "Realizamos os serviços: Pintura e Limpeza."

    def test_format_summary_singular(self):
        data = {"Serviço": ["Pintura"]}
        template = "Realizamos o{Serviço:s} serviço{Serviço:s}: {Serviço}."
        result = TextProcessor.format_summary(data, template)
        assert result == "Realizamos o serviço: Pintura."

    def test_format_summary_nos_plural(self):
        data = {"Serviço": ["Pintura"], "Bairro": ["Centro", "Tijuca"]}
        template = "Serviço{Serviço:s} {Serviço} realizado{Serviço:s} no{Bairro:nos} bairro{Bairro:s} {Bairro}."
        result = TextProcessor.format_summary(data, template)
        assert result == "Serviço Pintura realizado nos bairros Centro e Tijuca."

    def test_format_summary_empty(self):
        assert TextProcessor.format_summary({}, "") == ""

    def test_format_summary_with_acronyms(self):
        data = {"Serviço": ["pintura LED externa", "limpeza PCD"]}
        template = "Serviços: {Serviço}."
        result = TextProcessor.format_summary(data, template, acronyms=["LED", "PCD"])
        assert result == "Serviços: Pintura LED Externa e Limpeza PCD."

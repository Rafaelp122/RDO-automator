import pytest
from src.app.core.processor import TextProcessor

class TestTextProcessor:
    
    @pytest.mark.parametrize("input_text, expected", [
        ("INSTALAÇÃO DE LUMINÁRIA LED", "Instalação de Luminária LED"),
        ("limpeza de caixa de ralo", "Limpeza de Caixa de Ralo"),
        ("MANUTENÇÃO NO RIO DE JANEIRO RJ", "Manutenção no Rio de Janeiro RJ"),
        ("D'AREIA E PCD", "D'Areia e PCD"),
        ("sistema bhls e ip", "Sistema BHLS e IP"),
        ("", ""),
        (None, ""),
    ])
    def test_corrigir_capitalizacao(self, input_text, expected):
        assert TextProcessor.corrigir_capitalizacao(input_text) == expected

    def test_formatar_resumo_simples(self):
        dados = {"Serviço": ["Pintura", "LIMPEZA"]}
        formato = "Realizamos o{Serviço:s} serviço{Serviço:s}: {Serviço}."
        resultado = TextProcessor.formatar_resumo(dados, formato)
        # sorted: Limpeza, Pintura
        assert resultado == "Realizamos os serviços: Limpeza e Pintura."

    def test_formatar_resumo_singular(self):
        dados = {"Serviço": ["Pintura"]}
        formato = "Realizamos o{Serviço:s} serviço{Serviço:s}: {Serviço}."
        resultado = TextProcessor.formatar_resumo(dados, formato)
        assert resultado == "Realizamos o serviço: Pintura."

    def test_formatar_resumo_nos_plural(self):
        dados = {"Serviço": ["Pintura"], "Bairro": ["Centro", "Tijuca"]}
        formato = "Serviço{Serviço:s} {Serviço} realizado{Serviço:s} no{Bairro:nos} bairro{Bairro:s} {Bairro}."
        resultado = TextProcessor.formatar_resumo(dados, formato)
        assert resultado == "Serviço Pintura realizado nos bairros Centro e Tijuca."

    def test_formatar_resumo_vazio(self):
        assert TextProcessor.formatar_resumo({}, "") == ""

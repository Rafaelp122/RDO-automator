import pytest
import pandas as pd
from pathlib import Path
from unittest.mock import patch
from src.app.core.report_builder import ReportBuilder
from src.app.core.validator import ReportValidator
from src.app.infra.excel_loader import ExcelLoader
from src.app.core.config_models import ReportConfig

class TestSadPaths:

    def test_excel_loader_corrupted_file(self, tmp_path):
        # Criar um arquivo que NÃO é excel mas tem extensão .xlsx
        corrupted_path = tmp_path / "fake.xlsx"
        corrupted_path.write_text("ISTO NÃO É UM EXCEL")
        
        loader = ExcelLoader(str(corrupted_path))
        
        with pytest.raises(Exception): # Pandas deve falhar ao ler
            loader.load_all_sheets()

    def test_validator_detects_empty_mapping(self, valid_config):
        validator = ReportValidator()
        valid_config.mapeamento = {} # Mapeamento vazio é válido sintaticamente mas o builder não fará nada
        
        sucesso, erros, field_errors = validator.validate(valid_config)
        assert sucesso is True # Atualmente o validator permite mapeamento vazio
        assert len(field_errors) == 0

    def test_permission_error_on_save(self, valid_config, tmp_path):
        output_path = tmp_path / "locked.xlsx"
        output_path.touch()
        
        builder = ReportBuilder(valid_config)
        
        # Simular que o arquivo está bloqueado (PermissionError) via mock
        # Já que simular um lock real de arquivo é difícil em cross-platform
        with patch('pathlib.Path.rename') as mock_rename:
            mock_rename.side_effect = OSError("Access denied")
            with pytest.raises(PermissionError, match="Por favor, feche-o"):
                builder.build(output_path)

    def test_invalid_date_format_in_source(self, temp_excel_dir, sample_template_excel):
        input_dir, output_dir = temp_excel_dir
        path = input_dir / "invalid_dates.xlsx"
        
        # Dataframe com coluna 'Data' contendo lixo
        df = pd.DataFrame({
            'Data': ['DATA ERRADA', '2026-05-01'],
            'Servico': ['S1', 'S2']
        })
        df.to_excel(path, index=False)
        
        config = ReportConfig()
        config.arquivos.dados_origem = str(path)
        config.arquivos.template_ativo = str(sample_template_excel)
        config.projeto.mes = 5
        config.projeto.ano = 2026
        config.mapeamento = {"Sheet1": "A1"}
        config.extracao.colunas = ["Servico"]
        
        builder = ReportBuilder(config)
        output_file = output_dir / "result.xlsx"
        
        # O builder deve rodar sem crashar, ignorando a data inválida
        builder.build(output_file)
        assert output_file.exists()

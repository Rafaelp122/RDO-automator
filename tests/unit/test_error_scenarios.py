import pytest
import os
import tomli_w
import pandas as pd
from unittest.mock import MagicMock, patch
from src.app.ui.workers.validation_worker import ValidationWorker
from src.app.infra.excel_handler import ExcelHandler

class TestValidationScenarios:
    
    def test_validation_missing_origin_file(self, qtbot, tmp_path):
        os.chdir(tmp_path)
        config = {
            'arquivos': {'dados_origem': 'non_existent.xlsx'},
            'posicoes': {'celula_data_atual': 'E3'},
            'mapeamento': {'aba1': 'B10'},
            'extração': {'colunas': ['Data', 'Servico']}
        }
        with open("config.toml", "wb") as f:
            f.write(tomli_w.dumps(config).encode())
            
        worker = ValidationWorker()
        with qtbot.waitSignal(worker.validation_finished, timeout=2000) as blocker:
            worker.run()
        
        sucesso, erros = blocker.args
        assert sucesso is False
        assert any("Arquivo de origem não encontrado" in e for e in erros)

    def test_validation_missing_sheet(self, qtbot, tmp_path):
        os.chdir(tmp_path)
        # Create excel with only 'Sheet1'
        data_path = tmp_path / "data.xlsx"
        pd.DataFrame({'Data': [1], 'Servico': [1]}).to_excel(data_path, sheet_name='Sheet1', index=False)
        
        config = {
            'arquivos': {'dados_origem': str(data_path)},
            'posicoes': {'celula_data_atual': 'E3'},
            'mapeamento': {'AbaInexistente': 'B10'},
            'extração': {'colunas': ['Data', 'Servico']}
        }
        with open("config.toml", "wb") as f:
            f.write(tomli_w.dumps(config).encode())
            
        worker = ValidationWorker()
        with qtbot.waitSignal(worker.validation_finished, timeout=2000) as blocker:
            worker.run()
        
        sucesso, erros = blocker.args
        assert sucesso is False
        assert any("Aba 'AbaInexistente' não encontrada" in e for e in erros)

    def test_validation_missing_column(self, qtbot, tmp_path):
        os.chdir(tmp_path)
        data_path = tmp_path / "data.xlsx"
        pd.DataFrame({'Data': [1]}).to_excel(data_path, sheet_name='Aba1', index=False) # Missing 'Servico'
        
        config = {
            'arquivos': {'dados_origem': str(data_path)},
            'posicoes': {'celula_data_atual': 'E3'},
            'mapeamento': {'Aba1': 'B10'},
            'extração': {'colunas': ['Data', 'Servico']}
        }
        with open("config.toml", "wb") as f:
            f.write(tomli_w.dumps(config).encode())
            
        worker = ValidationWorker()
        with qtbot.waitSignal(worker.validation_finished, timeout=2000) as blocker:
            worker.run()
        
        sucesso, erros = blocker.args
        assert sucesso is False
        assert any("coluna 'Servico' inexistente" in e for e in erros)

class TestExcelHandlerErrorScenarios:
    
    def test_file_locked_error(self, tmp_path, monkeypatch):
        # Setup data and template
        data_path = tmp_path / "data.xlsx"
        pd.DataFrame({'Data': [pd.Timestamp('2026-03-01')], 'Servico': ['S1']}).to_excel(data_path, index=False, sheet_name='aba1')
        
        from openpyxl import Workbook
        template_path = tmp_path / "template.xlsx"
        wb = Workbook()
        wb.save(template_path)
        
        config = {
            'projeto': {'ano': 2026, 'mes': 3},
            'arquivos': {
                'dados_origem': str(data_path),
                'template_ativo': str(template_path)
            },
            'posicoes': {'celula_data_atual': 'A1'},
            'extração': {'colunas': ['Data', 'Servico']},
            'mapeamento': {'aba1': 'B1'}
        }
        
        # Simular que o arquivo está aberto forçando um OSError no os.rename
        output_name = "Diario_Consolidado_03_2026.xlsx"
        
        # Change CWD to handle the data/output path
        os.chdir(tmp_path)
        os.makedirs("data/output", exist_ok=True)
        output_path = os.path.join("data", "output", output_name)
        open(output_path, 'a').close() # Create the file
        
        handler = ExcelHandler(config)
        
        with patch('os.rename') as mock_rename:
            mock_rename.side_effect = OSError("File locked")
            with pytest.raises(PermissionError, match="está aberto. Por favor, feche-o"):
                handler.gerar_diario_completo()

import pytest
import os
import tomli_w
from src.app.ui.workers.validation_worker import ValidationWorker
from src.app.core.validator import ReportValidator

class TestValidationWorker:
    
    def test_coordinate_validation_logic(self):
        validator = ReportValidator()
        assert validator.is_valid_excel_coordinate("A1") is True
        assert validator.is_valid_excel_coordinate("Z99") is True
        assert validator.is_valid_excel_coordinate("ABC1000") is True
        assert validator.is_valid_excel_coordinate("A0") is False
        assert validator.is_valid_excel_coordinate("1A") is False
        assert validator.is_valid_excel_coordinate("A") is False
        assert validator.is_valid_excel_coordinate("ZZZZ1") is False

    def test_run_validation_invalid_coordinate(self, qtbot, tmp_path):
        os.chdir(tmp_path)
        config_content = {
            'arquivos': {
                'dados_origem': 'dados.xlsx',
            },
            'posicoes': {
                'celula_data_atual': 'INVALID'
            },
            'mapeamento': {
                'teste': 'B10'
            },
            'extração': {
                'colunas': ['Data', 'Servico']
            }
        }
        with open("config.toml", "wb") as f:
            f.write(tomli_w.dumps(config_content).encode())
            
        (tmp_path / "dados.xlsx").touch()
        
        worker = ValidationWorker()
        with qtbot.waitSignal(worker.validation_finished, timeout=2000) as blocker:
            worker.run()
            
        sucesso, erros = blocker.args
        assert sucesso is False
        assert any("configurada para" in e and "inválida" in e for e in erros)

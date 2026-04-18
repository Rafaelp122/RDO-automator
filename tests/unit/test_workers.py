import pytest
import os
from unittest.mock import MagicMock, patch
from src.app.ui.workers.processor_worker import ProcessorWorker

class TestProcessorWorker:
    
    def test_run_success(self, qtbot, tmp_path, monkeypatch):
        os.chdir(tmp_path)
        
        config_content = {
            'arquivos': {
                'dados_origem': 'dados.xlsx',
                'default_template': 'default.xlsx',
                'user_template': 'user.xlsx'
            }
        }
        with open("config.toml", "wb") as f:
            import tomli_w
            f.write(tomli_w.dumps(config_content).encode())
            
        (tmp_path / "dados.xlsx").touch()
        (tmp_path / "default.xlsx").touch()
        
        worker = ProcessorWorker()
        
        with qtbot.waitSignal(worker.finished, timeout=2000) as blocker:
            with patch('src.app.ui.workers.processor_worker.ReportService') as MockService:
                mock_service_inst = MockService.return_value
                mock_service_inst.generate_report.return_value = "resultado.xlsx"
                
                worker.run()
                
        assert blocker.args == ["resultado.xlsx"]
        mock_service_inst.generate_report.assert_called_once()

    def test_run_config_missing(self, qtbot, tmp_path):
        os.chdir(tmp_path)
        # config.toml NOT created
        
        worker = ProcessorWorker()
        
        with qtbot.waitSignal(worker.error, timeout=2000) as blocker:
            worker.run()
            
        # Error message comes from ConfigManager now
        assert "Arquivo ou diretório inexistente" in blocker.args[0]

    def test_run_data_file_missing(self, qtbot, tmp_path):
        os.chdir(tmp_path)
        config_content = {
            'arquivos': {
                'dados_origem': 'missing_data.xlsx',
                'default_template': 'default.xlsx'
            }
        }
        with open("config.toml", "wb") as f:
            import tomli_w
            f.write(tomli_w.dumps(config_content).encode())
            
        worker = ProcessorWorker()
        
        # We don't need to patch here because the service will raise FileNotFoundError
        with qtbot.waitSignal(worker.error, timeout=2000) as blocker:
            worker.run()
            
        assert "Arquivo de dados não encontrado" in blocker.args[0]

import pytest
import os
from unittest.mock import MagicMock, patch
from src.app.core.report_service import ReportService

class TestReportService:
    @pytest.fixture
    def service(self):
        return ReportService()

    @pytest.fixture
    def base_config(self):
        return {
            'projeto': {'mes': 1, 'ano': 2026},
            'arquivos': {
                'dados_origem': 'data_mock.xlsx',
                'default_template': 'default.xlsx',
                'user_template': 'user.xlsx'
            }
        }

    @patch('os.path.exists')
    def test_generate_report_missing_origin(self, mock_exists, service, base_config):
        # Simula que o arquivo de origem não existe
        mock_exists.return_value = False
        
        with pytest.raises(FileNotFoundError, match="Arquivo de dados não encontrado"):
            service.generate_report(base_config)

    @patch('os.path.exists')
    @patch('src.app.core.report_service.ExcelHandler')
    def test_use_user_template_when_exists(self, mock_handler_cls, mock_exists, service, base_config):
        # Simula que todos os arquivos existem
        mock_exists.return_value = True
        mock_handler = mock_handler_cls.return_value
        mock_handler.gerar_diario_completo.return_value = "output.xlsx"

        result = service.generate_report(base_config)

        # Verifica se o template_ativo foi definido como o do usuário
        assert base_config['arquivos']['template_ativo'] == 'user.xlsx'
        assert result == "output.xlsx"

    @patch('os.path.exists')
    @patch('src.app.core.report_service.ExcelHandler')
    def test_fallback_to_default_template(self, mock_handler_cls, mock_exists, service, base_config):
        # Simula que o de origem existe, o do usuário NÃO, mas o padrão SIM
        mock_exists.side_effect = lambda path: path in ['data_mock.xlsx', 'default.xlsx']
        
        mock_handler = mock_handler_cls.return_value
        mock_handler.gerar_diario_completo.return_value = "output.xlsx"

        service.generate_report(base_config)

        # Verifica se houve o fallback para o template padrão
        assert base_config['arquivos']['template_ativo'] == 'default.xlsx'

    @patch('os.path.exists')
    def test_error_when_no_templates_exist(self, mock_exists, service, base_config):
        # Simula que apenas o arquivo de dados existe
        mock_exists.side_effect = lambda path: path == 'data_mock.xlsx'
        
        with pytest.raises(FileNotFoundError, match="Template padrão não encontrado"):
            service.generate_report(base_config)

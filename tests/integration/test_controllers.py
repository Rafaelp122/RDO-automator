import pytest
from PySide6.QtCore import QTimer
from unittest.mock import MagicMock, patch
from src.app.ui.controllers.main_controller import MainController
from src.app.infra.config_manager import ConfigManager
from src.app.core.config_models import ReportConfig

class TestMainControllerIntegration:
    
    @pytest.fixture
    def mock_config_manager(self, tmp_path):
        config_path = tmp_path / "config.toml"
        manager = ConfigManager(config_path=config_path)
        manager.config = ReportConfig()
        return manager

    def test_controller_saves_on_config_changed_with_debounce(self, qtbot, mock_config_manager):
        # Patch para evitar que a validação real rode (queremos testar o salvamento)
        with patch('src.app.ui.controllers.main_controller.ValidationWorker') as mock_worker:
            controller = MainController(mock_config_manager)
            qtbot.addWidget(controller.view)
            
            # Simular alteração na config via sinal da View
            controller.config.projeto.nome = "Projeto Integrado"
            controller.view.config_changed.emit()
            
            # O timer de 500ms deve ter iniciado
            assert controller._save_timer.isActive()
            
            # Aguardar o debounce disparar (usamos 600ms para garantir)
            qtbot.wait(600)
            
            # Verificar se o ConfigManager.save_config foi chamado (indiretamente via persistência no arquivo)
            assert mock_config_manager.config_path.exists()
            with open(mock_config_manager.config_path, "r") as f:
                content = f.read()
                assert "Projeto Integrado" in content

    def test_controller_import_updates_view_and_model(self, qtbot, mock_config_manager, tmp_path):
        controller = MainController(mock_config_manager)
        qtbot.addWidget(controller.view)
        
        # Criar um arquivo TOML externo para importar
        external_toml = tmp_path / "external.toml"
        external_toml.write_text('[projeto]\nnome = "Importado"\nmes = 5\nano = 2026\n')
        
        # Mock do diálogo de seleção de arquivo
        with patch.object(controller.view, 'get_open_file_path', return_value=str(external_toml)):
            with patch.object(controller.view, 'show_success_dialog') as mock_success:
                controller._import_config()
                
                assert controller.config.projeto.nome == "Importado"
                assert controller.config.projeto.mes == 5
                mock_success.assert_called_once()
        
        # Cleanup: garantir que todas as threads terminem
        while controller._active_threads:
            qtbot.wait(50)

    def test_controller_validation_failure_highlights_ui(self, qtbot, mock_config_manager):
        controller = MainController(mock_config_manager)
        qtbot.addWidget(controller.view)
        
        # Forçar erro de validação injetando uma config inválida
        controller.config.posicoes.celula_data_atual = "INVALIDA"
        
        # Disparar validação
        controller._validate_initial()
        
        # Verificar se o destaque de erro aparece (usando polling para estabilidade)
        widget = controller.view.config_panel.coords_group.input_cel_data_atual
        qtbot.waitUntil(lambda: widget.property("error") is True, timeout=10000)
        
        # Cleanup: garantir que todas as threads terminem antes de sair do teste
        while controller._active_threads:
            qtbot.wait(50)

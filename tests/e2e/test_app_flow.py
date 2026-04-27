import pytest
import os
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QMessageBox
from unittest.mock import MagicMock, patch
from src.app.ui.controllers.main_controller import MainController
from src.app.infra.config_manager import ConfigManager
from src.app.core.config_models import ReportConfig
from src.app.core import constants

class TestAppE2E:

    @pytest.fixture
    def app_controller(self, tmp_path):
        # Configuração limpa
        config_path = tmp_path / "config.toml"
        manager = ConfigManager(config_path=config_path)
        manager.config = ReportConfig()
        
        controller = MainController(manager)
        return controller

    def test_full_journey_success(self, qtbot, app_controller, sample_data_excel, sample_template_excel):
        controller = app_controller
        window = controller.view
        qtbot.addWidget(window)
        
        # 1. Simular preenchimento da ingestão
        controller.config.arquivos.dados_origem = str(sample_data_excel)
        controller.config.arquivos.user_template = str(sample_template_excel)
        controller.config.arquivos.template_ativo = str(sample_template_excel)
        window.config_changed.emit()
        
        # 2. Preencher a Tabela de Mapeamento via UI
        mapping_group = window.config_panel.mapping_group
        mapping_group.add_row("Obras", "B10")
        mapping_group.changed.emit()
        
        # 3. Preencher colunas (Chips) e formato de extração
        extraction_panel = window.extraction_panel
        extraction_panel.input_chip.setText("Servico, Local")
        extraction_panel.input_chip.returnPressed.emit()
        
        extraction_panel.text_formato.setPlainText("{Servico} em {Local}")
        
        # Aguardar o fim de qualquer validação automática em background
        qtbot.wait(1000)
        qtbot.waitUntil(lambda: not controller._active_threads, timeout=10000)
        
        # 4. Iniciar Geração
        with patch.object(window, 'show_success_dialog') as mock_success:
            # Chamada direta ao controlador para garantir execução da lógica
            controller._start_generation()
            
            # Aguardar o processamento completo
            qtbot.waitUntil(lambda: mock_success.called, timeout=30000)
            mock_success.assert_called_once()
            
            # Verificar se o arquivo final existe
            output_dir = constants.OUTPUT_DIR
            files = os.listdir(output_dir)
            assert any("Diario_Consolidado" in f for f in files)

        # Cleanup final
        while controller._active_threads:
            qtbot.wait(50)

    def test_visual_error_feedback_e2e(self, qtbot, app_controller):
        controller = app_controller
        window = controller.view
        qtbot.addWidget(window)
        
        # Forçar erro: Célula inválida
        coords_group = window.config_panel.coords_group
        coords_group.input_cel_data_inicio.setText("XYZ")
        coords_group.input_cel_data_inicio.editingFinished.emit()
        
        # Esperar a propriedade error ser aplicada via polling
        qtbot.waitUntil(lambda: coords_group.input_cel_data_inicio.property("error") is True, timeout=10000)
        
        assert "inválida" in coords_group.input_cel_data_inicio.toolTip()

        # Cleanup final
        while controller._active_threads:
            qtbot.wait(50)

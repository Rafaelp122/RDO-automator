import pytest
import os
import tomllib
from src.app.infra.config_manager import ConfigManager

class TestConfigManager:
    @pytest.fixture
    def config_file(self, tmp_path):
        path = tmp_path / "config.toml"
        content = b'[projeto]\nnome = "Teste"\nano = 2026\n'
        path.write_bytes(content)
        return str(path)

    def test_load_config_success(self, config_file):
        manager = ConfigManager(config_file)
        config = manager.load_config()
        assert config['projeto']['nome'] == "Teste"
        assert config['projeto']['ano'] == 2026

    def test_load_config_file_not_found(self):
        manager = ConfigManager("non_existent.toml")
        config = manager.load_config()
        assert config['projeto']['mes'] is not None

    def test_save_config(self, tmp_path):
        path = tmp_path / "save_test.toml"
        manager = ConfigManager(str(path))
        new_data = {"app": {"version": "1.0"}}
        
        manager.save_config(new_data)
        
        with open(path, "rb") as f:
            saved = tomllib.load(f)
        assert saved["app"]["version"] == "1.0"

    def test_import_config(self, tmp_path):
        source = tmp_path / "source.toml"
        source.write_bytes(b'[new]\nkey = "value"\n')
        
        manager = ConfigManager()
        imported = manager.import_config(str(source))
        
        assert imported["new"]["key"] == "value"
        assert manager.config["new"]["key"] == "value"

    def test_export_config(self, tmp_path):
        target = tmp_path / "export.toml"
        manager = ConfigManager()
        data = {"export": "data"}
        
        manager.export_config(str(target), data)
        
        with open(target, "rb") as f:
            exported = tomllib.load(f)
        assert exported["export"] == "data"

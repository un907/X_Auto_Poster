import pytest
import sys
import os
import json
from unittest.mock import MagicMock, patch

# Add parent directory to path to import main
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Mock customtkinter to avoid GUI issues during import
sys.modules["customtkinter"] = MagicMock()
sys.modules["tkinter"] = MagicMock()

import main

class TestSettingsManager:
    def test_default_settings(self):
        """Test that default settings are loaded when file is missing"""
        with patch("os.path.exists", return_value=False):
            settings = main.SettingsManager.load()
            assert settings["headless"] is False
            assert settings["wait_min"] == 120
            assert settings["auto_like"] is True

    def test_save_settings(self, tmp_path):
        """Test saving settings to a file"""
        # Use a temporary file
        test_file = tmp_path / "settings.json"
        main.SettingsManager.SETTINGS_FILE = str(test_file)
        
        data = {"test_key": "test_value"}
        main.SettingsManager.save(data)
        
        assert test_file.exists()
        with open(test_file, "r", encoding="utf-8") as f:
            loaded = json.load(f)
            assert loaded["test_key"] == "test_value"

class TestPersonaManager:
    def test_load_empty(self):
        """Test loading when file is missing"""
        with patch("os.path.exists", return_value=False):
            personas = main.PersonaManager.load()
            assert personas == {}

class TestPostGeneration:
    def test_template_generation_morning(self):
        """Test template generation logic (Morning)"""
        # Mock app instance
        app = MagicMock()
        app.settings = {"ai_mode": False, "gif_probability": 0}
        app.log = MagicMock()
        
        # Mock datetime to return morning hour (e.g., 8 AM)
        with patch("datetime.datetime") as mock_datetime:
            mock_datetime.now.return_value.hour = 8
            
            # Call the method using the class, passing the mock app as self
            content = main.AutoPostApp.generate_post_content(app, "test_user")
            
            assert content is not None
            assert len(content) > 0
            # Check if it contains an emoji (simple check for template format)
            # Template format: "{emoji} {action} {emoji}" or similar
            # We just ensure it returns a string.
            assert isinstance(content, str)

    def test_template_generation_night(self):
        """Test template generation logic (Night)"""
        app = MagicMock()
        app.settings = {"ai_mode": False, "gif_probability": 0}
        app.log = MagicMock()
        
        with patch("datetime.datetime") as mock_datetime:
            mock_datetime.now.return_value.hour = 20
            
            content = main.AutoPostApp.generate_post_content(app, "test_user")
            assert content is not None
            assert isinstance(content, str)

if __name__ == "__main__":
    pytest.main()

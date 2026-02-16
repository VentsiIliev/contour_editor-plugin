"""
Tests for SettingsService.
This module tests:
- Singleton pattern
- Configuration management
- File operations (load/save)
- Default settings management
- Batch segment updates
"""
import pytest
import json
import os
from unittest.mock import Mock, patch, mock_open, MagicMock
from pathlib import Path
@pytest.fixture
def settings_service():
    """Create a fresh SettingsService for each test."""
    from contour_editor.domain.services.settings_service import SettingsService
    # Reset singleton
    SettingsService._instance = None
    service = SettingsService(settings_file_path="/tmp/test_settings.json")
    yield service
    # Cleanup
    SettingsService._instance = None
@pytest.fixture
def sample_config():
    """Create a sample SettingsConfig."""
    from contour_editor.model.SettingsConfig import SettingsConfig
    return SettingsConfig(
        default_settings={"color": "red", "width": "2"},
        groups=["group1", "group2"],
        combo_field_key="mode"
    )
# ===== Singleton Tests =====
def test_settings_service_singleton():
    """Test that SettingsService follows singleton pattern."""
    from contour_editor.domain.services.settings_service import SettingsService
    SettingsService._instance = None
    service1 = SettingsService.get_instance()
    service2 = SettingsService.get_instance()
    assert service1 is service2
    SettingsService._instance = None
# ===== Configuration Tests =====
def test_configure(settings_service, sample_config):
    """Test service configuration."""
    with patch.object(settings_service, 'initialize_default_settings'):
        settings_service.configure(sample_config)
    assert settings_service.default_settings == {"color": "red", "width": "2"}
    assert settings_service._settings_groups == ["group1", "group2"]
    assert settings_service._combo_field_key == "mode"
def test_get_defaults(settings_service):
    """Test retrieving default settings."""
    settings_service.default_settings = {"color": "blue", "width": "3"}
    result = settings_service.get_defaults()
    assert result == {"color": "blue", "width": "3"}
    # Should return a copy, not the original
    result["color"] = "green"
    assert settings_service.default_settings["color"] == "blue"
def test_get_combo_field_key(settings_service):
    """Test retrieving combo field key."""
    settings_service._combo_field_key = "test_key"
    result = settings_service.get_combo_field_key()
    assert result == "test_key"
def test_get_settings_groups(settings_service):
    """Test retrieving settings groups."""
    settings_service._settings_groups = ["g1", "g2", "g3"]
    result = settings_service.get_settings_groups()
    assert result == ["g1", "g2", "g3"]
# ===== File Operations Tests =====
def test_load_from_file_success(settings_service):
    """Test loading settings from existing file."""
    mock_data = {"color": "yellow", "width": "5"}
    with patch('builtins.open', mock_open(read_data=json.dumps(mock_data))):
        with patch('os.path.exists', return_value=True):
            result = settings_service.load_from_file()
    assert result == mock_data
def test_load_from_file_not_exists(settings_service):
    """Test loading when file doesn't exist."""
    with patch('os.path.exists', return_value=False):
        result = settings_service.load_from_file()
    assert result == {}
def test_load_from_file_error(settings_service):
    """Test loading with file read error."""
    with patch('builtins.open', side_effect=IOError("Read error")):
        with patch('os.path.exists', return_value=True):
            result = settings_service.load_from_file()
    assert result == {}
def test_save_to_file_success(settings_service, tmp_path):
    """Test saving settings to file."""
    settings_service.settings_file_path = str(tmp_path / "test_settings.json")
    test_settings = {"color": "purple", "width": "7"}
    settings_service.save_to_file(test_settings)
    # Verify file was created and contains correct data
    assert os.path.exists(settings_service.settings_file_path)
    with open(settings_service.settings_file_path, 'r') as f:
        saved_data = json.load(f)
    assert saved_data == test_settings
def test_save_to_file_creates_directory(settings_service, tmp_path):
    """Test that save creates directory if it doesn't exist."""
    nested_path = tmp_path / "nested" / "dir"
    settings_service.settings_file_path = str(nested_path / "settings.json")
    test_settings = {"test": "data"}
    settings_service.save_to_file(test_settings)
    assert os.path.exists(settings_service.settings_file_path)
def test_save_to_file_error(settings_service):
    """Test save with write error."""
    settings_service.settings_file_path = "/invalid/path/settings.json"
    test_settings = {"test": "data"}
    # Should not crash, just log error
    with patch('os.makedirs', side_effect=OSError("Permission denied")):
        settings_service.save_to_file(test_settings)
    # No assertion needed - just verify it doesn't crash
# ===== Settings Management Tests =====
def test_update_defaults(settings_service):
    """Test updating default settings."""
    settings_service.default_settings = {"color": "red", "width": "2"}
    with patch.object(settings_service, 'save_to_file') as mock_save:
        settings_service.update_defaults({"color": "green", "size": "10"})
    assert settings_service.default_settings["color"] == "green"
    assert settings_service.default_settings["size"] == "10"
    mock_save.assert_called_once()
def test_initialize_default_settings(settings_service):
    """Test initializing defaults from file."""
    settings_service.default_settings = {"color": "red", "width": "2", "extra": "value"}
    file_settings = {"color": "blue", "width": "5"}
    with patch.object(settings_service, 'load_from_file', return_value=file_settings):
        settings_service.initialize_default_settings()
    # Should update existing keys
    assert settings_service.default_settings["color"] == "blue"
    assert settings_service.default_settings["width"] == "5"
    # Should keep keys not in file
    assert settings_service.default_settings["extra"] == "value"
def test_initialize_default_settings_empty_file(settings_service):
    """Test initializing when file is empty."""
    settings_service.default_settings = {"color": "red"}
    with patch.object(settings_service, 'load_from_file', return_value={}):
        settings_service.initialize_default_settings()
    # Should remain unchanged
    assert settings_service.default_settings["color"] == "red"
# ===== Batch Operations Tests =====
def test_apply_to_all_segments(settings_service, mock_manager):
    """Test applying settings to all segments."""
    seg1 = Mock()
    seg1.set_settings = Mock()
    seg2 = Mock()
    seg2.set_settings = Mock()
    seg3 = Mock()
    seg3.set_settings = Mock()
    mock_manager.get_segments = Mock(return_value=[seg1, seg2, seg3])
    test_settings = {"color": "orange", "width": "4"}
    settings_service.apply_to_all_segments(mock_manager, test_settings)
    seg1.set_settings.assert_called_once_with(test_settings)
    seg2.set_settings.assert_called_once_with(test_settings)
    seg3.set_settings.assert_called_once_with(test_settings)
def test_apply_to_all_segments_empty(settings_service, mock_manager):
    """Test applying settings when no segments exist."""
    mock_manager.get_segments = Mock(return_value=[])
    test_settings = {"color": "orange"}
    # Should not crash
    settings_service.apply_to_all_segments(mock_manager, test_settings)
    # Just verify it runs without error
    assert mock_manager.get_segments.called
# Override the last test
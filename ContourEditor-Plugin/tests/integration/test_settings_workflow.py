"""
Integration tests for settings workflows.
This module tests end-to-end settings operations:
- Save and load settings workflow
- Apply to all segments workflow
- Default settings workflow
- Settings persistence workflow
"""
import pytest
import json
import os
from unittest.mock import Mock, patch
from pathlib import Path
@pytest.fixture
def settings_workflow_setup(tmp_path):
    """Setup for settings workflow tests."""
    from contour_editor.services.settings_service import SettingsService
    from contour_editor.models.settings_config import SettingsConfig
    # Reset singleton
    SettingsService._instance = None
    # Create service with temp file
    settings_file = tmp_path / "test_settings.json"
    service = SettingsService(settings_file_path=str(settings_file))
    # Configure with test settings
    config = SettingsConfig(
        default_settings={"color": "red", "width": "2"},
        groups=["visual", "behavior"],
        combo_field_key="mode"
    )
    with patch.object(service, 'initialize_default_settings'):
        service.configure(config)
    yield {
        'service': service,
        'settings_file': settings_file
    }
    # Cleanup
    SettingsService._instance = None
def test_save_load_settings_workflow(settings_workflow_setup):
    """Test complete save and load settings workflow."""
    setup = settings_workflow_setup
    service = setup['service']
    settings_file = setup['settings_file']
    # Workflow: Update and save settings
    new_settings = {
        "color": "blue",
        "width": "5",
        "opacity": "0.8"
    }
    service.save_to_file(new_settings)
    # Verify file was created
    assert settings_file.exists()
    # Workflow: Load settings from file
    loaded = service.load_from_file()
    assert loaded == new_settings
    assert loaded["color"] == "blue"
    assert loaded["width"] == "5"
    assert loaded["opacity"] == "0.8"
def test_apply_to_all_segments_workflow(settings_workflow_setup, mock_manager):
    """Test applying settings to all segments."""
    setup = settings_workflow_setup
    service = setup['service']
    # Setup segments
    seg1 = Mock()
    seg1.set_settings = Mock()
    seg2 = Mock()
    seg2.set_settings = Mock()
    seg3 = Mock()
    seg3.set_settings = Mock()
    mock_manager.get_segments = Mock(return_value=[seg1, seg2, seg3])
    # Workflow: Apply settings to all
    test_settings = {
        "color": "green",
        "width": "3",
        "visible": True
    }
    service.apply_to_all_segments(mock_manager, test_settings)
    # Verify all segments received settings
    seg1.set_settings.assert_called_once_with(test_settings)
    seg2.set_settings.assert_called_once_with(test_settings)
    seg3.set_settings.assert_called_once_with(test_settings)
def test_default_settings_workflow(settings_workflow_setup):
    """Test default settings management workflow."""
    setup = settings_workflow_setup
    service = setup['service']
    # Initial defaults
    initial_defaults = service.get_defaults()
    assert initial_defaults["color"] == "red"
    assert initial_defaults["width"] == "2"
    # Workflow: Update defaults
    new_defaults = {
        "color": "yellow",
        "width": "10",
        "style": "dashed"
    }
    service.update_defaults(new_defaults)
    # Verify defaults updated
    updated_defaults = service.get_defaults()
    assert updated_defaults["color"] == "yellow"
    assert updated_defaults["width"] == "10"
    assert updated_defaults["style"] == "dashed"
    # Verify file was updated
    settings_file = setup['settings_file']
    assert settings_file.exists()
    with open(settings_file, 'r') as f:
        saved_data = json.load(f)
    assert saved_data["color"] == "yellow"
def test_settings_persistence_workflow(tmp_path):
    """Test settings persistence across service instances."""
    from contour_editor.services.settings_service import SettingsService
    from contour_editor.models.settings_config import SettingsConfig
    settings_file = tmp_path / "persistent_settings.json"
    # Workflow Part 1: Create service and save settings
    SettingsService._instance = None
    service1 = SettingsService(settings_file_path=str(settings_file))
    config = SettingsConfig(
        default_settings={"color": "red", "width": "2"},
        groups=[],
        combo_field_key=""
    )
    with patch.object(service1, 'initialize_default_settings'):
        service1.configure(config)
    # Save settings
    persistent_settings = {
        "color": "purple",
        "width": "7",
        "persistent": "yes"
    }
    service1.save_to_file(persistent_settings)
    # Workflow Part 2: Create new service instance and load settings
    SettingsService._instance = None
    service2 = SettingsService(settings_file_path=str(settings_file))
    # Load previously saved settings
    loaded_settings = service2.load_from_file()
    # Verify persistence
    assert loaded_settings == persistent_settings
    assert loaded_settings["color"] == "purple"
    assert loaded_settings["width"] == "7"
    assert loaded_settings["persistent"] == "yes"
    # Cleanup
    SettingsService._instance = None

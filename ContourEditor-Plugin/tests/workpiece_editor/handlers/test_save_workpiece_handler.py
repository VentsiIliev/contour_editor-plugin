import pytest
from unittest.mock import Mock, patch
from workpiece_editor.handlers.SaveWorkpieceHandler import SaveWorkpieceHandler
class TestSaveWorkpieceHandlerDataExport:
    """Test data export functionality"""
    def test_export_data_basic(self):
        """Test basic export_data without Field dependency"""
        mock_workpiece_manager = Mock()
        mock_editor_data = Mock()
        mock_workpiece_manager.export_editor_data.return_value = mock_editor_data
        with patch.object(SaveWorkpieceHandler, '_merge_data') as mock_merge:
            with patch('workpiece_editor.handlers.SaveWorkpieceHandler.WorkpieceAdapter') as mock_adapter:
                mock_adapter.to_workpiece_data.return_value = {
                    "main_contour": Mock(),
                    "spray_pattern": {}
                }
                mock_merge.return_value = {"workpieceId": "WP123"}
                form_data = {"workpieceId": "WP123", "name": "Test"}
                result = SaveWorkpieceHandler.export_data(mock_workpiece_manager, form_data)
                assert result is not None
                mock_adapter.to_workpiece_data.assert_called_once()
                mock_merge.assert_called_once()
    def test_export_data_calls_adapter(self):
        """Test that export_data calls WorkpieceAdapter"""
        mock_workpiece_manager = Mock()
        mock_editor_data = Mock()
        mock_workpiece_manager.export_editor_data.return_value = mock_editor_data
        with patch.object(SaveWorkpieceHandler, '_merge_data') as mock_merge:
            with patch('workpiece_editor.handlers.SaveWorkpieceHandler.WorkpieceAdapter') as mock_adapter:
                mock_adapter.to_workpiece_data.return_value = {
                    "main_contour": Mock(),
                    "spray_pattern": {}
                }
                mock_merge.return_value = {}
                SaveWorkpieceHandler.export_data(mock_workpiece_manager, {})
                mock_adapter.to_workpiece_data.assert_called_once_with(mock_editor_data)
# Skip tests that require WorkpieceFieldProvider implementation
@pytest.mark.skip(reason="Requires WorkpieceFieldProvider implementation")
class TestSaveWorkpieceHandlerValidation:
    """Test validation functionality - SKIPPED until WorkpieceFieldProvider exists"""
    def test_placeholder(self):
        pass
@pytest.mark.skip(reason="Requires WorkpieceFieldProvider implementation")
class TestSaveWorkpieceHandlerSaveWorkflow:
    """Test save workflow - SKIPPED until WorkpieceFieldProvider exists"""
    def test_placeholder(self):
        pass
@pytest.mark.skip(reason="Requires WorkpieceFieldProvider implementation")
class TestSaveWorkpieceHandlerEdgeCases:
    """Test edge cases - SKIPPED until WorkpieceFieldProvider exists"""
    def test_placeholder(self):
        pass

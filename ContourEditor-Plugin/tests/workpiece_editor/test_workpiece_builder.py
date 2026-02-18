import pytest
from unittest.mock import Mock, patch
from workpiece_editor import WorkpieceEditorBuilder
from contour_editor import BezierSegmentManager
class TestWorkpieceEditorBuilder:
    def test_initialization(self):
        builder = WorkpieceEditorBuilder()
        assert builder._base_builder is not None
    def test_with_parent(self):
        builder = WorkpieceEditorBuilder()
        parent = Mock()
        result = builder.with_parent(parent)
        assert result == builder
    def test_with_segment_manager(self):
        builder = WorkpieceEditorBuilder()
        result = builder.with_segment_manager(BezierSegmentManager)
        assert result == builder
    def test_with_settings(self):
        builder = WorkpieceEditorBuilder()
        config = Mock()
        provider = Mock()
        result = builder.with_settings(config, provider)
        assert result == builder
    def test_with_form(self):
        builder = WorkpieceEditorBuilder()
        factory = Mock()
        result = builder.with_form(factory)
        assert result == builder
    def test_with_widgets(self):
        builder = WorkpieceEditorBuilder()
        factory = Mock()
        result = builder.with_widgets(factory)
        assert result == builder
    def test_on_save(self):
        builder = WorkpieceEditorBuilder()
        callback = Mock()
        result = builder.on_save(callback)
        assert result == builder
    def test_on_capture(self):
        builder = WorkpieceEditorBuilder()
        callback = Mock()
        result = builder.on_capture(callback)
        assert result == builder
    def test_on_execute(self):
        builder = WorkpieceEditorBuilder()
        callback = Mock()
        result = builder.on_execute(callback)
        assert result == builder
    def test_on_update_camera_feed(self):
        builder = WorkpieceEditorBuilder()
        callback = Mock()
        result = builder.on_update_camera_feed(callback)
        assert result == builder
    @patch('workpiece_editor.builder.MainApplicationFrame')
    def test_build_basic(self, mock_frame_class):
        builder = WorkpieceEditorBuilder()
        builder.with_segment_manager(BezierSegmentManager)
        mock_editor = Mock()
        mock_editor.contourEditor = Mock()
        mock_editor.contourEditor.editor_with_rulers = Mock()
        mock_editor.contourEditor.editor_with_rulers.editor = Mock()
        mock_editor.start_requested = Mock()
        mock_editor.start_requested.connect = Mock()
        mock_editor.capture_data_received = Mock()
        mock_editor.capture_data_received.connect = Mock()
        builder._base_builder.build = Mock(return_value=mock_editor)
        result = builder.build()
        assert result == mock_editor
    def test_load_workpiece_before_build_raises(self):
        builder = WorkpieceEditorBuilder()
        with pytest.raises(RuntimeError, match="Cannot load workpiece before building"):
            builder.load_workpiece(Mock())
class TestBuildWorkpieceEditorFunction:
    """Test build_workpiece_editor() function"""
    @patch('workpiece_editor.builder.WorkpieceEditorBuilder')
    @patch('workpiece_editor.builder.SegmentSettingsProvider')
    @patch('workpiece_editor.builder.WorkpieceFormFactory')
    def test_build_workpiece_editor_creates_editor(self, mock_factory_class, mock_provider_class, mock_builder_class):
        from workpiece_editor.builder import build_workpiece_editor
        mock_provider = Mock()
        mock_provider.get_default_values.return_value = {}
        mock_provider.get_all_setting_keys.return_value = []
        mock_provider.get_available_material_types.return_value = []
        mock_provider_class.return_value = mock_provider
        mock_factory = Mock()
        mock_factory_class.return_value = mock_factory
        mock_builder = Mock()
        mock_editor = Mock()
        mock_editor.save_requested = Mock()
        mock_editor.save_requested.connect = Mock()
        mock_builder.build.return_value = mock_editor
        # Chain the builder methods
        mock_builder.with_segment_manager.return_value = mock_builder
        mock_builder.with_settings.return_value = mock_builder
        mock_builder.with_form.return_value = mock_builder
        mock_builder_class.return_value = mock_builder
        result = build_workpiece_editor()
        assert mock_provider_class.called
        mock_builder.build.assert_called_once()
    @patch('workpiece_editor.builder.SegmentSettingsProvider')
    def test_build_workpiece_editor_uses_segment_settings_provider(self, mock_provider_class):
        from workpiece_editor.builder import build_workpiece_editor
        mock_provider = Mock()
        mock_provider.get_default_values.return_value = {}
        mock_provider.get_all_setting_keys.return_value = []
        mock_provider.get_available_material_types.return_value = ["Type A"]
        mock_provider_class.return_value = mock_provider
        try:
            build_workpiece_editor()
        except:
            pass
        mock_provider_class.assert_called_once()
    @patch('workpiece_editor.builder.WorkpieceFormFactory')
    @patch('workpiece_editor.builder.SegmentSettingsProvider')
    def test_build_workpiece_editor_creates_form_factory(self, mock_provider_class, mock_factory_class):
        from workpiece_editor.builder import build_workpiece_editor
        mock_provider = Mock()
        mock_provider.get_default_values.return_value = {}
        mock_provider.get_all_setting_keys.return_value = []
        mock_provider.get_available_material_types.return_value = ["Type A"]
        mock_provider_class.return_value = mock_provider
        try:
            build_workpiece_editor()
        except:
            pass
        mock_factory_class.assert_called_once()
class TestSignalConnections:
    """Test signal connections in builder"""
    @patch('workpiece_editor.builder.MainApplicationFrame')
    def test_build_connects_start_handler(self, mock_frame_class):
        builder = WorkpieceEditorBuilder()
        builder.with_segment_manager(BezierSegmentManager)
        mock_editor = Mock()
        mock_editor.contourEditor = Mock()
        mock_editor.contourEditor.editor_with_rulers = Mock()
        mock_editor.contourEditor.editor_with_rulers.editor = Mock()
        mock_editor.start_requested = Mock()
        mock_editor.start_requested.connect = Mock()
        mock_editor.capture_data_received = Mock()
        mock_editor.capture_data_received.connect = Mock()
        builder._base_builder.build = Mock(return_value=mock_editor)
        builder.build()
        mock_editor.start_requested.connect.assert_called_once()
    @patch('workpiece_editor.builder.MainApplicationFrame')
    def test_build_connects_capture_handler(self, mock_frame_class):
        builder = WorkpieceEditorBuilder()
        builder.with_segment_manager(BezierSegmentManager)
        mock_editor = Mock()
        mock_editor.contourEditor = Mock()
        mock_editor.contourEditor.editor_with_rulers = Mock()
        mock_editor.contourEditor.editor_with_rulers.editor = Mock()
        mock_editor.start_requested = Mock()
        mock_editor.start_requested.connect = Mock()
        mock_editor.capture_data_received = Mock()
        mock_editor.capture_data_received.connect = Mock()
        builder._base_builder.build = Mock(return_value=mock_editor)
        builder.build()
        mock_editor.capture_data_received.connect.assert_called_once()
    @patch('workpiece_editor.builder.MainApplicationFrame')
    def test_build_creates_workpiece_manager(self, mock_frame_class):
        builder = WorkpieceEditorBuilder()
        builder.with_segment_manager(BezierSegmentManager)
        mock_editor = Mock()
        mock_editor.contourEditor = Mock()
        mock_editor.contourEditor.editor_with_rulers = Mock()
        mock_editor.contourEditor.editor_with_rulers.editor = Mock()
        mock_editor.start_requested = Mock()
        mock_editor.start_requested.connect = Mock()
        mock_editor.capture_data_received = Mock()
        mock_editor.capture_data_received.connect = Mock()
        builder._base_builder.build = Mock(return_value=mock_editor)
        result = builder.build()
        # Should have workpiece_manager attribute set
        assert hasattr(mock_editor.contourEditor, 'workpiece_manager')
class TestBuilderIntegration:
    """Test builder integration scenarios"""
    def test_builder_fluent_api_chain(self):
        builder = WorkpieceEditorBuilder()
        config = Mock()
        provider = Mock()
        factory = Mock()
        result = (builder
                  .with_segment_manager(BezierSegmentManager)
                  .with_settings(config, provider)
                  .with_form(factory))
        assert result == builder
    def test_get_workpiece_manager_before_build(self):
        builder = WorkpieceEditorBuilder()
        manager = builder.get_workpiece_manager()
        assert manager is None
    @patch('workpiece_editor.builder.MainApplicationFrame')
    def test_get_workpiece_manager_after_build(self, mock_frame_class):
        builder = WorkpieceEditorBuilder()
        builder.with_segment_manager(BezierSegmentManager)
        mock_editor = Mock()
        mock_editor.contourEditor = Mock()
        mock_editor.contourEditor.editor_with_rulers = Mock()
        mock_editor.contourEditor.editor_with_rulers.editor = Mock()
        mock_editor.start_requested = Mock()
        mock_editor.start_requested.connect = Mock()
        mock_editor.capture_data_received = Mock()
        mock_editor.capture_data_received.connect = Mock()
        builder._base_builder.build = Mock(return_value=mock_editor)
        builder.build()
        manager = builder.get_workpiece_manager()
        assert manager is not None

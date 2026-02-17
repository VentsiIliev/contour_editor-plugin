"""
Tests for Command Pattern implementations.
This module tests:
- AddSegmentCommand
- DeleteSegmentCommand
- ToggleSegmentVisibilityCommand
- ChangeSegmentLayerCommand
- Command execution, undo, redo
"""
import pytest
from unittest.mock import Mock, patch
from PyQt6.QtCore import QPointF
@pytest.fixture
def mock_segment_with_layer():
    """Create a mock segment with layer."""
    segment = Mock()
    segment.visible = True
    segment.points = [QPointF(0, 0), QPointF(100, 100)]
    segment.layer = Mock()
    segment.layer.name = "Contour"
    return segment
# ===== AddSegmentCommand Tests =====
def test_add_segment_execute(mock_manager, mock_event_bus):
    """Test AddSegmentCommand execution creates a segment."""
    from contour_editor.services.commands.segment_commands import AddSegmentCommand
    new_segment = Mock()
    mock_manager.start_new_segment = Mock(return_value=(new_segment, True))
    mock_manager.segments = []
    cmd = AddSegmentCommand(mock_manager, "Contour")
    with patch('contour_editor.services.commands.segment_commands.EventBus.get_instance', return_value=mock_event_bus):
        cmd.execute()
    mock_manager.start_new_segment.assert_called_once_with("Contour")
    assert cmd._executed is True
def test_add_segment_undo(mock_manager, mock_event_bus):
    """Test AddSegmentCommand undo removes the segment."""
    from contour_editor.services.commands.segment_commands import AddSegmentCommand
    new_segment = Mock()
    mock_manager.start_new_segment = Mock(return_value=(new_segment, True))
    mock_manager.segments = [new_segment]
    cmd = AddSegmentCommand(mock_manager, "Contour")
    with patch('contour_editor.services.commands.segment_commands.EventBus.get_instance', return_value=mock_event_bus):
        cmd.execute()
        cmd.undo()
    assert len(mock_manager.segments) == 0
def test_add_segment_redo(mock_manager, mock_event_bus):
    """Test AddSegmentCommand redo re-creates segment."""
    from contour_editor.services.commands.segment_commands import AddSegmentCommand

    # Simulate segment list growth on each start_new_segment call
    def add_segment_side_effect(layer_name):
        new_seg = Mock()
        mock_manager.segments.append(new_seg)
        return (new_seg, True)

    mock_manager.start_new_segment = Mock(side_effect=add_segment_side_effect)
    mock_manager.segments = []
    cmd = AddSegmentCommand(mock_manager, "Contour")
    with patch('contour_editor.services.commands.segment_commands.EventBus.get_instance', return_value=mock_event_bus):
        cmd.execute()
        assert len(mock_manager.segments) == 1
        cmd.undo()
        assert len(mock_manager.segments) == 0
        cmd.execute()  # Redo is just execute again
        assert len(mock_manager.segments) == 1
    assert mock_manager.start_new_segment.call_count == 2
# ===== DeleteSegmentCommand Tests =====
def test_delete_segment_execute(mock_manager, mock_event_bus, mock_segment_with_layer):
    """Test DeleteSegmentCommand execution deletes segment."""
    from contour_editor.services.commands.segment_commands import DeleteSegmentCommand
    mock_manager.segments = [mock_segment_with_layer]
    mock_manager.delete_segment = Mock()
    cmd = DeleteSegmentCommand(mock_manager, 0)
    with patch('contour_editor.services.commands.segment_commands.EventBus.get_instance', return_value=mock_event_bus):
        cmd.execute()
    mock_manager.delete_segment.assert_called_once_with(0)
    assert cmd.deleted_segment == mock_segment_with_layer
def test_delete_segment_undo(mock_manager, mock_event_bus, mock_segment_with_layer):
    """Test DeleteSegmentCommand undo restores segment."""
    from contour_editor.services.commands.segment_commands import DeleteSegmentCommand
    mock_manager.segments = [mock_segment_with_layer]
    mock_manager.delete_segment = Mock(side_effect=lambda idx: mock_manager.segments.pop(idx))
    cmd = DeleteSegmentCommand(mock_manager, 0)
    with patch('contour_editor.services.commands.segment_commands.EventBus.get_instance', return_value=mock_event_bus):
        cmd.execute()
        assert len(mock_manager.segments) == 0
        cmd.undo()
        assert len(mock_manager.segments) == 1
        assert mock_manager.segments[0] == mock_segment_with_layer
def test_delete_segment_redo(mock_manager, mock_event_bus, mock_segment_with_layer):
    """Test DeleteSegmentCommand redo removes segment again."""
    from contour_editor.services.commands.segment_commands import DeleteSegmentCommand
    mock_manager.segments = [mock_segment_with_layer]
    mock_manager.delete_segment = Mock(side_effect=lambda idx: mock_manager.segments.pop(idx) if idx < len(mock_manager.segments) else None)
    cmd = DeleteSegmentCommand(mock_manager, 0)
    with patch('contour_editor.services.commands.segment_commands.EventBus.get_instance', return_value=mock_event_bus):
        cmd.execute()
        cmd.undo()
        # Executing again acts as redo
        cmd.execute()
    assert mock_manager.delete_segment.call_count == 2
def test_delete_segment_invalid_index(mock_manager, mock_event_bus):
    """Test DeleteSegmentCommand handles invalid index gracefully."""
    from contour_editor.services.commands.segment_commands import DeleteSegmentCommand
    mock_manager.segments = []
    cmd = DeleteSegmentCommand(mock_manager, 999)
    with patch('contour_editor.services.commands.segment_commands.EventBus.get_instance', return_value=mock_event_bus):
        cmd.execute()  # Should not crash
    assert cmd.deleted_segment is None
# ===== ToggleSegmentVisibilityCommand Tests =====
def test_toggle_visibility_execute(mock_manager, mock_event_bus, mock_segment_with_layer):
    """Test ToggleSegmentVisibilityCommand toggles visibility."""
    from contour_editor.services.commands.segment_commands import ToggleSegmentVisibilityCommand
    mock_manager.segments = [mock_segment_with_layer]
    mock_segment_with_layer.visible = True
    cmd = ToggleSegmentVisibilityCommand(mock_manager, 0)
    with patch('contour_editor.services.commands.segment_commands.EventBus.get_instance', return_value=mock_event_bus):
        cmd.execute()
    assert mock_segment_with_layer.visible is False
def test_toggle_visibility_undo(mock_manager, mock_event_bus, mock_segment_with_layer):
    """Test ToggleSegmentVisibilityCommand undo restores visibility."""
    from contour_editor.services.commands.segment_commands import ToggleSegmentVisibilityCommand
    mock_manager.segments = [mock_segment_with_layer]
    mock_segment_with_layer.visible = True
    cmd = ToggleSegmentVisibilityCommand(mock_manager, 0)
    with patch('contour_editor.services.commands.segment_commands.EventBus.get_instance', return_value=mock_event_bus):
        cmd.execute()
        assert mock_segment_with_layer.visible is False
        cmd.undo()
        assert mock_segment_with_layer.visible is True
# ===== ChangeSegmentLayerCommand Tests =====
def test_change_layer_execute(mock_manager, mock_event_bus, mock_segment_with_layer):
    """Test ChangeSegmentLayerCommand changes layer."""
    from contour_editor.services.commands.segment_commands import ChangeSegmentLayerCommand
    mock_manager.segments = [mock_segment_with_layer]
    mock_manager.assign_segment_layer = Mock()
    cmd = ChangeSegmentLayerCommand(mock_manager, 0, "Fill")
    with patch('contour_editor.services.commands.segment_commands.EventBus.get_instance', return_value=mock_event_bus):
        cmd.execute()
    mock_manager.assign_segment_layer.assert_called_once_with(0, "Fill")
    assert cmd.old_layer_name == "Contour"
def test_change_layer_undo(mock_manager, mock_event_bus, mock_segment_with_layer):
    """Test ChangeSegmentLayerCommand undo restores old layer."""
    from contour_editor.services.commands.segment_commands import ChangeSegmentLayerCommand
    mock_manager.segments = [mock_segment_with_layer]
    mock_manager.assign_segment_layer = Mock()
    cmd = ChangeSegmentLayerCommand(mock_manager, 0, "Fill")
    with patch('contour_editor.services.commands.segment_commands.EventBus.get_instance', return_value=mock_event_bus):
        cmd.execute()
        cmd.undo()
    # Should be called twice: once for execute, once for undo
    assert mock_manager.assign_segment_layer.call_count == 2
    # Second call should restore original layer
    second_call_args = mock_manager.assign_segment_layer.call_args_list[1]
    assert second_call_args[0] == (0, "Contour")

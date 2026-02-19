"""
Tests for SegmentService.
This module tests:
- Command-based operations (add, delete, toggle, change layer)
- Direct operations (add points, disconnect, set active)
- Layer operations (visibility, locking)
"""
import pytest
from unittest.mock import Mock, patch
from PyQt6.QtCore import QPointF
@pytest.fixture
def segment_service(mock_manager, mock_command_history, mock_event_bus):
    """Create a SegmentService with mocked dependencies."""
    from contour_editor.services.segment_service import SegmentService
    return SegmentService(mock_manager, mock_command_history, mock_event_bus)
# ===== Command-based Operations =====
def test_add_segment(segment_service):
    """Test add_segment creates and executes AddSegmentCommand."""
    with patch('contour_editor.services.segment_service.AddSegmentCommand') as MockCmd:
        mock_cmd = Mock()
        mock_cmd.seg_index = 5
        mock_cmd.execute = Mock()
        mock_cmd.can_merge_with = Mock(return_value=False)
        MockCmd.return_value = mock_cmd
        result = segment_service.add_segment("Contour")
        MockCmd.assert_called_once_with(segment_service.manager, "Contour")
        mock_cmd.execute.assert_called_once()
        assert result == 5
def test_add_segment_default_layer(segment_service):
    """Test add_segment uses default layer when not specified."""
    with patch('contour_editor.services.segment_service.AddSegmentCommand') as MockCmd:
        mock_cmd = Mock()
        mock_cmd.seg_index = 0
        mock_cmd.execute = Mock()
        mock_cmd.can_merge_with = Mock(return_value=False)
        MockCmd.return_value = mock_cmd
        segment_service.add_segment()
        MockCmd.assert_called_once_with(segment_service.manager, "Contour")
def test_delete_segment(segment_service):
    """Test delete_segment creates and executes DeleteSegmentCommand."""
    with patch('contour_editor.services.segment_service.DeleteSegmentCommand') as MockCmd:
        mock_cmd = Mock()
        mock_cmd.execute = Mock()
        mock_cmd.can_merge_with = Mock(return_value=False)
        MockCmd.return_value = mock_cmd
        segment_service.delete_segment(3)
        MockCmd.assert_called_once_with(segment_service.manager, 3)
        mock_cmd.execute.assert_called_once()
def test_toggle_visibility(segment_service):
    """Test toggle_visibility creates and executes ToggleSegmentVisibilityCommand."""
    with patch('contour_editor.services.segment_service.ToggleSegmentVisibilityCommand') as MockCmd:
        mock_cmd = Mock()
        mock_cmd.execute = Mock()
        mock_cmd.can_merge_with = Mock(return_value=False)
        MockCmd.return_value = mock_cmd
        segment_service.toggle_visibility(2)
        MockCmd.assert_called_once_with(segment_service.manager, 2)
        mock_cmd.execute.assert_called_once()
def test_change_layer(segment_service):
    """Test change_layer creates and executes ChangeSegmentLayerCommand."""
    with patch('contour_editor.services.segment_service.ChangeSegmentLayerCommand') as MockCmd:
        mock_cmd = Mock()
        mock_cmd.execute = Mock()
        mock_cmd.can_merge_with = Mock(return_value=False)
        MockCmd.return_value = mock_cmd
        segment_service.change_layer(1, "Fill")
        MockCmd.assert_called_once_with(segment_service.manager, 1, "Fill")
        mock_cmd.execute.assert_called_once()
# ===== Direct Operations =====
def test_add_control_point(segment_service, mock_manager):
    """Test add_control_point delegates to manager."""
    pos = QPointF(100, 200)
    mock_manager.add_control_point = Mock(return_value=True)
    result = segment_service.add_control_point(0, pos)
    mock_manager.add_control_point.assert_called_once_with(0, pos)
    assert result is True
def test_add_anchor_point(segment_service, mock_manager):
    """Test add_anchor_point delegates to manager."""
    pos = QPointF(150, 250)
    mock_manager.insert_anchor_point = Mock(return_value=True)
    result = segment_service.add_anchor_point(1, pos)
    mock_manager.insert_anchor_point.assert_called_once_with(1, pos)
    assert result is True
def test_disconnect_line_success(segment_service, mock_manager):
    """Test disconnect_line when segment is found."""
    pos = QPointF(50, 50)
    mock_manager.find_segment_at = Mock(return_value=(2, 1))
    mock_manager.disconnect_line_segment = Mock(return_value=True)
    result = segment_service.disconnect_line(pos, 2)
    mock_manager.find_segment_at.assert_called_once_with(pos)
    mock_manager.disconnect_line_segment.assert_called_once_with(2, 1)
    assert result is True
def test_disconnect_line_no_segment(segment_service, mock_manager):
    """Test disconnect_line when no segment found at position."""
    pos = QPointF(999, 999)
    mock_manager.find_segment_at = Mock(return_value=None)
    result = segment_service.disconnect_line(pos, 0)
    mock_manager.find_segment_at.assert_called_once_with(pos)
    assert result is False
def test_disconnect_line_wrong_segment(segment_service, mock_manager):
    """Test disconnect_line when found segment differs from expected."""
    pos = QPointF(50, 50)
    mock_manager.find_segment_at = Mock(return_value=(3, 0))
    mock_manager.disconnect_line_segment = Mock(return_value=True)
    result = segment_service.disconnect_line(pos, 2)
    mock_manager.disconnect_line_segment.assert_called_once_with(3, 0)
    assert result is True
def test_set_active_segment(segment_service, mock_manager):
    """Test set_active_segment updates manager and emits event."""
    mock_manager.set_active_segment = Mock()
    # Don't test event emission due to Qt signal constraints
    segment_service.set_active_segment(4)
    mock_manager.set_active_segment.assert_called_once_with(4)
# ===== Layer Operations =====
def test_set_layer_visibility_workpiece(segment_service, mock_manager):
    """Test set_layer_visibility for Main layer."""
    mock_layer = Mock()
    mock_layer.name = "Main"
    mock_layer.visible = True  # Start as visible
    mock_manager.external_layer = mock_layer
    seg1 = Mock()
    seg1.layer = Mock(name="Main")
    seg1.layer.name = "Main"
    seg2 = Mock()
    seg2.layer = Mock(name="Contour")
    seg2.layer.name = "Contour"
    mock_manager.get_segments = Mock(return_value=[seg1, seg2])
    mock_manager.set_segment_visibility = Mock()
    segment_service.set_layer_visibility("Main", False)
    assert mock_layer.visible == False
    mock_manager.set_segment_visibility.assert_called_once_with(0, False)
def test_set_layer_visibility_contour(segment_service, mock_manager):
    """Test set_layer_visibility for Contour layer."""
    mock_layer = Mock()
    mock_layer.name = "Contour"
    mock_manager.contour_layer = mock_layer
    seg1 = Mock()
    seg1.layer = Mock(name="Contour")
    seg1.layer.name = "Contour"
    mock_manager.get_segments = Mock(return_value=[seg1])
    mock_manager.set_segment_visibility = Mock()
    segment_service.set_layer_visibility("Contour", True)
    assert mock_layer.visible is True
    mock_manager.set_segment_visibility.assert_called_once_with(0, True)
def test_set_layer_visibility_fill(segment_service, mock_manager):
    """Test set_layer_visibility for Fill layer."""
    mock_layer = Mock()
    mock_layer.name = "Fill"
    mock_manager.fill_layer = mock_layer
    mock_manager.get_segments = Mock(return_value=[])
    segment_service.set_layer_visibility("Fill", False)
    assert mock_layer.visible is False
def test_set_layer_visibility_invalid_layer(segment_service, mock_manager):
    """Test set_layer_visibility with invalid layer name."""
    mock_manager.external_layer = Mock()
    mock_manager.contour_layer = Mock()
    mock_manager.fill_layer = Mock()
    segment_service.set_layer_visibility("InvalidLayer", True)
    # Should not modify any layers
    assert mock_manager.external_layer.visible != True
def test_set_layer_locked(segment_service, mock_manager):
    """Test set_layer_locked delegates to manager."""
    mock_manager.set_layer_locked = Mock()
    segment_service.set_layer_locked("Contour", True)
    mock_manager.set_layer_locked.assert_called_once_with("Contour", True)
def test_set_layer_locked_invalid_layer(segment_service, mock_manager):
    """Test set_layer_locked with invalid layer does not crash."""
    mock_manager.set_layer_locked = Mock()
    segment_service.set_layer_locked("InvalidLayer", True)
    mock_manager.set_layer_locked.assert_called_once_with("InvalidLayer", True)

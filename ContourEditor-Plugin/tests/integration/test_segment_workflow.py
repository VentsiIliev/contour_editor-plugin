"""
Integration tests for segment workflows.
This module tests end-to-end segment operations:
- Add/delete segment workflows
- Visibility toggle with undo
- Layer change with undo
- Complex operation sequences
- Full undo/redo cycles
"""
import pytest
from unittest.mock import Mock, patch
from PyQt6.QtCore import QPointF
@pytest.fixture
def segment_workflow_setup(mock_manager, mock_command_history, mock_event_bus):
    """Setup for segment workflow tests."""
    from contour_editor.domain.services.segment_service import SegmentService
    service = SegmentService(mock_manager, mock_command_history, mock_event_bus)
    return {
        'service': service,
        'manager': mock_manager,
        'history': mock_command_history,
        'event_bus': mock_event_bus
    }
def test_add_delete_segment_workflow(segment_workflow_setup):
    """Test complete add and delete segment workflow."""
    setup = segment_workflow_setup
    service = setup['service']
    manager = setup['manager']
    history = setup['history']
    # Mock segment creation
    seg1 = Mock()
    seg1.layer = Mock(name="Contour")
    manager.start_new_segment = Mock(return_value=(seg1, True))
    manager.segments = []
    with patch('contour_editor.services.segment_service.AddSegmentCommand') as AddCmd:
        with patch('contour_editor.services.segment_service.DeleteSegmentCommand') as DelCmd:
            # Create mock commands
            add_cmd = Mock()
            add_cmd.seg_index = 0
            add_cmd.execute = Mock(side_effect=lambda: manager.segments.append(seg1))
            add_cmd.undo = Mock(side_effect=lambda: manager.segments.clear())
            add_cmd.can_merge_with = Mock(return_value=False)
            AddCmd.return_value = add_cmd
            del_cmd = Mock()
            del_cmd.execute = Mock(side_effect=lambda: manager.segments.clear())
            del_cmd.undo = Mock(side_effect=lambda: manager.segments.append(seg1))
            del_cmd.can_merge_with = Mock(return_value=False)
            DelCmd.return_value = del_cmd
            # Workflow: Add segment
            seg_idx = service.add_segment("Contour")
            assert seg_idx == 0
            assert len(manager.segments) == 1
            # Workflow: Undo add (removes segment)
            history.undo()
            assert len(manager.segments) == 0
            # Workflow: Redo add (restores segment)
            history.redo()
            assert len(manager.segments) == 1
            # Workflow: Delete segment
            service.delete_segment(0)
            assert len(manager.segments) == 0
            # Workflow: Undo delete (restores segment)
            history.undo()
            assert len(manager.segments) == 1
def test_segment_visibility_workflow(segment_workflow_setup):
    """Test visibility toggle workflow with undo/redo."""
    setup = segment_workflow_setup
    service = setup['service']
    manager = setup['manager']
    history = setup['history']
    # Setup segment
    seg = Mock()
    seg.visible = True
    manager.segments = [seg]
    with patch('contour_editor.services.segment_service.ToggleSegmentVisibilityCommand') as ToggleCmd:
        # Create mock command
        toggle_cmd = Mock()
        toggle_cmd.execute = Mock(side_effect=lambda: setattr(seg, 'visible', not seg.visible))
        toggle_cmd.undo = Mock(side_effect=lambda: setattr(seg, 'visible', not seg.visible))
        toggle_cmd.can_merge_with = Mock(return_value=False)
        ToggleCmd.return_value = toggle_cmd
        # Initial state: visible
        assert seg.visible is True
        # Toggle off
        service.toggle_visibility(0)
        assert seg.visible is False
        # Undo toggle (back to visible)
        history.undo()
        assert seg.visible is True
        # Redo toggle (back to hidden)
        history.redo()
        assert seg.visible is False
def test_segment_layer_change_workflow(segment_workflow_setup):
    """Test layer change workflow with undo/redo."""
    setup = segment_workflow_setup
    service = setup['service']
    manager = setup['manager']
    history = setup['history']
    # Setup segment
    seg = Mock()
    layer_mock = Mock()
    layer_mock.name = "Contour"
    seg.layer = layer_mock
    manager.segments = [seg]
    manager.assign_segment_layer = Mock()
    with patch('contour_editor.services.segment_service.ChangeSegmentLayerCommand') as ChangeCmd:
        # Create mock command
        change_cmd = Mock()
        original_layer = "Contour"
        new_layer = "Fill"
        def execute_change():
            seg.layer.name = new_layer
        def undo_change():
            seg.layer.name = original_layer
        change_cmd.execute = Mock(side_effect=execute_change)
        change_cmd.undo = Mock(side_effect=undo_change)
        change_cmd.old_layer_name = original_layer
        change_cmd.can_merge_with = Mock(return_value=False)
        ChangeCmd.return_value = change_cmd
        # Initial: Contour layer
        assert seg.layer.name == "Contour"
        # Change to Fill
        service.change_layer(0, "Fill")
        assert seg.layer.name == "Fill"
        # Undo (back to Contour)
        history.undo()
        assert seg.layer.name == "Contour"
        # Redo (back to Fill)
        history.redo()
        assert seg.layer.name == "Fill"
def test_multiple_segment_operations(segment_workflow_setup):
    """Test complex sequence of segment operations."""
    setup = segment_workflow_setup
    service = setup['service']
    manager = setup['manager']
    history = setup['history']
    # Setup
    segments = []
    manager.segments = segments
    with patch('contour_editor.services.segment_service.AddSegmentCommand') as AddCmd:
        with patch('contour_editor.services.segment_service.ToggleSegmentVisibilityCommand') as ToggleCmd:
            # Mock add commands
            def create_add_cmd(idx):
                cmd = Mock()
                seg = Mock()
                seg.visible = True
                cmd.seg_index = idx
                cmd.execute = Mock(side_effect=lambda: segments.append(seg))
                cmd.undo = Mock(side_effect=lambda: segments.pop())
                cmd.can_merge_with = Mock(return_value=False)
                return cmd
            AddCmd.side_effect = lambda mgr, layer: create_add_cmd(len(segments))
            # Mock visibility commands
            def create_toggle_cmd(idx):
                cmd = Mock()
                cmd.execute = Mock(side_effect=lambda: setattr(segments[idx], 'visible', not segments[idx].visible))
                cmd.undo = Mock(side_effect=lambda: setattr(segments[idx], 'visible', not segments[idx].visible))
                cmd.can_merge_with = Mock(return_value=False)
                return cmd
            ToggleCmd.side_effect = lambda mgr, idx: create_toggle_cmd(idx)
            # Complex workflow
            # 1. Add three segments
            service.add_segment("Contour")
            service.add_segment("Fill")
            service.add_segment("Workpiece")
            assert len(segments) == 3
            # 2. Toggle visibility of first segment
            service.toggle_visibility(0)
            assert segments[0].visible is False
            # 3. Undo visibility toggle
            history.undo()
            assert segments[0].visible is True
            # 4. Undo last add (removes workpiece segment)
            history.undo()
            assert len(segments) == 2
            # 5. Redo (restores workpiece segment)
            history.redo()
            assert len(segments) == 3
def test_undo_redo_workflow(segment_workflow_setup):
    """Test full undo/redo cycle with multiple operations."""
    setup = segment_workflow_setup
    service = setup['service']
    manager = setup['manager']
    history = setup['history']
    segments = []
    manager.segments = segments
    with patch('contour_editor.services.segment_service.AddSegmentCommand') as AddCmd:
        # Setup add command mock
        def create_add_cmd(idx):
            cmd = Mock()
            seg = Mock()
            seg.visible = True
            layer_mock = Mock()
            layer_mock.name = "Contour"
            seg.layer = layer_mock
            cmd.seg_index = idx
            cmd.execute = Mock(side_effect=lambda: segments.append(seg))
            cmd.undo = Mock(side_effect=lambda: segments.pop() if segments else None)
            cmd.can_merge_with = Mock(return_value=False)
            return cmd
        AddCmd.side_effect = lambda mgr, layer: create_add_cmd(len(segments))
        # Add two segments
        service.add_segment("Contour")
        service.add_segment("Fill")
        assert len(segments) == 2
        assert history.can_undo()
        assert not history.can_redo()
        # Undo once
        history.undo()
        assert len(segments) == 1
        assert history.can_undo()
        assert history.can_redo()
        # Undo again
        history.undo()
        assert len(segments) == 0
        assert not history.can_undo()
        assert history.can_redo()
        # Redo once
        history.redo()
        assert len(segments) == 1
        assert history.can_undo()
        assert history.can_redo()
        # Redo again
        history.redo()
        assert len(segments) == 2
        assert history.can_undo()
        assert not history.can_redo()

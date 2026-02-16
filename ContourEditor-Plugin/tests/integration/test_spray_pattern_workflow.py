"""
Integration tests for spray pattern workflows.
This module tests end-to-end spray pattern operations:
- Pattern generation workflow
- Shrink contour workflow  
- Fill pattern workflow
- Contour pattern workflow
- Pattern with layer management
"""
import pytest
import numpy as np
from unittest.mock import Mock, patch
from PyQt6.QtCore import QPointF
@pytest.fixture
def pattern_workflow_setup(mock_manager):
    """Setup for spray pattern workflow tests."""
    from contour_editor.domain.services.contour_processing_service import ContourProcessingService
    service = ContourProcessingService(mock_manager)
    # Sample square contour
    contour = np.array([
        [10.0, 10.0],
        [110.0, 10.0],
        [110.0, 110.0],
        [10.0, 110.0],
        [10.0, 10.0]
    ], dtype=np.float32)
    return {
        'service': service,
        'manager': mock_manager,
        'contour': contour
    }
def test_generate_spray_pattern_workflow(pattern_workflow_setup):
    """Test end-to-end spray pattern generation."""
    setup = pattern_workflow_setup
    service = setup['service']
    manager = setup['manager']
    contour = setup['contour']
    # Setup workpiece segment
    workpiece_seg = Mock()
    workpiece_seg.layer = Mock(name="Workpiece")
    workpiece_seg.layer.name = "Workpiece"
    workpiece_seg.points = [
        QPointF(10, 10),
        QPointF(110, 10),
        QPointF(110, 110),
        QPointF(10, 110),
        QPointF(10, 10)
    ]
    manager.get_segments = Mock(return_value=[workpiece_seg])
    with patch('contour_editor.services.contour_processing_service.generate_spray_pattern') as mock_gen:
        # Mock spray pattern generation
        mock_gen.return_value = [
            np.array([[20, 30], [100, 30]]),
            np.array([[100, 40], [20, 40]]),
        ]
        # Workflow: Extract contour
        contour_pts = service.get_workpiece_contour_points()
        assert contour_pts is not None
        assert contour_pts.shape[0] == 5
        # Workflow: Generate pattern
        zigzag = service.generate_spray_pattern(contour_pts, spacing=10.0)
        assert len(zigzag) == 2
        # Workflow: Create segments from pattern
        manager.create_segment = Mock(return_value=Mock())
        manager.segments = []
        segments = service.create_segments_from_points(zigzag, "Fill")
        assert len(segments) == 2
def test_shrink_contour_workflow(pattern_workflow_setup):
    """Test shrink contour with segment creation."""
    setup = pattern_workflow_setup
    service = setup['service']
    manager = setup['manager']
    contour = setup['contour']
    with patch('contour_editor.services.contour_processing_service.shrink_contour_points') as mock_shrink:
        # Mock shrink result
        mock_shrink.return_value = np.array([
            [20.0, 20.0],
            [100.0, 20.0],
            [100.0, 100.0],
            [20.0, 100.0],
            [20.0, 20.0]
        ])
        # Workflow: Shrink contour
        result = service.shrink_contour(contour, shrink_amount=10.0)
        assert result is not None
        assert len(result) == 4  # 5 points = 4 line segments
        # Workflow: Create segments from shrunk contour
        manager.create_segment = Mock(return_value=Mock())
        manager.segments = []
        segments = service.create_segments_from_points(result, "Contour")
        assert len(segments) == 4
def test_fill_pattern_workflow(pattern_workflow_setup):
    """Test fill pattern generation (continuous path)."""
    setup = pattern_workflow_setup
    service = setup['service']
    manager = setup['manager']
    contour = setup['contour']
    with patch('contour_editor.services.contour_processing_service.Polygon'):
        # Mock zigzag segments
        zigzag_segments = [
            np.array([[10, 20], [110, 20]]),
            np.array([[110, 30], [10, 30]]),
            np.array([[10, 40], [110, 40]]),
        ]
        # Setup manager
        manager.create_segment = Mock(return_value=Mock())
        manager.segments = []
        # Workflow: Create fill pattern (single continuous segment)
        segments = service.create_fill_pattern(zigzag_segments, "Fill", contour)
        assert len(segments) == 1  # One continuous path
        manager.create_segment.assert_called_once()
def test_contour_pattern_workflow(pattern_workflow_setup):
    """Test contour pattern generation (individual segments)."""
    setup = pattern_workflow_setup
    service = setup['service']
    manager = setup['manager']
    # Mock zigzag segments
    zigzag_segments = [
        np.array([[10, 20], [110, 20]]),
        np.array([[110, 30], [10, 30]]),
        np.array([[10, 40], [110, 40]]),
    ]
    # Setup manager
    manager.create_segment = Mock(return_value=Mock())
    manager.segments = []
    # Workflow: Create contour pattern (separate segments)
    segments = service.create_contour_pattern(zigzag_segments, "Contour")
    assert len(segments) == 3  # Three separate segments
    assert manager.create_segment.call_count == 3
def test_pattern_with_layer_management(pattern_workflow_setup, mock_command_history, mock_event_bus):
    """Test pattern generation with layer management."""
    setup = pattern_workflow_setup
    contour_service = setup['service']
    manager = setup['manager']
    contour = setup['contour']
    from contour_editor.domain.services.segment_service import SegmentService
    segment_service = SegmentService(manager, mock_command_history, mock_event_bus)
    # Setup workpiece
    workpiece_seg = Mock()
    workpiece_seg.layer = Mock(name="Workpiece")
    workpiece_seg.layer.name = "Workpiece"
    workpiece_seg.points = [QPointF(c[0], c[1]) for c in contour]
    manager.get_segments = Mock(return_value=[workpiece_seg])
    manager.contour_layer = Mock(name="Contour", visible=True)
    manager.fill_layer = Mock(name="Fill", visible=True)
    with patch('contour_editor.services.contour_processing_service.generate_spray_pattern') as mock_gen:
        # Mock pattern
        mock_gen.return_value = [
            np.array([[20, 30], [100, 30]]),
        ]
        # Workflow: Extract contour
        contour_pts = contour_service.get_workpiece_contour_points()
        assert contour_pts is not None
        # Workflow: Generate pattern
        zigzag = contour_service.generate_spray_pattern(contour_pts, spacing=10.0)
        assert len(zigzag) == 1
        # Workflow: Create segments in Fill layer
        manager.create_segment = Mock(return_value=Mock())
        manager.segments = []
        segments = contour_service.create_segments_from_points(zigzag, "Fill")
        assert len(segments) == 1
        # Workflow: Manage layer visibility
        fill_seg = Mock()
        fill_seg.layer = Mock(name="Fill")
        fill_seg.layer.name = "Fill"
        manager.get_segments = Mock(return_value=[fill_seg])
        manager.set_segment_visibility = Mock()
        segment_service.set_layer_visibility("Fill", False)
        assert manager.fill_layer.visible is False
        manager.set_segment_visibility.assert_called_once_with(0, False)

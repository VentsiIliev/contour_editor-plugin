"""
Tests for ContourProcessingService.
This module tests:
- Contour extraction from workpiece
- Contour shrinking operations
- Spray pattern generation
- Segment creation from points
- Fill and contour pattern creation
"""
import pytest
import numpy as np
from unittest.mock import Mock, patch, MagicMock
from PyQt6.QtCore import QPointF
@pytest.fixture
def contour_service(mock_manager):
    """Create ContourProcessingService with mocked manager."""
    from contour_editor.domain.services.contour_processing_service import ContourProcessingService
    return ContourProcessingService(mock_manager)
@pytest.fixture
def square_contour():
    """Create a simple square contour."""
    return np.array([
        [10.0, 10.0],
        [110.0, 10.0],
        [110.0, 110.0],
        [10.0, 110.0],
        [10.0, 10.0]
    ], dtype=np.float32)
@pytest.fixture
def triangle_contour():
    """Create a simple triangle contour."""
    return np.array([
        [50.0, 10.0],
        [100.0, 100.0],
        [0.0, 100.0],
        [50.0, 10.0]
    ], dtype=np.float32)
# ===== Contour Extraction Tests =====
def test_get_workpiece_contour_points(contour_service, mock_manager):
    """Test extraction of workpiece contour points."""
    workpiece_seg = Mock()
    workpiece_seg.layer = Mock(name="Workpiece")
    workpiece_seg.layer.name = "Workpiece"
    workpiece_seg.points = [QPointF(0, 0), QPointF(100, 0), QPointF(100, 100), QPointF(0, 100)]
    other_seg = Mock()
    other_seg.layer = Mock(name="Contour")
    other_seg.layer.name = "Contour"
    mock_manager.get_segments = Mock(return_value=[workpiece_seg, other_seg])
    result = contour_service.get_workpiece_contour_points()
    assert result is not None
    assert isinstance(result, np.ndarray)
    assert result.shape == (4, 2)
    assert result[0, 0] == 0.0
    assert result[0, 1] == 0.0
def test_get_workpiece_contour_points_no_workpiece(contour_service, mock_manager):
    """Test when no workpiece segment exists."""
    seg = Mock()
    seg.layer = Mock(name="Contour")
    seg.layer.name = "Contour"
    mock_manager.get_segments = Mock(return_value=[seg])
    result = contour_service.get_workpiece_contour_points()
    assert result is None
def test_get_workpiece_contour_points_insufficient_points(contour_service, mock_manager):
    """Test when workpiece has too few points."""
    workpiece_seg = Mock()
    workpiece_seg.layer = Mock(name="Workpiece")
    workpiece_seg.layer.name = "Workpiece"
    workpiece_seg.points = [QPointF(0, 0), QPointF(100, 0)]  # Only 2 points
    mock_manager.get_segments = Mock(return_value=[workpiece_seg])
    result = contour_service.get_workpiece_contour_points()
    assert result is None
# ===== Shrink Contour Tests =====
def test_shrink_contour(contour_service, square_contour):
    """Test contour shrinking operation."""
    with patch('contour_editor.services.contour_processing_service.shrink_contour_points') as mock_shrink:
        # Return a smaller square
        mock_shrink.return_value = np.array([
            [20.0, 20.0],
            [100.0, 20.0],
            [100.0, 100.0],
            [20.0, 100.0],
            [20.0, 20.0]
        ])
        result = contour_service.shrink_contour(square_contour, 10.0)
        mock_shrink.assert_called_once_with(square_contour, 10.0)
        assert result is not None
        assert len(result) == 4  # 5 points = 4 segments
def test_shrink_contour_invalid_input(contour_service):
    """Test shrink with invalid contour."""
    result = contour_service.shrink_contour(None, 10.0)
    assert result is None
    result = contour_service.shrink_contour(np.array([[0, 0]]), 10.0)
    assert result is None
def test_shrink_contour_failed_shrink(contour_service, square_contour):
    """Test when shrink operation fails."""
    with patch('contour_editor.services.contour_processing_service.shrink_contour_points') as mock_shrink:
        mock_shrink.return_value = None
        result = contour_service.shrink_contour(square_contour, 100.0)
        assert result is None
def test_shrink_contour_too_small_result(contour_service, square_contour):
    """Test when shrink results in too small contour."""
    with patch('contour_editor.services.contour_processing_service.shrink_contour_points') as mock_shrink:
        mock_shrink.return_value = np.array([[50.0, 50.0]])  # Only 1 point
        result = contour_service.shrink_contour(square_contour, 50.0)
        assert result is None
# ===== Spray Pattern Generation Tests =====
def test_generate_spray_pattern(contour_service, square_contour):
    """Test spray pattern generation."""
    with patch('contour_editor.services.contour_processing_service.generate_spray_pattern') as mock_pattern:
        mock_pattern.return_value = [
            np.array([[10, 20], [110, 20]]),
            np.array([[110, 30], [10, 30]]),
        ]
        result = contour_service.generate_spray_pattern(square_contour, 10.0)
        mock_pattern.assert_called_once()
        assert len(result) == 2
def test_generate_spray_pattern_with_shrink(contour_service, square_contour):
    """Test spray pattern with shrink offset."""
    with patch('contour_editor.services.contour_processing_service.shrink_contour_points') as mock_shrink:
        with patch('contour_editor.services.contour_processing_service.generate_spray_pattern') as mock_pattern:
            mock_shrink.return_value = square_contour - 5  # Shrunk contour
            mock_pattern.return_value = [np.array([[15, 25], [105, 25]])]
            result = contour_service.generate_spray_pattern(square_contour, 10.0, shrink_offset=5.0)
            mock_shrink.assert_called_once_with(square_contour, 5.0)
            assert len(result) == 1
def test_generate_spray_pattern_invalid_contour(contour_service):
    """Test spray pattern with invalid contour."""
    result = contour_service.generate_spray_pattern(None, 10.0)
    assert result == []
    result = contour_service.generate_spray_pattern(np.array([[0, 0]]), 10.0)
    assert result == []
def test_generate_spray_pattern_shrink_failed(contour_service, square_contour):
    """Test spray pattern when shrink fails."""
    with patch('contour_editor.services.contour_processing_service.shrink_contour_points') as mock_shrink:
        mock_shrink.return_value = None
        result = contour_service.generate_spray_pattern(square_contour, 10.0, shrink_offset=100.0)
        assert result == []
# ===== Segment Creation Tests =====
def test_create_segments_from_points(contour_service, mock_manager):
    """Test creating segments from point lists."""
    point_lists = [
        [QPointF(0, 0), QPointF(100, 0)],
        [QPointF(100, 0), QPointF(100, 100)],
    ]
    mock_seg1 = Mock()
    mock_seg2 = Mock()
    mock_manager.create_segment = Mock(side_effect=[mock_seg1, mock_seg2])
    mock_manager.segments = []
    result = contour_service.create_segments_from_points(point_lists, "Fill")
    assert len(result) == 2
    assert len(mock_manager.segments) == 2
    assert mock_manager.create_segment.call_count == 2
def test_create_segments_from_points_numpy(contour_service, mock_manager):
    """Test creating segments from numpy arrays."""
    point_lists = [
        np.array([[0, 0], [100, 0]]),
        np.array([[100, 0], [100, 100]]),
    ]
    mock_seg = Mock()
    mock_manager.create_segment = Mock(return_value=mock_seg)
    mock_manager.segments = []
    result = contour_service.create_segments_from_points(point_lists, "Fill")
    assert len(result) == 2
def test_create_segments_from_points_empty(contour_service, mock_manager):
    """Test with empty point lists."""
    mock_manager.segments = []
    result = contour_service.create_segments_from_points([], "Fill")
    assert result == []
    assert len(mock_manager.segments) == 0
def test_create_segments_from_points_invalid(contour_service, mock_manager):
    """Test with invalid point data."""
    point_lists = [
        None,
        [QPointF(0, 0)],  # Only 1 point
        [QPointF(100, 0), QPointF(100, 100)],  # Valid
    ]
    mock_seg = Mock()
    mock_manager.create_segment = Mock(return_value=mock_seg)
    mock_manager.segments = []
    result = contour_service.create_segments_from_points(point_lists, "Fill")
    assert len(result) == 1  # Only the valid one
# ===== Fill Pattern Tests =====
def test_create_fill_pattern(contour_service, mock_manager, square_contour):
    """Test fill pattern creation (continuous zigzag)."""
    with patch('contour_editor.services.contour_processing_service.Polygon'):
        zigzag_segments = [
            np.array([[10, 20], [110, 20]]),
            np.array([[110, 30], [10, 30]]),
            np.array([[10, 40], [110, 40]]),
        ]
        mock_seg = Mock()
        mock_manager.create_segment = Mock(return_value=mock_seg)
        mock_manager.segments = []
        result = contour_service.create_fill_pattern(zigzag_segments, "Fill", square_contour)
        assert len(result) == 1  # One continuous segment
        mock_manager.create_segment.assert_called_once()
def test_create_fill_pattern_empty(contour_service, mock_manager, square_contour):
    """Test fill pattern with empty zigzag."""
    result = contour_service.create_fill_pattern([], "Fill", square_contour)
    assert result == []
    result = contour_service.create_fill_pattern(None, "Fill", square_contour)
    assert result == []
# ===== Contour Pattern Tests =====
def test_create_contour_pattern(contour_service, mock_manager):
    """Test contour pattern creation (individual segments)."""
    zigzag_segments = [
        np.array([[10, 20], [110, 20]]),
        np.array([[110, 30], [10, 30]]),
        np.array([[10, 40], [110, 40]]),
    ]
    mock_seg1 = Mock()
    mock_seg2 = Mock()
    mock_seg3 = Mock()
    mock_manager.create_segment = Mock(side_effect=[mock_seg1, mock_seg2, mock_seg3])
    mock_manager.segments = []
    result = contour_service.create_contour_pattern(zigzag_segments, "Contour")
    assert len(result) == 3  # Three separate segments
    assert mock_manager.create_segment.call_count == 3
def test_create_contour_pattern_alternating_direction(contour_service, mock_manager):
    """Test that contour pattern alternates direction."""
    zigzag_segments = [
        np.array([[10, 20], [110, 20]]),
        np.array([[110, 30], [10, 30]]),
    ]
    mock_seg = Mock()
    mock_manager.create_segment = Mock(return_value=mock_seg)
    mock_manager.segments = []
    result = contour_service.create_contour_pattern(zigzag_segments, "Contour")
    # Check that create_segment was called with reversed points for second segment
    calls = mock_manager.create_segment.call_args_list
    assert len(calls) == 2
def test_create_contour_pattern_empty(contour_service, mock_manager):
    """Test contour pattern with empty input."""
    result = contour_service.create_contour_pattern([], "Contour")
    assert result == []
    result = contour_service.create_contour_pattern(None, "Contour")
    assert result == []

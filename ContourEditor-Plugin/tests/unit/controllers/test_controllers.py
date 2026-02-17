"""
Comprehensive Test Suite for Controllers

This module tests:
- SegmentActionController (segment operations, control/anchor points, disconnection)
- ViewportController (zoom, pan, image management, coordinate mapping)
"""
import pytest
import numpy as np
from unittest.mock import Mock, patch
from PyQt6.QtCore import QPointF
from PyQt6.QtGui import QImage


@pytest.fixture
def mock_bezier_manager():
    """Create a mock BezierSegmentManager."""
    manager = Mock()
    manager.segments = []
    manager.active_segment_index = 0
    manager.start_new_segment = Mock(return_value=(Mock(), True))
    manager.get_segments = Mock(return_value=manager.segments)
    manager.delete_segment = Mock()
    manager.disconnect_line_segment = Mock(return_value=True)
    manager.find_segment_at = Mock()
    manager.add_control_point = Mock(return_value=True)
    manager.insert_anchor_point = Mock(return_value=True)
    return manager


@pytest.fixture
def mock_segment_service():
    """Create a mock SegmentService."""
    service = Mock()
    service.disconnect_line = Mock(return_value=True)
    service.add_control_point = Mock(return_value=True)
    service.add_anchor_point = Mock(return_value=True)
    return service


@pytest.fixture
def mock_editor():
    """Create a mock editor widget."""
    editor = Mock()
    editor.width = Mock(return_value=800)
    editor.height = Mock(return_value=600)
    editor.update = Mock()
    editor.grabGesture = Mock()
    editor.ungrabGesture = Mock()
    return editor


class TestSegmentActionController:
    """Tests for SegmentActionController"""

    def test_initialization_with_manager_only(self, mock_bezier_manager):
        """Test SegmentActionController initialization with only manager"""
        from contour_editor.controllers.SegmentActionController import SegmentActionController

        controller = SegmentActionController(mock_bezier_manager)

        assert controller.bezier_manager is mock_bezier_manager
        assert controller.segment_service is None

    def test_initialization_with_service(self, mock_bezier_manager, mock_segment_service):
        """Test SegmentActionController initialization with service"""
        from contour_editor.controllers.SegmentActionController import SegmentActionController

        controller = SegmentActionController(mock_bezier_manager, mock_segment_service)

        assert controller.bezier_manager is mock_bezier_manager
        assert controller.segment_service is mock_segment_service

    def test_add_new_segment_success(self, mock_bezier_manager):
        """Test adding a new segment successfully"""
        from contour_editor.controllers.SegmentActionController import SegmentActionController

        new_segment = Mock()
        mock_bezier_manager.start_new_segment.return_value = (new_segment, True)
        mock_bezier_manager.get_segments.return_value = [new_segment]

        controller = SegmentActionController(mock_bezier_manager)
        result = controller.add_new_segment("Contour")

        assert result is new_segment
        mock_bezier_manager.start_new_segment.assert_called_once_with("Contour")

    def test_add_new_segment_default_layer(self, mock_bezier_manager):
        """Test adding a new segment with default layer"""
        from contour_editor.controllers.SegmentActionController import SegmentActionController

        new_segment = Mock()
        mock_bezier_manager.start_new_segment.return_value = (new_segment, True)

        controller = SegmentActionController(mock_bezier_manager)
        controller.add_new_segment()

        mock_bezier_manager.start_new_segment.assert_called_once_with("Contour")

    def test_add_new_segment_locked_layer(self, mock_bezier_manager):
        """Test adding a new segment on locked layer"""
        from contour_editor.controllers.SegmentActionController import SegmentActionController

        mock_bezier_manager.start_new_segment.return_value = (None, False)

        controller = SegmentActionController(mock_bezier_manager)
        result = controller.add_new_segment("Contour")

        assert result is None

    def test_add_new_segment_fill_layer(self, mock_bezier_manager):
        """Test adding a new segment on Fill layer"""
        from contour_editor.controllers.SegmentActionController import SegmentActionController

        new_segment = Mock()
        mock_bezier_manager.start_new_segment.return_value = (new_segment, True)

        controller = SegmentActionController(mock_bezier_manager)
        controller.add_new_segment("Fill")

        mock_bezier_manager.start_new_segment.assert_called_once_with("Fill")

    def test_delete_segment(self, mock_bezier_manager):
        """Test deleting a segment"""
        from contour_editor.controllers.SegmentActionController import SegmentActionController

        controller = SegmentActionController(mock_bezier_manager)
        controller.delete_segment(0)

        mock_bezier_manager.delete_segment.assert_called_once_with(0)

    def test_delete_segment_invalid_index(self, mock_bezier_manager):
        """Test deleting segment with invalid index"""
        from contour_editor.controllers.SegmentActionController import SegmentActionController

        controller = SegmentActionController(mock_bezier_manager)
        controller.delete_segment(999)

        mock_bezier_manager.delete_segment.assert_called_once_with(999)

    def test_on_add_control_point_requested_with_service(self, mock_bezier_manager, mock_segment_service):
        """Test adding control point with segment service"""
        from contour_editor.controllers.SegmentActionController import SegmentActionController

        pos = QPointF(50, 50)
        seg_index = 0
        mock_segment_service.add_control_point.return_value = True

        controller = SegmentActionController(mock_bezier_manager, mock_segment_service)
        result = controller.on_add_control_point_requested(pos, seg_index)

        assert result is True
        mock_segment_service.add_control_point.assert_called_once_with(seg_index, pos)

    def test_on_add_control_point_requested_without_service(self, mock_bezier_manager):
        """Test adding control point without segment service"""
        from contour_editor.controllers.SegmentActionController import SegmentActionController

        pos = QPointF(50, 50)
        seg_index = 0
        segment = Mock()
        mock_bezier_manager.get_segments.return_value = [segment]
        mock_bezier_manager.find_segment_at.return_value = (0, 1)
        mock_bezier_manager.add_control_point.return_value = True

        controller = SegmentActionController(mock_bezier_manager)
        result = controller.on_add_control_point_requested(pos, seg_index)

        assert result is True
        mock_bezier_manager.add_control_point.assert_called_once()

    def test_on_add_control_point_requested_none_pos(self, mock_bezier_manager):
        """Test adding control point with None position"""
        from contour_editor.controllers.SegmentActionController import SegmentActionController

        controller = SegmentActionController(mock_bezier_manager)
        result = controller.on_add_control_point_requested(None, 0)

        assert result is None

    def test_on_add_control_point_requested_none_index(self, mock_bezier_manager):
        """Test adding control point with None index"""
        from contour_editor.controllers.SegmentActionController import SegmentActionController

        pos = QPointF(50, 50)
        controller = SegmentActionController(mock_bezier_manager)
        result = controller.on_add_control_point_requested(pos, None)

        assert result is None

    def test_on_add_anchor_point_requested_with_service(self, mock_bezier_manager, mock_segment_service):
        """Test adding anchor point with segment service"""
        from contour_editor.controllers.SegmentActionController import SegmentActionController

        pos = QPointF(50, 50)
        seg_index = 0
        mock_segment_service.add_anchor_point.return_value = True

        controller = SegmentActionController(mock_bezier_manager, mock_segment_service)
        result = controller.on_add_anchor_point_requested(pos, seg_index)

        assert result is True
        mock_segment_service.add_anchor_point.assert_called_once_with(seg_index, pos)

    def test_on_add_anchor_point_requested_without_service(self, mock_bezier_manager):
        """Test adding anchor point without segment service"""
        from contour_editor.controllers.SegmentActionController import SegmentActionController

        pos = QPointF(50, 50)
        seg_index = 0
        mock_bezier_manager.insert_anchor_point.return_value = True

        controller = SegmentActionController(mock_bezier_manager)
        result = controller.on_add_anchor_point_requested(pos, seg_index)

        assert result is True
        mock_bezier_manager.insert_anchor_point.assert_called_once_with(seg_index, pos)

    def test_on_add_anchor_point_requested_none_pos(self, mock_bezier_manager):
        """Test adding anchor point with None position"""
        from contour_editor.controllers.SegmentActionController import SegmentActionController

        controller = SegmentActionController(mock_bezier_manager)
        result = controller.on_add_anchor_point_requested(None, 0)

        assert result is None

    def test_on_add_anchor_point_requested_none_index(self, mock_bezier_manager):
        """Test adding anchor point with None index"""
        from contour_editor.controllers.SegmentActionController import SegmentActionController

        pos = QPointF(50, 50)
        controller = SegmentActionController(mock_bezier_manager)
        result = controller.on_add_anchor_point_requested(pos, None)

        assert result is None

    def test_on_disconnect_line_requested_with_service(self, mock_bezier_manager, mock_segment_service):
        """Test disconnect line with segment service"""
        from contour_editor.controllers.SegmentActionController import SegmentActionController

        pos = QPointF(50, 50)
        seg_index = 0
        mock_segment_service.disconnect_line.return_value = True

        controller = SegmentActionController(mock_bezier_manager, mock_segment_service)
        result = controller.on_disconnect_line_requested(pos, seg_index)

        assert result is True
        mock_segment_service.disconnect_line.assert_called_once_with(pos, seg_index)

    def test_on_disconnect_line_requested_without_service(self, mock_bezier_manager):
        """Test disconnect line without segment service"""
        from contour_editor.controllers.SegmentActionController import SegmentActionController

        pos = QPointF(50, 50)
        seg_index = 0
        mock_bezier_manager.find_segment_at.return_value = (0, 1)
        mock_bezier_manager.disconnect_line_segment.return_value = True

        controller = SegmentActionController(mock_bezier_manager)
        result = controller.on_disconnect_line_requested(pos, seg_index)

        assert result is True
        mock_bezier_manager.disconnect_line_segment.assert_called_once_with(0, 1)

    def test_on_disconnect_line_requested_no_segment_found(self, mock_bezier_manager):
        """Test disconnect line when no segment found"""
        from contour_editor.controllers.SegmentActionController import SegmentActionController

        pos = QPointF(50, 50)
        seg_index = 0
        mock_bezier_manager.find_segment_at.return_value = None

        controller = SegmentActionController(mock_bezier_manager)
        result = controller.on_disconnect_line_requested(pos, seg_index)

        assert result is None

    def test_on_disconnect_line_requested_none_pos(self, mock_bezier_manager):
        """Test disconnect line with None position"""
        from contour_editor.controllers.SegmentActionController import SegmentActionController

        controller = SegmentActionController(mock_bezier_manager)
        result = controller.on_disconnect_line_requested(None, 0)

        assert result is None

    def test_on_disconnect_line_requested_none_index(self, mock_bezier_manager):
        """Test disconnect line with None index"""
        from contour_editor.controllers.SegmentActionController import SegmentActionController

        pos = QPointF(50, 50)
        controller = SegmentActionController(mock_bezier_manager)
        result = controller.on_disconnect_line_requested(pos, None)

        assert result is None

    def test_on_delete_segment_requested(self, mock_bezier_manager):
        """Test deleting segment via request"""
        from contour_editor.controllers.SegmentActionController import SegmentActionController

        controller = SegmentActionController(mock_bezier_manager)
        controller.on_delete_segment_requested(0)

        mock_bezier_manager.delete_segment.assert_called_once_with(0)

    def test_on_delete_segment_requested_none_index(self, mock_bezier_manager):
        """Test delete segment request with None index"""
        from contour_editor.controllers.SegmentActionController import SegmentActionController

        controller = SegmentActionController(mock_bezier_manager)
        controller.on_delete_segment_requested(None)

        mock_bezier_manager.delete_segment.assert_not_called()


class TestViewportController:
    """Tests for ViewportController"""

    def test_initialization(self, mock_editor):
        """Test ViewportController initialization"""
        from contour_editor.controllers.viewport_controller import ViewportController

        controller = ViewportController(mock_editor)

        assert controller.editor is mock_editor
        assert controller.scale_factor == 1.0
        assert controller.translation == QPointF(0, 0)
        assert controller.is_zooming is False
        assert controller.image is None

    def test_zoom_in(self, mock_editor):
        """Test zoom in functionality"""
        from contour_editor.controllers.viewport_controller import ViewportController

        controller = ViewportController(mock_editor)
        initial_scale = controller.scale_factor

        controller.zoom_in()

        assert controller.scale_factor > initial_scale
        mock_editor.update.assert_called()

    def test_zoom_out(self, mock_editor):
        """Test zoom out functionality"""
        from contour_editor.controllers.viewport_controller import ViewportController

        controller = ViewportController(mock_editor)
        controller.scale_factor = 2.0
        initial_scale = controller.scale_factor

        controller.zoom_out()

        assert controller.scale_factor < initial_scale
        mock_editor.update.assert_called()

    def test_zoom_in_multiple_times(self, mock_editor):
        """Test multiple zoom in operations"""
        from contour_editor.controllers.viewport_controller import ViewportController

        controller = ViewportController(mock_editor)
        initial_scale = controller.scale_factor

        controller.zoom_in()
        first_scale = controller.scale_factor
        controller.zoom_in()
        second_scale = controller.scale_factor

        assert initial_scale < first_scale < second_scale

    def test_zoom_out_multiple_times(self, mock_editor):
        """Test multiple zoom out operations"""
        from contour_editor.controllers.viewport_controller import ViewportController

        controller = ViewportController(mock_editor)
        controller.scale_factor = 10.0
        first_scale = controller.scale_factor

        controller.zoom_out()
        second_scale = controller.scale_factor
        controller.zoom_out()
        third_scale = controller.scale_factor

        assert first_scale > second_scale > third_scale

    def test_reset_zoom_without_image(self, mock_editor):
        """Test reset zoom without image"""
        from contour_editor.controllers.viewport_controller import ViewportController

        controller = ViewportController(mock_editor)
        controller.scale_factor = 2.5
        controller.translation = QPointF(100, 100)

        controller.reset_zoom()

        assert controller.scale_factor == 1.0
        assert controller.translation == QPointF(0, 0)
        mock_editor.update.assert_called()

    def test_reset_zoom_with_image(self, mock_editor):
        """Test reset zoom with image"""
        from contour_editor.controllers.viewport_controller import ViewportController

        controller = ViewportController(mock_editor)
        image = QImage(1280, 720, QImage.Format.Format_RGB32)
        controller.image = image
        controller.scale_factor = 2.5

        controller.reset_zoom()

        assert controller.scale_factor == 1.0
        # Translation should center the image
        expected_x = (800 - 1280) / 2
        expected_y = (600 - 720) / 2
        assert controller.translation == QPointF(expected_x, expected_y)

    def test_toggle_zooming_on(self, mock_editor):
        """Test toggling zooming on"""
        from contour_editor.controllers.viewport_controller import ViewportController

        controller = ViewportController(mock_editor)
        assert controller.is_zooming is False

        controller.toggle_zooming()

        assert controller.is_zooming is True
        mock_editor.grabGesture.assert_called_once()

    def test_toggle_zooming_off(self, mock_editor):
        """Test toggling zooming off"""
        from contour_editor.controllers.viewport_controller import ViewportController

        controller = ViewportController(mock_editor)
        controller.is_zooming = True

        controller.toggle_zooming()

        assert controller.is_zooming is False
        mock_editor.ungrabGesture.assert_called_once()

    def test_reset_zoom_flag(self, mock_editor):
        """Test resetting zoom flag"""
        from contour_editor.controllers.viewport_controller import ViewportController

        controller = ViewportController(mock_editor)
        controller.is_zooming = True

        controller.reset_zoom_flag()

        assert controller.is_zooming is False

    def test_load_image_from_path(self, mock_editor):
        """Test loading image from file path"""
        from contour_editor.controllers.viewport_controller import ViewportController

        controller = ViewportController(mock_editor)

        # Create a temporary valid image
        with patch('contour_editor.controllers.viewport_controller.QImage') as mock_qimage:
            mock_image = Mock()
            mock_image.isNull.return_value = False
            mock_qimage.return_value = mock_image

            result = controller.load_image("/path/to/image.png")

            assert controller.image is mock_image
            assert result is mock_image

    def test_load_image_null_path(self, mock_editor):
        """Test loading image with null path"""
        from contour_editor.controllers.viewport_controller import ViewportController

        controller = ViewportController(mock_editor)

        with patch('contour_editor.controllers.viewport_controller.QImage') as mock_qimage:
            mock_image = Mock()
            mock_qimage.return_value = mock_image

            result = controller.load_image(None)

            assert controller.image is mock_image

    def test_load_image_invalid_path(self, mock_editor):
        """Test loading image with invalid path"""
        from contour_editor.controllers.viewport_controller import ViewportController

        controller = ViewportController(mock_editor)

        with patch('contour_editor.controllers.viewport_controller.QImage') as mock_qimage:
            mock_image_fail = Mock()
            mock_image_fail.isNull.return_value = True
            mock_image_default = Mock()
            mock_qimage.side_effect = [mock_image_fail, mock_image_default]

            result = controller.load_image("/invalid/path.png")

            assert controller.image is mock_image_default

    def test_set_image_from_numpy_rgb(self, mock_editor):
        """Test setting image from RGB numpy array"""
        from contour_editor.controllers.viewport_controller import ViewportController

        controller = ViewportController(mock_editor)

        # Create RGB image array
        image_array = np.zeros((100, 100, 3), dtype=np.uint8)

        # Test that set_image can handle RGB arrays
        # We just verify it doesn't crash and processes the array
        try:
            controller.set_image(image_array)
            # If no exception, the method handled it
            assert True
        except Exception as e:
            pytest.fail(f"set_image failed with RGB array: {e}")

    def test_set_image_from_numpy_rgba(self, mock_editor):
        """Test setting image from RGBA numpy array"""
        from contour_editor.controllers.viewport_controller import ViewportController

        controller = ViewportController(mock_editor)

        # Create RGBA image array
        image_array = np.zeros((100, 100, 4), dtype=np.uint8)

        # Test that set_image can handle RGBA arrays
        # We just verify it doesn't crash and processes the array
        try:
            controller.set_image(image_array)
            # If no exception, the method handled it
            assert True
        except Exception as e:
            pytest.fail(f"set_image failed with RGBA array: {e}")

    def test_set_image_none(self, mock_editor):
        """Test setting image to None"""
        from contour_editor.controllers.viewport_controller import ViewportController

        controller = ViewportController(mock_editor)

        controller.set_image(None)

        assert controller.image is None

    def test_update_image_from_qimage(self, mock_editor):
        """Test updating image from QImage"""
        from contour_editor.controllers.viewport_controller import ViewportController

        controller = ViewportController(mock_editor)
        image = QImage(100, 100, QImage.Format.Format_RGB32)

        controller.update_image(image)

        assert controller.image is image
        mock_editor.update.assert_called()

    def test_update_image_from_path(self, mock_editor):
        """Test updating image from file path"""
        from contour_editor.controllers.viewport_controller import ViewportController

        controller = ViewportController(mock_editor)

        with patch('contour_editor.controllers.viewport_controller.QImage') as mock_qimage:
            mock_image = Mock()
            mock_image.isNull.return_value = False
            mock_qimage.return_value = mock_image

            controller.update_image("/path/to/image.png")

            assert controller.image is mock_image
            mock_editor.update.assert_called()

    def test_update_image_invalid_path(self, mock_editor):
        """Test updating image with invalid path"""
        from contour_editor.controllers.viewport_controller import ViewportController

        controller = ViewportController(mock_editor)
        controller.image = QImage(100, 100, QImage.Format.Format_RGB32)
        original_image = controller.image

        with patch('contour_editor.controllers.viewport_controller.QImage') as mock_qimage:
            mock_image = Mock()
            mock_image.isNull.return_value = True
            mock_qimage.return_value = mock_image

            controller.update_image("/invalid/path.png")

            # Image should not change
            assert controller.image is original_image

    def test_update_image_invalid_type(self, mock_editor):
        """Test updating image with invalid type"""
        from contour_editor.controllers.viewport_controller import ViewportController

        controller = ViewportController(mock_editor)
        original_image = controller.image

        # Try to update with invalid type
        controller.update_image(12345)

        # Image should not change
        assert controller.image is original_image

    def test_is_within_image_true(self, mock_editor):
        """Test checking if point is within image bounds"""
        from contour_editor.controllers.viewport_controller import ViewportController

        controller = ViewportController(mock_editor)
        controller.image = QImage(1280, 720, QImage.Format.Format_RGB32)
        controller.scale_factor = 1.0
        controller.translation = QPointF(0, 0)

        with patch('contour_editor.controllers.viewport_controller.map_to_image_space') as mock_map:
            mock_map.return_value = QPointF(100, 100)

            result = controller.is_within_image(QPointF(100, 100))

            assert result is True

    def test_is_within_image_false_x(self, mock_editor):
        """Test checking if point is outside image bounds (x)"""
        from contour_editor.controllers.viewport_controller import ViewportController

        controller = ViewportController(mock_editor)
        controller.image = QImage(1280, 720, QImage.Format.Format_RGB32)
        controller.scale_factor = 1.0
        controller.translation = QPointF(0, 0)

        with patch('contour_editor.controllers.viewport_controller.map_to_image_space') as mock_map:
            mock_map.return_value = QPointF(1500, 100)

            result = controller.is_within_image(QPointF(1500, 100))

            assert result is False

    def test_is_within_image_false_y(self, mock_editor):
        """Test checking if point is outside image bounds (y)"""
        from contour_editor.controllers.viewport_controller import ViewportController

        controller = ViewportController(mock_editor)
        controller.image = QImage(1280, 720, QImage.Format.Format_RGB32)
        controller.scale_factor = 1.0
        controller.translation = QPointF(0, 0)

        with patch('contour_editor.controllers.viewport_controller.map_to_image_space') as mock_map:
            mock_map.return_value = QPointF(100, 800)

            result = controller.is_within_image(QPointF(100, 800))

            assert result is False


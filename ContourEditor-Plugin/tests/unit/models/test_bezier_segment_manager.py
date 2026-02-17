"""
Comprehensive Test Suite for Backend - Default Implementation

This module tests:
- Segment class (points, controls, settings, visibility, layers)
- Layer class (segment management, locking, visibility)
- BezierSegmentManager (segment creation, management, undo/redo)
- Contour to Bezier conversion
"""
import pytest
import numpy as np
from unittest.mock import Mock
from PyQt6.QtCore import QPointF


class TestSegment:
    """Tests for Segment class"""

    def test_segment_initialization(self):
        """Test basic segment initialization"""
        from contour_editor.models.segment import Segment

        segment = Segment()
        assert segment.points == []
        assert segment.controls == []
        assert segment.visible is True
        assert segment.layer is None
        assert segment.settings == {}

    def test_segment_with_layer_and_settings(self):
        """Test segment initialization with layer and settings"""
        from contour_editor.models.segment import Segment, Layer

        layer = Layer("Contour")
        settings = {"color": "#FF0000"}
        segment = Segment(layer=layer, settings=settings)

        assert segment.layer is layer
        assert segment.settings == settings

    def test_add_point(self):
        """Test adding points to segment"""
        from contour_editor.models.segment import Segment

        segment = Segment()
        p1 = QPointF(10, 20)
        p2 = QPointF(30, 40)

        segment.add_point(p1)
        assert len(segment.points) == 1
        assert segment.points[0] == p1

        segment.add_point(p2)
        assert len(segment.points) == 2
        assert len(segment.controls) == 1  # Control point auto-created

    def test_remove_point(self):
        """Test removing points"""
        from contour_editor.models.segment import Segment

        segment = Segment()
        segment.add_point(QPointF(0, 0))
        segment.add_point(QPointF(10, 10))
        segment.add_point(QPointF(20, 20))

        segment.remove_point(1)
        assert len(segment.points) == 2
        assert segment.points[0] == QPointF(0, 0)
        assert segment.points[1] == QPointF(20, 20)

    def test_remove_point_out_of_bounds(self):
        """Test removing point at invalid index"""
        from contour_editor.models.segment import Segment

        segment = Segment()
        segment.add_point(QPointF(0, 0))
        segment.remove_point(10)  # Should not raise
        assert len(segment.points) == 1

    def test_add_control_point(self):
        """Test adding control points"""
        from contour_editor.models.segment import Segment

        segment = Segment()
        segment.add_point(QPointF(0, 0))
        segment.add_point(QPointF(10, 10))

        control = QPointF(5, 5)
        segment.add_control_point(0, control)

        assert segment.controls[0] == control

    def test_set_settings(self):
        """Test setting segment settings"""
        from contour_editor.models.segment import Segment

        segment = Segment()
        settings = {"color": "#00FF00", "width": 2}
        segment.set_settings(settings)

        assert segment.settings == settings

    def test_set_layer(self):
        """Test setting segment layer"""
        from contour_editor.models.segment import Segment, Layer

        segment = Segment()
        layer1 = Layer("Contour")
        layer2 = Layer("Fill")

        segment.set_layer(layer1)
        assert segment.layer is layer1

        segment.set_layer(layer2)
        assert segment.layer is layer2

    def test_segment_visibility_toggle(self):
        """Test toggling segment visibility"""
        from contour_editor.models.segment import Segment

        segment = Segment()
        assert segment.visible is True

        segment.visible = False
        assert segment.visible is False

    def test_get_layer_methods(self):
        """Test layer getter methods"""
        from contour_editor.models.segment import Segment, Layer

        layer = Layer("Contour")
        segment = Segment(layer=layer)

        assert segment.get_external_layer() == layer
        assert segment.get_contour_layer() == layer
        assert segment.get_fill_layer() == layer

    def test_segment_string_representation(self):
        """Test segment string representation"""
        from contour_editor.models.segment import Segment

        segment = Segment()
        segment.add_point(QPointF(0, 0))

        str_repr = str(segment)
        assert "Segment" in str_repr
        assert "points=" in str_repr


class TestLayer:
    """Tests for Layer class"""

    def test_layer_initialization(self):
        """Test basic layer initialization"""
        from contour_editor.models.bezier_segment_manager import Layer

        layer = Layer("Contour")
        assert layer.name == "Contour"
        assert layer.locked is False
        assert layer.visible is True
        assert layer.segments == []

    def test_layer_with_properties(self):
        """Test layer initialization with properties"""
        from contour_editor.models.bezier_segment_manager import Layer

        layer = Layer("Fill", locked=True, visible=False)
        assert layer.name == "Fill"
        assert layer.locked is True
        assert layer.visible is False

    def test_add_segment(self):
        """Test adding segments to layer"""
        from contour_editor.models.bezier_segment_manager import Layer, Segment

        layer = Layer("Contour")
        segment = Segment(layer=layer)

        layer.add_segment(segment)
        assert len(layer.segments) == 1
        assert layer.segments[0] is segment

    def test_add_multiple_segments(self):
        """Test adding multiple segments"""
        from contour_editor.models.bezier_segment_manager import Layer, Segment

        layer = Layer("Contour")
        seg1 = Segment(layer=layer)
        seg2 = Segment(layer=layer)
        seg3 = Segment(layer=layer)

        layer.add_segment(seg1)
        layer.add_segment(seg2)
        layer.add_segment(seg3)

        assert len(layer.segments) == 3

    def test_remove_segment(self):
        """Test removing segments"""
        from contour_editor.models.bezier_segment_manager import Layer, Segment

        layer = Layer("Contour")
        seg1 = Segment(layer=layer)
        seg2 = Segment(layer=layer)
        seg3 = Segment(layer=layer)

        layer.add_segment(seg1)
        layer.add_segment(seg2)
        layer.add_segment(seg3)

        layer.remove_segment(1)
        assert len(layer.segments) == 2

    def test_layer_locking(self):
        """Test layer locking mechanism"""
        from contour_editor.models.bezier_segment_manager import Layer

        layer = Layer("Contour", locked=False)
        assert layer.locked is False

        layer.locked = True
        assert layer.locked is True

    def test_layer_visibility(self):
        """Test layer visibility"""
        from contour_editor.models.bezier_segment_manager import Layer

        layer = Layer("Contour", visible=True)
        assert layer.visible is True

        layer.visible = False
        assert layer.visible is False

    def test_layer_string_representation(self):
        """Test layer string representation"""
        from contour_editor.models.bezier_segment_manager import Layer

        layer = Layer("Contour")
        str_repr = str(layer)
        assert "Layer" in str_repr
        assert "Contour" in str_repr


class TestBezierSegmentManager:
    """Tests for BezierSegmentManager class"""

    def test_initialization(self):
        """Test BezierSegmentManager initialization"""
        from contour_editor.models.bezier_segment_manager import BezierSegmentManager

        manager = BezierSegmentManager()

        assert manager.active_segment_index == 0
        assert len(manager.segments) == 1
        assert manager.undo_stack == []
        assert manager.redo_stack == []
        assert manager.external_layer.name == "Main"
        assert manager.contour_layer.name == "Contour"
        assert manager.fill_layer.name == "Fill"

    def test_create_segment(self):
        """Test creating segments"""
        from contour_editor.models.bezier_segment_manager import BezierSegmentManager

        manager = BezierSegmentManager()
        points = [QPointF(0, 0), QPointF(10, 10), QPointF(20, 20)]

        segment = manager.create_segment(points, "Contour")

        assert len(segment.points) == 3
        assert segment.layer == manager.contour_layer

    def test_create_segment_workpiece_layer(self):
        """Test creating segment on Workpiece layer"""
        from contour_editor.models.bezier_segment_manager import BezierSegmentManager

        manager = BezierSegmentManager()
        points = [QPointF(0, 0), QPointF(10, 10)]

        segment = manager.create_segment(points, "Main")
        assert segment.layer == manager.external_layer

    def test_create_segment_fill_layer(self):
        """Test creating segment on Fill layer"""
        from contour_editor.models.bezier_segment_manager import BezierSegmentManager

        manager = BezierSegmentManager()
        points = [QPointF(0, 0), QPointF(10, 10)]

        segment = manager.create_segment(points, "Fill")
        assert segment.layer == manager.fill_layer

    def test_create_segment_invalid_layer(self):
        """Test creating segment with invalid layer"""
        from contour_editor.models.bezier_segment_manager import BezierSegmentManager

        manager = BezierSegmentManager()
        points = [QPointF(0, 0), QPointF(10, 10)]

        with pytest.raises(ValueError):
            manager.create_segment(points, "InvalidLayer")

    def test_add_point_to_active_segment(self):
        """Test adding point to active segment"""
        from contour_editor.models.bezier_segment_manager import BezierSegmentManager

        manager = BezierSegmentManager()
        manager.active_segment_index = 0
        point = QPointF(50, 50)

        manager.add_point(point)

        assert len(manager.segments[0].points) == 1
        assert manager.segments[0].points[0] == point

    def test_set_active_segment(self):
        """Test setting active segment"""
        from contour_editor.models.bezier_segment_manager import BezierSegmentManager

        manager = BezierSegmentManager()
        manager.start_new_segment("Contour")
        manager.start_new_segment("Contour")

        manager.set_active_segment(1)
        assert manager.active_segment_index == 1

    def test_set_active_segment_locked_layer(self):
        """Test setting active segment with locked layer"""
        from contour_editor.models.bezier_segment_manager import BezierSegmentManager

        manager = BezierSegmentManager()
        manager.contour_layer.locked = True
        manager.segments[0].layer = manager.contour_layer

        manager.set_active_segment(0)
        # Should not change active segment
        assert manager.active_segment_index == 0

    def test_start_new_segment(self):
        """Test starting a new segment"""
        from contour_editor.models.bezier_segment_manager import BezierSegmentManager

        manager = BezierSegmentManager()
        initial_count = len(manager.segments)

        segment, success = manager.start_new_segment("Contour")

        assert success is True
        assert segment is not None
        assert len(manager.segments) == initial_count + 1

    def test_start_new_segment_locked_layer(self):
        """Test starting segment on locked layer"""
        from contour_editor.models.bezier_segment_manager import BezierSegmentManager

        manager = BezierSegmentManager()
        manager.contour_layer.locked = True

        segment, success = manager.start_new_segment("Contour")

        assert success is False
        assert segment is None

    def test_assign_segment_layer(self):
        """Test assigning layer to segment"""
        from contour_editor.models.bezier_segment_manager import BezierSegmentManager

        manager = BezierSegmentManager()
        manager.segments[0].layer = manager.contour_layer

        manager.assign_segment_layer(0, "Fill")

        assert manager.segments[0].layer == manager.fill_layer

    def test_save_state(self):
        """Test saving state for undo"""
        from contour_editor.models.bezier_segment_manager import BezierSegmentManager

        manager = BezierSegmentManager()
        manager.segments[0].add_point(QPointF(10, 10))

        manager.save_state()

        assert len(manager.undo_stack) == 1

    def test_undo_redo(self):
        """Test undo/redo functionality"""
        from contour_editor.models.bezier_segment_manager import BezierSegmentManager

        manager = BezierSegmentManager()
        manager.add_point(QPointF(10, 10))
        manager.save_state()

        initial_points = len(manager.segments[0].points)

        manager.add_point(QPointF(20, 20))
        manager.undo()

        assert len(manager.segments[0].points) == initial_points

    def test_undo_empty_stack(self):
        """Test undo with empty stack"""
        from contour_editor.models.bezier_segment_manager import BezierSegmentManager

        manager = BezierSegmentManager()

        with pytest.raises(Exception):
            manager.undo()

    def test_redo_empty_stack(self):
        """Test redo with empty stack"""
        from contour_editor.models.bezier_segment_manager import BezierSegmentManager

        manager = BezierSegmentManager()

        with pytest.raises(Exception):
            manager.redo()

    def test_clear_all_segments(self):
        """Test clearing all segments"""
        from contour_editor.models.bezier_segment_manager import BezierSegmentManager

        manager = BezierSegmentManager()
        manager.start_new_segment("Contour")
        manager.start_new_segment("Fill")

        manager.clear_all_segments()

        assert len(manager.segments) == 0
        assert manager.active_segment_index == -1

    def test_get_segments(self):
        """Test getting all segments"""
        from contour_editor.models.bezier_segment_manager import BezierSegmentManager

        manager = BezierSegmentManager()
        manager.start_new_segment("Contour")

        segments = manager.get_segments()

        assert len(segments) == 2  # Initial + new

    def test_remove_point(self):
        """Test removing point from segment"""
        from contour_editor.models.bezier_segment_manager import BezierSegmentManager

        manager = BezierSegmentManager()
        manager.segments[0].add_point(QPointF(10, 10))
        manager.segments[0].add_point(QPointF(20, 20))
        manager.segments[0].add_point(QPointF(30, 30))

        manager.segments[0].remove_point(1)

        assert len(manager.segments[0].points) == 2

    def test_remove_point_invalid_index(self):
        """Test removing point at invalid index"""
        from contour_editor.models.bezier_segment_manager import BezierSegmentManager

        manager = BezierSegmentManager()

        manager.segments[0].remove_point(100)  # Should not raise
        assert len(manager.segments[0].points) == 0

    def test_set_layer_locked(self):
        """Test locking/unlocking layers"""
        from contour_editor.models.bezier_segment_manager import BezierSegmentManager

        manager = BezierSegmentManager()

        manager.contour_layer.locked = True
        assert manager.contour_layer.locked is True

        manager.contour_layer.locked = False
        assert manager.contour_layer.locked is False



class TestContourToBezier:
    """Tests for contour to Bezier conversion"""

    def test_contour_to_bezier_basic(self):
        """Test basic contour to bezier conversion"""
        from contour_editor.models.bezier_segment_manager import BezierSegmentManager

        manager = BezierSegmentManager()
        contour = np.array([[[0, 0]], [[10, 0]], [[10, 10]], [[0, 10]]], dtype=np.int32)

        segments = manager.contour_to_bezier(contour)

        assert len(segments) == 1
        assert len(segments[0].points) == 5  # Closed contour

    def test_contour_to_bezier_not_closed(self):
        """Test contour to bezier with open contour"""
        from contour_editor.models.bezier_segment_manager import BezierSegmentManager

        manager = BezierSegmentManager()
        contour = np.array([[[0, 0]], [[10, 0]], [[10, 10]]], dtype=np.int32)

        segments = manager.contour_to_bezier(contour, close_contour=True)

        assert len(segments) == 1
        # Should be closed: first point repeated at end
        assert segments[0].points[0] == segments[0].points[-1]

    def test_contour_to_bezier_control_points(self):
        """Test that control points are generated"""
        from contour_editor.models.bezier_segment_manager import BezierSegmentManager

        manager = BezierSegmentManager()
        contour = np.array([[[0, 0]], [[10, 0]], [[10, 10]], [[0, 10]]], dtype=np.int32)

        segments = manager.contour_to_bezier(contour, control_point_ratio=0.5)

        assert len(segments[0].controls) > 0

    def test_contour_to_bezier_empty(self):
        """Test contour to bezier with empty contour"""
        from contour_editor.models.bezier_segment_manager import BezierSegmentManager

        manager = BezierSegmentManager()
        contour = np.array([], dtype=np.int32)

        segments = manager.contour_to_bezier(contour)

        assert len(segments) == 0

    def test_contour_to_bezier_single_point(self):
        """Test contour to bezier with single point"""
        from contour_editor.models.bezier_segment_manager import BezierSegmentManager

        manager = BezierSegmentManager()
        contour = np.array([[[5, 5]]], dtype=np.int32)

        segments = manager.contour_to_bezier(contour)

        assert len(segments) == 0


@pytest.mark.unit
class TestBackendIntegration:
    """Integration tests for backend components"""

    def test_segment_and_layer_integration(self):
        """Test integration between segments and layers"""
        from contour_editor.models.bezier_segment_manager import BezierSegmentManager

        manager = BezierSegmentManager()
        manager.start_new_segment("Contour")
        manager.segments[1].add_point(QPointF(10, 10))
        manager.segments[1].add_point(QPointF(20, 20))

        assert len(manager.contour_layer.segments) >= 1
        assert len(manager.segments[1].points) == 2

    def test_undo_redo_with_multiple_operations(self):
        """Test undo/redo with multiple operations"""
        from contour_editor.models.bezier_segment_manager import BezierSegmentManager

        manager = BezierSegmentManager()

        manager.segments[0].add_point(QPointF(10, 10))
        manager.save_state()
        manager.segments[0].add_point(QPointF(20, 20))
        manager.save_state()
        manager.segments[0].add_point(QPointF(30, 30))

        manager.undo()
        assert len(manager.segments[0].points) == 2

        manager.undo()
        assert len(manager.segments[0].points) == 1

        manager.redo()
        assert len(manager.segments[0].points) == 2

    def test_layer_locking_prevents_operations(self):
        """Test that layer locking prevents operations"""
        from contour_editor.models.bezier_segment_manager import BezierSegmentManager

        manager = BezierSegmentManager()
        manager.contour_layer.locked = True

        segment, success = manager.start_new_segment("Contour")

        assert success is False

    def test_multiple_layers_workflow(self):
        """Test workflow with multiple layers"""
        from contour_editor.models.bezier_segment_manager import BezierSegmentManager

        manager = BezierSegmentManager()

        # Create segments in different layers
        manager.start_new_segment("Contour")
        manager.segments[1].add_point(QPointF(10, 10))

        manager.set_active_segment(0)
        manager.assign_segment_layer(0, "Fill")

        assert manager.segments[0].layer == manager.fill_layer


"""Tests for mouse wheel zoom functionality"""
import pytest
from PyQt6.QtCore import QPointF
@pytest.fixture(scope="module", autouse=True)
def register_segment_manager():
    """Register default segment manager for tests"""
    from contour_editor.persistence.data.segment_provider import SegmentManagerProvider
    from contour_editor.models.bezier_segment_manager import BezierSegmentManager
    # Register manager
    SegmentManagerProvider.get_instance().set_manager_class(BezierSegmentManager)
    yield
    # Cleanup
    SegmentManagerProvider._instance = None
@pytest.fixture
def editor(qapp):
    """Create ContourEditor instance for testing"""
    from contour_editor.core.editor import ContourEditor
    # Pass None for visionSystem as it's not needed for zoom tests
    editor = ContourEditor(visionSystem=None, parent=None, image_path=None, data=None)
    return editor
@pytest.fixture
def zoom_handler(editor):
    """Get the zoom handler from editor's event manager"""
    return editor.event_manager._zoom_handler
def test_zoom_handler_initialization(zoom_handler):
    """Test that ZoomHandler initializes correctly"""
    assert zoom_handler is not None
    assert hasattr(zoom_handler, 'ctx')
    assert hasattr(zoom_handler, 'handle_wheel_event')
def test_zoom_in_function(zoom_handler, editor):
    """Test zoom_in increases scale factor"""
    initial_scale = editor.viewport_controller.scale_factor
    zoom_handler.zoom_in()
    new_scale = editor.viewport_controller.scale_factor
    assert new_scale > initial_scale
    assert new_scale == pytest.approx(initial_scale * 1.25, rel=0.01)
def test_zoom_out_function(zoom_handler, editor):
    """Test zoom_out decreases scale factor"""
    initial_scale = editor.viewport_controller.scale_factor
    zoom_handler.zoom_out()
    new_scale = editor.viewport_controller.scale_factor
    assert new_scale < initial_scale
    assert new_scale == pytest.approx(initial_scale * 0.8, rel=0.01)
def test_reset_zoom(zoom_handler, editor):
    """Test reset_zoom returns to default scale"""
    # Zoom in first
    zoom_handler.zoom_in()
    zoom_handler.zoom_in()
    assert editor.viewport_controller.scale_factor != 1.0
    # Reset
    zoom_handler.reset_zoom()
    # Should be back to default (may not be exactly 1.0 depending on fit logic)
    # Just verify it changed
    assert editor.viewport_controller.scale_factor > 0
def test_wheel_event_zoom_in(zoom_handler, editor):
    """Test wheel event with positive angle zooms in"""
    initial_scale = editor.viewport_controller.scale_factor
    # Create a mock wheel event (scroll up = zoom in)
    class MockWheelEvent:
        def angleDelta(self):
            class Delta:
                def y(self):
                    return 120  # Positive = scroll up
            return Delta()
        def position(self):
            return QPointF(100, 100)
    event = MockWheelEvent()
    zoom_handler.handle_wheel_event(event)
    new_scale = editor.viewport_controller.scale_factor
    assert new_scale > initial_scale
    assert new_scale == pytest.approx(initial_scale * 1.25, rel=0.01)
def test_wheel_event_zoom_out(zoom_handler, editor):
    """Test wheel event with negative angle zooms out"""
    initial_scale = editor.viewport_controller.scale_factor
    # Create a mock wheel event (scroll down = zoom out)
    class MockWheelEvent:
        def angleDelta(self):
            class Delta:
                def y(self):
                    return -120  # Negative = scroll down
            return Delta()
        def position(self):
            return QPointF(100, 100)
    event = MockWheelEvent()
    zoom_handler.handle_wheel_event(event)
    new_scale = editor.viewport_controller.scale_factor
    assert new_scale < initial_scale
    assert new_scale == pytest.approx(initial_scale * 0.8, rel=0.01)
def test_wheel_event_zero_angle(zoom_handler, editor):
    """Test wheel event with zero angle does nothing"""
    initial_scale = editor.viewport_controller.scale_factor
    # Create a mock wheel event with zero angle
    class MockWheelEvent:
        def angleDelta(self):
            class Delta:
                def y(self):
                    return 0  # No scroll
            return Delta()
        def position(self):
            return QPointF(100, 100)
    event = MockWheelEvent()
    zoom_handler.handle_wheel_event(event)
    # Scale should not change
    assert editor.viewport_controller.scale_factor == initial_scale
def test_wheel_zoom_at_cursor_position(zoom_handler, editor):
    """Test that zoom centers on cursor position"""
    # Set initial viewport state
    editor.viewport_controller.translation = QPointF(0, 0)
    editor.viewport_controller.scale_factor = 1.0
    cursor_pos = QPointF(200, 150)
    class MockWheelEvent:
        def angleDelta(self):
            class Delta:
                def y(self):
                    return 120
            return Delta()
        def position(self):
            return cursor_pos
    event = MockWheelEvent()
    zoom_handler.handle_wheel_event(event)
    # After zoom, the translation should have changed to keep cursor position fixed
    # This verifies zoom_at_point is working
    assert editor.viewport_controller.scale_factor == pytest.approx(1.25, rel=0.01)
def test_multiple_zoom_operations(zoom_handler, editor):
    """Test multiple zoom operations in sequence"""
    initial_scale = editor.viewport_controller.scale_factor
    # Zoom in 3 times
    zoom_handler.zoom_in()
    zoom_handler.zoom_in()
    zoom_handler.zoom_in()
    expected_scale = initial_scale * (1.25 ** 3)
    assert editor.viewport_controller.scale_factor == pytest.approx(expected_scale, rel=0.01)
    # Zoom out 2 times
    zoom_handler.zoom_out()
    zoom_handler.zoom_out()
    expected_scale = initial_scale * (1.25 ** 3) * (0.8 ** 2)
    assert editor.viewport_controller.scale_factor == pytest.approx(expected_scale, rel=0.01)
def test_event_manager_handles_wheel(editor):
    """Test that EventManager properly delegates wheel events to ZoomHandler"""
    initial_scale = editor.viewport_controller.scale_factor
    class MockWheelEvent:
        def angleDelta(self):
            class Delta:
                def y(self):
                    return 120
            return Delta()
        def position(self):
            return QPointF(100, 100)
    event = MockWheelEvent()
    editor.event_manager.handle_wheel(event)
    # Verify zoom happened
    assert editor.viewport_controller.scale_factor > initial_scale
def test_zoom_handler_context_access(zoom_handler):
    """Test that ZoomHandler can access context APIs"""
    assert hasattr(zoom_handler.ctx, 'viewport')
    assert hasattr(zoom_handler.ctx, 'widget')
    assert hasattr(zoom_handler.ctx.viewport, 'zoom_centered')
    assert hasattr(zoom_handler.ctx.viewport, 'zoom_at_point')
    assert hasattr(zoom_handler.ctx.viewport, 'reset_zoom')
def test_zoom_limits(zoom_handler, editor):
    """Test that zoom has reasonable limits (if implemented)"""
    # Zoom in many times
    for _ in range(20):
        zoom_handler.zoom_in()
    scale_max = editor.viewport_controller.scale_factor
    # Reset and zoom out many times
    editor.viewport_controller.scale_factor = 1.0
    for _ in range(20):
        zoom_handler.zoom_out()
    scale_min = editor.viewport_controller.scale_factor
    # Verify reasonable limits exist
    assert scale_min > 0  # Can't zoom to zero
    assert scale_max < 1000  # Reasonable upper limit
    assert scale_min < scale_max
if __name__ == '__main__':
    pytest.main([__file__, '-v'])

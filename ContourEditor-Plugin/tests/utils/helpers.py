"""
Test helper functions and utilities.
This module provides reusable helper functions for test setup,
assertions, and data creation.
"""
import numpy as np
from unittest.mock import Mock
from PyQt6.QtCore import QPointF
# ===== Mock Creation Helpers =====
def create_mock_segment(index=0, layer_name="Contour", visible=True, num_points=4):
    """
    Create a mock segment with specified properties.
    Args:
        index: Segment index
        layer_name: Name of the layer
        visible: Visibility status
        num_points: Number of points in segment
    Returns:
        Mock segment object
    """
    segment = Mock()
    segment.index = index
    segment.points = [QPointF(i*10, i*10) for i in range(num_points)]
    segment.controls = []
    segment.visible = visible
    segment.layer = create_mock_layer(layer_name, visible=True, locked=False)
    segment.set_settings = Mock()
    segment.get_settings = Mock(return_value={})
    return segment
def create_mock_layer(name, visible=True, locked=False):
    """
    Create a mock layer with specified properties.
    Args:
        name: Layer name
        visible: Visibility status
        locked: Lock status
    Returns:
        Mock layer object
    """
    layer = Mock()
    layer.name = name
    layer.visible = visible
    layer.locked = locked
    return layer
def create_mock_manager_with_segments(num_segments=3, layer_name="Contour"):
    """
    Create a mock manager with pre-populated segments.
    Args:
        num_segments: Number of segments to create
        layer_name: Layer name for segments
    Returns:
        Mock manager with segments
    """
    manager = Mock()
    manager.segments = [
        create_mock_segment(i, layer_name) 
        for i in range(num_segments)
    ]
    manager.active_segment_index = 0
    manager.get_segments = Mock(return_value=manager.segments)
    manager.create_segment = Mock()
    manager.set_segment_visibility = Mock()
    manager.set_active_segment = Mock()
    # Add layer mocks
    manager.external_layer = create_mock_layer("Workpiece")
    manager.contour_layer = create_mock_layer("Contour")
    manager.fill_layer = create_mock_layer("Fill")
    manager.getLayer = Mock(side_effect=lambda name: {
        "Workpiece": manager.external_layer,
        "Contour": manager.contour_layer,
        "Fill": manager.fill_layer
    }.get(name))
    manager.isLayerLocked = Mock(return_value=False)
    return manager
# ===== Assertion Helpers =====
def assert_segments_equal(seg1, seg2, check_visibility=True, check_layer=True):
    """
    Assert that two segments are equal.
    Args:
        seg1: First segment
        seg2: Second segment
        check_visibility: Whether to check visibility
        check_layer: Whether to check layer
    """
    assert len(seg1.points) == len(seg2.points), \
        f"Point count mismatch: {len(seg1.points)} vs {len(seg2.points)}"
    for i, (p1, p2) in enumerate(zip(seg1.points, seg2.points)):
        assert_points_equal(p1, p2, f"Point {i}")
    if check_visibility:
        assert seg1.visible == seg2.visible, \
            f"Visibility mismatch: {seg1.visible} vs {seg2.visible}"
    if check_layer:
        assert seg1.layer.name == seg2.layer.name, \
            f"Layer mismatch: {seg1.layer.name} vs {seg2.layer.name}"
def assert_points_equal(p1, p2, label="Point"):
    """
    Assert that two QPointF objects are equal.
    Args:
        p1: First point
        p2: Second point
        label: Label for error messages
    """
    assert abs(p1.x() - p2.x()) < 0.001, \
        f"{label} X mismatch: {p1.x()} vs {p2.x()}"
    assert abs(p1.y() - p2.y()) < 0.001, \
        f"{label} Y mismatch: {p1.y()} vs {p2.y()}"
def assert_layer_properties(layer, expected_name=None, expected_visible=None, expected_locked=None):
    """
    Assert layer properties.
    Args:
        layer: Layer to check
        expected_name: Expected layer name (None to skip)
        expected_visible: Expected visibility (None to skip)
        expected_locked: Expected lock status (None to skip)
    """
    if expected_name is not None:
        assert layer.name == expected_name, \
            f"Layer name mismatch: expected {expected_name}, got {layer.name}"
    if expected_visible is not None:
        assert layer.visible == expected_visible, \
            f"Layer visibility mismatch: expected {expected_visible}, got {layer.visible}"
    if expected_locked is not None:
        assert layer.locked == expected_locked, \
            f"Layer lock status mismatch: expected {expected_locked}, got {layer.locked}"
def compare_numpy_arrays(arr1, arr2, tolerance=1e-6):
    """
    Compare two numpy arrays with tolerance.
    Args:
        arr1: First array
        arr2: Second array
        tolerance: Comparison tolerance
    Returns:
        True if arrays are equal within tolerance
    """
    if arr1 is None and arr2 is None:
        return True
    if arr1 is None or arr2 is None:
        return False
    if arr1.shape != arr2.shape:
        return False
    return np.allclose(arr1, arr2, atol=tolerance)
# ===== Test Data Creation =====
def create_test_contour(shape="square", size=100, offset=(0, 0)):
    """
    Create test contour data.
    Args:
        shape: Shape type ("square", "triangle", "hexagon")
        size: Size of the shape
        offset: (x, y) offset tuple
    Returns:
        Numpy array of contour points
    """
    x_off, y_off = offset
    if shape == "square":
        return np.array([
            [x_off, y_off],
            [x_off + size, y_off],
            [x_off + size, y_off + size],
            [x_off, y_off + size],
            [x_off, y_off]  # Close the contour
        ], dtype=np.float32)
    elif shape == "triangle":
        return np.array([
            [x_off + size/2, y_off],
            [x_off + size, y_off + size],
            [x_off, y_off + size],
            [x_off + size/2, y_off]  # Close the contour
        ], dtype=np.float32)
    elif shape == "hexagon":
        angles = np.linspace(0, 2*np.pi, 7)  # 7 points (6 + closing)
        x = x_off + size/2 + (size/2) * np.cos(angles)
        y = y_off + size/2 + (size/2) * np.sin(angles)
        return np.column_stack([x, y]).astype(np.float32)
    else:
        raise ValueError(f"Unknown shape: {shape}")
def create_test_zigzag_pattern(num_lines=5, width=100, spacing=10, offset=(0, 0)):
    """
    Create test zigzag pattern data.
    Args:
        num_lines: Number of zigzag lines
        width: Width of each line
        spacing: Vertical spacing between lines
        offset: (x, y) offset tuple
    Returns:
        List of numpy arrays representing line segments
    """
    x_off, y_off = offset
    zigzag = []
    for i in range(num_lines):
        y = y_off + i * spacing
        if i % 2 == 0:
            # Left to right
            line = np.array([[x_off, y], [x_off + width, y]], dtype=np.float32)
        else:
            # Right to left
            line = np.array([[x_off + width, y], [x_off, y]], dtype=np.float32)
        zigzag.append(line)
    return zigzag
def create_test_settings(layer="Contour", visible=True, **kwargs):
    """
    Create test settings dictionary.
    Args:
        layer: Layer name
        visible: Visibility status
        **kwargs: Additional settings
    Returns:
        Settings dictionary
    """
    settings = {
        "layer": layer,
        "visible": visible,
        "color": "#FF0000",
        "line_width": 2.0,
        "line_style": "solid",
        "opacity": 1.0
    }
    settings.update(kwargs)
    return settings
# ===== Command Testing Helpers =====
def create_command_with_effects(execute_effect=None, undo_effect=None):
    """
    Create a mock command with side effects.
    Args:
        execute_effect: Side effect for execute()
        undo_effect: Side effect for undo()
    Returns:
        Mock command
    """
    cmd = Mock()
    cmd.execute = Mock(side_effect=execute_effect)
    cmd.undo = Mock(side_effect=undo_effect)
    cmd.can_merge_with = Mock(return_value=False)
    return cmd
def assert_command_history_state(history, can_undo=None, can_redo=None, stack_size=None):
    """
    Assert command history state.
    Args:
        history: CommandHistory instance
        can_undo: Expected undo availability (None to skip)
        can_redo: Expected redo availability (None to skip)
        stack_size: Expected stack size (None to skip)
    """
    if can_undo is not None:
        assert history.can_undo() == can_undo, \
            f"Expected can_undo={can_undo}, got {history.can_undo()}"
    if can_redo is not None:
        assert history.can_redo() == can_redo, \
            f"Expected can_redo={can_redo}, got {history.can_redo()}"
    if stack_size is not None:
        actual_size = len(history._undo_stack)
        assert actual_size == stack_size, \
            f"Expected stack size={stack_size}, got {actual_size}"
# ===== Qt Testing Helpers =====
def create_qpoint_list(coordinates):
    """
    Create a list of QPointF from coordinate tuples.
    Args:
        coordinates: List of (x, y) tuples
    Returns:
        List of QPointF objects
    """
    return [QPointF(x, y) for x, y in coordinates]
def qpoint_to_tuple(point):
    """
    Convert QPointF to (x, y) tuple.
    Args:
        point: QPointF object
    Returns:
        (x, y) tuple
    """
    return (point.x(), point.y())
def qpoint_list_to_tuples(points):
    """
    Convert list of QPointF to list of tuples.
    Args:
        points: List of QPointF objects
    Returns:
        List of (x, y) tuples
    """
    return [qpoint_to_tuple(p) for p in points]

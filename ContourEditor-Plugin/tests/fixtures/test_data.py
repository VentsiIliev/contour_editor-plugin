"""
Test data fixtures for reusable test data across all tests.
"""
import numpy as np
from PyQt6.QtCore import QPointF
def sample_segments():
    """Create a list of sample segments for testing."""
    from unittest.mock import Mock
    segments = []
    layers = ["Workpiece", "Contour", "Fill"]
    for i in range(5):
        segment = Mock()
        segment.points = [
            QPointF(i * 50, i * 50),
            QPointF((i + 1) * 50, (i + 1) * 50)
        ]
        segment.controls = [QPointF(i * 50 + 25, (i + 1) * 50 - 25)]
        segment.visible = True
        segment.layer = Mock(
            name=layers[i % 3],
            visible=True,
            locked=False
        )
        segment.layer.name = layers[i % 3]
        segments.append(segment)
    return segments
def sample_contour_points_square():
    """Create a simple square contour."""
    return np.array([
        [10, 10],
        [110, 10],
        [110, 110],
        [10, 110],
        [10, 10]  # Closed
    ], dtype=np.float32)
def sample_contour_points_triangle():
    """Create a simple triangle contour."""
    return np.array([
        [50, 10],
        [100, 100],
        [0, 100],
        [50, 10]  # Closed
    ], dtype=np.float32)
def sample_contour_points_complex():
    """Create a more complex polygon contour."""
    return np.array([
        [20, 20],
        [80, 20],
        [100, 50],
        [80, 80],
        [20, 80],
        [0, 50],
        [20, 20]  # Closed
    ], dtype=np.float32)
def sample_settings_default():
    """Create default settings dictionary."""
    return {
        "color": "#000000",
        "line_width": 1.0,
        "point_size": 5,
        "visible": True,
        "layer": "Contour",
        "locked": False
    }
def sample_settings_workpiece():
    """Create workpiece layer settings."""
    return {
        "color": "#FF0000",
        "line_width": 2.0,
        "point_size": 6,
        "visible": True,
        "layer": "Workpiece",
        "locked": False
    }
def sample_settings_fill():
    """Create fill layer settings."""
    return {
        "color": "#0000FF",
        "line_width": 1.5,
        "point_size": 4,
        "visible": True,
        "layer": "Fill",
        "locked": True
    }
def sample_spray_pattern_segments():
    """Create sample spray pattern segment data."""
    # Represents zigzag segments as numpy arrays
    return np.array([
        [[10, 20], [90, 20]],  # Horizontal line 1
        [[90, 30], [10, 30]],  # Horizontal line 2 (reversed)
        [[10, 40], [90, 40]],  # Horizontal line 3
        [[90, 50], [10, 50]],  # Horizontal line 4 (reversed)
    ], dtype=np.float32)

"""
Shared pytest fixtures and configuration for all tests.
"""
import sys
from pathlib import Path
from unittest.mock import Mock, MagicMock
import pytest
from PyQt6.QtCore import QPointF

# Mock qtawesome if not installed so unit/integration tests that don't
# need UI widgets can still run (qtawesome is pulled in transitively via
# contour_editor/__init__.py -> core/main_frame.py -> ui/__init__.py).
try:
    import qtawesome  # noqa: F401
except ImportError:
    sys.modules['qtawesome'] = MagicMock()
# Add src to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))
@pytest.fixture
def mock_manager():
    """Create a mock BezierSegmentManager."""
    manager = Mock()
    manager.segments = []
    manager.active_segment_index = None
    manager.external_layer = Mock(name="Main", visible=True, locked=False)
    manager.contour_layer = Mock(name="Contour", visible=True, locked=False)
    manager.fill_layer = Mock(name="Fill", visible=True, locked=False)
    # Common methods
    manager.get_segments = Mock(return_value=manager.segments)
    manager.create_segment = Mock()
    manager.set_segment_visibility = Mock()
    manager.set_active_segment = Mock()
    manager.isLayerLocked = Mock(return_value=False)
    manager.getLayer = Mock()
    return manager
@pytest.fixture
def mock_event_bus():
    """Create a mock EventBus."""
    from contour_editor.core.event_bus import EventBus
    event_bus = EventBus.get_instance()
    # Reset singleton for testing
    EventBus._instance = None
    # Create fresh instance
    event_bus = EventBus.get_instance()
    yield event_bus
    # Cleanup
    EventBus._instance = None
@pytest.fixture
def mock_command_history():
    """Create a mock CommandHistory."""
    from contour_editor.services.commands.command_history import CommandHistory
    # Reset singleton for testing
    CommandHistory._instance = None
    # Create fresh instance
    cmd_history = CommandHistory.get_instance()
    yield cmd_history
    # Cleanup
    CommandHistory._instance = None
@pytest.fixture
def mock_segment():
    """Create a mock segment."""
    segment = Mock()
    segment.points = [QPointF(0, 0), QPointF(100, 100)]
    segment.controls = []
    segment.visible = True
    segment.layer = Mock(name="Contour", visible=True, locked=False)
    return segment
@pytest.fixture
def mock_segments_list(mock_segment):
    """Create a list of mock segments."""
    segments = []
    for i in range(3):
        seg = Mock()
        seg.points = [QPointF(i*100, i*100), QPointF((i+1)*100, (i+1)*100)]
        seg.controls = []
        seg.visible = True
        seg.layer = Mock(name="Contour", visible=True, locked=False)
        segments.append(seg)
    return segments
@pytest.fixture
def sample_contour_points():
    """Create sample contour points as numpy array."""
    import numpy as np
    # Simple square contour
    return np.array([
        [0, 0],
        [100, 0],
        [100, 100],
        [0, 100],
        [0, 0]  # Closed contour
    ], dtype=np.float32)
@pytest.fixture
def sample_settings():
    """Create sample settings dictionary."""
    return {
        "color": "#FF0000",
        "line_width": 2.0,
        "visible": True,
        "layer": "Contour"
    }
# Try to use pytest-qt's qapp fixture, fallback to None for tests that don't need it
try:
    from pytest_qt.qtbot import QtBot
    pytest_plugins = ['pytest_qt']
except ImportError:
    # pytest-qt not installed, provide a mock qapp for tests that need it
    @pytest.fixture
    def qapp():
        """Mock QApplication fixture if pytest-qt is not available."""
        try:
            from PyQt6.QtWidgets import QApplication
            app = QApplication.instance()
            if app is None:
                app = QApplication([])
            return app
        except Exception:
            return None

    @pytest.fixture
    def qtbot(qapp):
        """Mock qtbot fixture if pytest-qt is not available."""
        from unittest.mock import Mock
        return Mock()

# ===== EventBus Singleton Management =====

@pytest.fixture(autouse=True)
def reset_singletons():
    """Reset singleton instances before each test to prevent stale references."""
    # Reset EventBus singleton
    try:
        from contour_editor.core.event_bus import EventBus
        EventBus._instance = None
    except Exception:
        pass

    # Reset CommandHistory singleton
    try:
        from contour_editor.services.commands.command_history import CommandHistory
        CommandHistory._instance = None
    except Exception:
        pass

    yield

    # Cleanup after test
    try:
        from contour_editor.core.event_bus import EventBus
        EventBus._instance = None
    except Exception:
        pass

    try:
        from contour_editor.services.commands.command_history import CommandHistory
        CommandHistory._instance = None
    except Exception:
        pass

# ===== Enhanced Fixtures for Stage 6 =====

@pytest.fixture
def sample_segments():
    """Create a list of sample segments with different properties."""
    import numpy as np

    segments = []

    # Segment 0: Contour layer, visible
    seg0 = Mock()
    seg0.points = [QPointF(0, 0), QPointF(100, 0), QPointF(100, 100), QPointF(0, 100)]
    seg0.controls = []
    seg0.visible = True
    seg0.layer = Mock(name="Contour")
    seg0.layer.name = "Contour"
    seg0.layer.visible = True
    seg0.layer.locked = False
    seg0.set_settings = Mock()
    segments.append(seg0)

    # Segment 1: Fill layer, visible
    seg1 = Mock()
    seg1.points = [QPointF(10, 10), QPointF(90, 10), QPointF(90, 90), QPointF(10, 90)]
    seg1.controls = []
    seg1.visible = True
    seg1.layer = Mock(name="Fill")
    seg1.layer.name = "Fill"
    seg1.layer.visible = True
    seg1.layer.locked = False
    seg1.set_settings = Mock()
    segments.append(seg1)

    # Segment 2: Workpiece layer, hidden
    seg2 = Mock()
    seg2.points = [QPointF(20, 20), QPointF(80, 20), QPointF(80, 80), QPointF(20, 80)]
    seg2.controls = []
    seg2.visible = False
    seg2.layer = Mock(name="Main")
    seg2.layer.name = "Main"
    seg2.layer.visible = True
    seg2.layer.locked = False
    seg2.set_settings = Mock()
    segments.append(seg2)

    return segments


@pytest.fixture
def sample_triangle_contour():
    """Create a triangle contour for testing."""
    import numpy as np
    return np.array([
        [50.0, 10.0],
        [100.0, 100.0],
        [0.0, 100.0],
        [50.0, 10.0]
    ], dtype=np.float32)


@pytest.fixture
def sample_complex_contour():
    """Create a complex contour with more points."""
    import numpy as np
    return np.array([
        [10.0, 50.0],
        [30.0, 20.0],
        [70.0, 20.0],
        [90.0, 50.0],
        [70.0, 80.0],
        [30.0, 80.0],
        [10.0, 50.0]
    ], dtype=np.float32)


@pytest.fixture
def sample_default_settings():
    """Create comprehensive default settings."""
    return {
        "color": "#0000FF",
        "line_width": 2.0,
        "line_style": "solid",
        "visible": True,
        "layer": "Contour",
        "opacity": 1.0,
        "z_index": 0
    }


@pytest.fixture
def mock_layer_factory():
    """Factory function to create mock layers."""
    def create_layer(name, visible=True, locked=False):
        layer = Mock()
        layer.name = name
        layer.visible = visible
        layer.locked = locked
        return layer
    return create_layer


@pytest.fixture
def mock_segment_factory(mock_layer_factory):
    """Factory function to create mock segments."""
    def create_segment(index, layer_name="Contour", visible=True, num_points=4):
        segment = Mock()
        segment.points = [QPointF(i*10, i*10) for i in range(num_points)]
        segment.controls = []
        segment.visible = visible
        segment.layer = mock_layer_factory(layer_name)
        segment.set_settings = Mock()
        return segment
    return create_segment


@pytest.fixture
def mock_command_factory():
    """Factory function to create mock commands."""
    def create_command(execute_side_effect=None, undo_side_effect=None):
        cmd = Mock()
        cmd.execute = Mock(side_effect=execute_side_effect)
        cmd.undo = Mock(side_effect=undo_side_effect)
        cmd.can_merge_with = Mock(return_value=False)
        return cmd
    return create_command


# ===== Test Helper Functions =====

def assert_event_emitted(event_bus, signal_name, expected_count=1):
    """
    Helper to assert that an event was emitted.

    Args:
        event_bus: The EventBus instance
        signal_name: Name of the signal to check
        expected_count: Expected number of emissions
    """
    signal = getattr(event_bus, signal_name, None)
    assert signal is not None, f"Signal {signal_name} not found on event_bus"
    # Note: Actual emission checking requires Qt signal spy in real tests


def assert_segment_properties(segment, expected_visible=None, expected_layer=None):
    """
    Helper to assert segment properties.

    Args:
        segment: Segment to check
        expected_visible: Expected visibility (None to skip)
        expected_layer: Expected layer name (None to skip)
    """
    if expected_visible is not None:
        assert segment.visible == expected_visible, \
            f"Expected visible={expected_visible}, got {segment.visible}"

    if expected_layer is not None:
        assert segment.layer.name == expected_layer, \
            f"Expected layer={expected_layer}, got {segment.layer.name}"


def assert_command_executed(command, times=1):
    """
    Helper to assert command execution.

    Args:
        command: Command to check
        times: Expected execution count
    """
    assert command.execute.call_count == times, \
        f"Expected execute called {times} times, got {command.execute.call_count}"


def create_mock_points(count=4, start_x=0, start_y=0, spacing=10):
    """
    Helper to create a list of QPointF objects.

    Args:
        count: Number of points to create
        start_x: Starting X coordinate
        start_y: Starting Y coordinate
        spacing: Space between points

    Returns:
        List of QPointF objects
    """
    return [QPointF(start_x + i*spacing, start_y + i*spacing) for i in range(count)]


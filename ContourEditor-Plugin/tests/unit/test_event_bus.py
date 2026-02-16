"""
Tests for EventBus.
This module tests:
- Singleton pattern
- Signal emissions
- Multiple subscribers
- Signal cleanup
"""
import pytest
def test_event_bus_singleton(mock_event_bus):
    """Test that EventBus follows singleton pattern."""
    from contour_editor.core.event_bus import EventBus
    bus1 = EventBus.get_instance()
    bus2 = EventBus.get_instance()
    assert bus1 is bus2
def test_segment_visibility_changed_signal(mock_event_bus, qtbot):
    """Test segment_visibility_changed signal emission."""
    received_signals = []
    def slot(seg_index, visible):
        received_signals.append((seg_index, visible))
    mock_event_bus.segment_visibility_changed.connect(slot)
    mock_event_bus.segment_visibility_changed.emit(0, True)
    assert len(received_signals) == 1
    assert received_signals[0] == (0, True)
def test_segment_deleted_signal(mock_event_bus, qtbot):
    """Test segment_deleted signal emission."""
    received_signals = []
    def slot(seg_index):
        received_signals.append(seg_index)
    mock_event_bus.segment_deleted.connect(slot)
    mock_event_bus.segment_deleted.emit(5)
    assert len(received_signals) == 1
    assert received_signals[0] == 5
def test_segment_added_signal(mock_event_bus, qtbot):
    """Test segment_added signal emission."""
    received_signals = []
    def slot(seg_index):
        received_signals.append(seg_index)
    mock_event_bus.segment_added.connect(slot)
    mock_event_bus.segment_added.emit(3)
    assert len(received_signals) == 1
    assert received_signals[0] == 3
def test_segment_layer_changed_signal(mock_event_bus, qtbot):
    """Test segment_layer_changed signal emission."""
    received_signals = []
    def slot(seg_index, layer_name):
        received_signals.append((seg_index, layer_name))
    mock_event_bus.segment_layer_changed.connect(slot)
    mock_event_bus.segment_layer_changed.emit(2, "Contour")
    assert len(received_signals) == 1
    assert received_signals[0] == (2, "Contour")
def test_points_changed_signal(mock_event_bus, qtbot):
    """Test points_changed signal emission."""
    received_signals = []
    def slot():
        received_signals.append("changed")
    mock_event_bus.points_changed.connect(slot)
    mock_event_bus.points_changed.emit()
    assert len(received_signals) == 1
    assert received_signals[0] == "changed"
def test_selection_changed_signal(mock_event_bus, qtbot):
    """Test selection_changed signal emission."""
    received_signals = []
    def slot(selection_list):
        received_signals.append(selection_list)
    mock_event_bus.selection_changed.connect(slot)
    mock_event_bus.selection_changed.emit([1, 2, 3])
    assert len(received_signals) == 1
    assert received_signals[0] == [1, 2, 3]
def test_active_segment_changed_signal(mock_event_bus, qtbot):
    """Test active_segment_changed signal emission."""
    received_signals = []
    def slot(seg_index):
        received_signals.append(seg_index)
    mock_event_bus.active_segment_changed.connect(slot)
    mock_event_bus.active_segment_changed.emit(4)
    assert len(received_signals) == 1
    assert received_signals[0] == 4
def test_multiple_subscribers(mock_event_bus, qtbot):
    """Test that multiple subscribers receive signals."""
    received1 = []
    received2 = []
    received3 = []
    def slot1(seg_index, visible):
        received1.append((seg_index, visible))
    def slot2(seg_index, visible):
        received2.append((seg_index, visible))
    def slot3(seg_index, visible):
        received3.append((seg_index, visible))
    mock_event_bus.segment_visibility_changed.connect(slot1)
    mock_event_bus.segment_visibility_changed.connect(slot2)
    mock_event_bus.segment_visibility_changed.connect(slot3)
    mock_event_bus.segment_visibility_changed.emit(0, False)
    assert len(received1) == 1
    assert len(received2) == 1
    assert len(received3) == 1
    assert received1[0] == (0, False)
    assert received2[0] == (0, False)
    assert received3[0] == (0, False)
def test_signal_disconnect(mock_event_bus, qtbot):
    """Test signal disconnect and cleanup."""
    received_signals = []
    def slot(seg_index):
        received_signals.append(seg_index)
    mock_event_bus.segment_deleted.connect(slot)
    mock_event_bus.segment_deleted.emit(1)
    assert len(received_signals) == 1
    # Disconnect
    mock_event_bus.segment_deleted.disconnect(slot)
    mock_event_bus.segment_deleted.emit(2)
    # Should still be 1, not 2
    assert len(received_signals) == 1

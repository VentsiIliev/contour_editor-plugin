"""
Tests for Point Manager Data Models.
This module tests:
- ListItemData creation for different item types
- String representation
- Data storage
"""
import pytest
def test_list_item_data_layer():
    """Test ListItemData for layer items."""
    from contour_editor.widgets.point_manager.models import ListItemData
    item = ListItemData(item_type='layer', layer_name='Contour')
    assert item.item_type == 'layer'
    assert item.layer_name == 'Contour'
    assert item.seg_index is None
    assert item.point_index is None
    assert item.point_type is None
def test_list_item_data_segment():
    """Test ListItemData for segment items."""
    from contour_editor.widgets.point_manager.models import ListItemData
    item = ListItemData(item_type='segment', layer_name='Fill', seg_index=5)
    assert item.item_type == 'segment'
    assert item.layer_name == 'Fill'
    assert item.seg_index == 5
    assert item.point_index is None
    assert item.point_type is None
def test_list_item_data_point():
    """Test ListItemData for point items."""
    from contour_editor.widgets.point_manager.models import ListItemData
    item = ListItemData(
        item_type='point',
        seg_index=3,
        point_index=7,
        point_type='anchor'
    )
    assert item.item_type == 'point'
    assert item.seg_index == 3
    assert item.point_index == 7
    assert item.point_type == 'anchor'
    assert item.layer_name is None
def test_list_item_data_repr_layer():
    """Test string representation for layer items."""
    from contour_editor.widgets.point_manager.models import ListItemData
    item = ListItemData(item_type='layer', layer_name='Workpiece')
    assert repr(item) == "ListItemData(layer=Workpiece)"
def test_list_item_data_repr_segment():
    """Test string representation for segment items."""
    from contour_editor.widgets.point_manager.models import ListItemData
    item = ListItemData(item_type='segment', layer_name='Contour', seg_index=2)
    assert repr(item) == "ListItemData(segment=2, layer=Contour)"
def test_list_item_data_repr_point():
    """Test string representation for point items."""
    from contour_editor.widgets.point_manager.models import ListItemData
    item = ListItemData(item_type='point', seg_index=1, point_index=4, point_type='control')
    assert repr(item) == "ListItemData(point=control[4], segment=1)"
def test_list_item_data_repr_unknown():
    """Test string representation for unknown item type."""
    from contour_editor.widgets.point_manager.models import ListItemData
    item = ListItemData(item_type='unknown')
    assert repr(item) == "ListItemData(type=unknown)"
def test_list_item_data_all_params():
    """Test ListItemData with all parameters specified."""
    from contour_editor.widgets.point_manager.models import ListItemData
    item = ListItemData(
        item_type='point',
        layer_name='Fill',
        seg_index=10,
        point_index=20,
        point_type='anchor'
    )
    assert item.item_type == 'point'
    assert item.layer_name == 'Fill'
    assert item.seg_index == 10
    assert item.point_index == 20
    assert item.point_type == 'anchor'

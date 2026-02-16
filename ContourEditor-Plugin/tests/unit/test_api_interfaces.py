"""
Tests for API Interfaces.

This module tests:
- Segment class (points, controls, settings, visibility, layers)
- Layer class (segment management, visibility, locking)
- ISegmentManager interface compliance
- ISettingsProvider interface compliance
"""
import pytest
from unittest.mock import Mock
from PyQt6.QtCore import QPointF


class TestSegment:
    """Tests for Segment class"""

    def test_segment_initialization(self):
        """Test basic segment initialization"""
        from contour_editor.api.interfaces import Segment, Layer

        layer = Layer("Contour")
        segment = Segment(layer)

        assert segment.points == []
        assert segment.controls == []
        assert segment.visible is True
        assert segment.layer is layer
        assert segment.settings == {}

    def test_segment_with_settings(self):
        """Test segment initialization with settings"""
        from contour_editor.api.interfaces import Segment, Layer

        settings = {"color": "#FF0000", "width": 2}
        layer = Layer("Contour")
        segment = Segment(layer, settings)

        assert segment.settings == settings

    def test_add_point(self):
        """Test adding a point to segment"""
        from contour_editor.api.interfaces import Segment

        segment = Segment()
        point = QPointF(10, 20)

        segment.add_point(point)

        assert len(segment.points) == 1
        assert segment.points[0] == point

    def test_add_multiple_points(self):
        """Test adding multiple points"""
        from contour_editor.api.interfaces import Segment

        segment = Segment()
        points = [QPointF(i*10, i*20) for i in range(5)]

        for point in points:
            segment.add_point(point)

        assert len(segment.points) == 5
        assert segment.points == points

    def test_add_point_creates_control_points(self):
        """Test that adding points auto-creates control point slots"""
        from contour_editor.api.interfaces import Segment

        segment = Segment()
        segment.add_point(QPointF(0, 0))
        segment.add_point(QPointF(10, 10))

        # After 2nd point, should have 1 control slot
        assert len(segment.controls) == 1

    def test_remove_point(self):
        """Test removing a point"""
        from contour_editor.api.interfaces import Segment

        segment = Segment()
        segment.add_point(QPointF(0, 0))
        segment.add_point(QPointF(10, 10))
        segment.add_point(QPointF(20, 20))

        assert len(segment.points) == 3
        segment.remove_point(1)
        assert len(segment.points) == 2

    def test_remove_point_out_of_bounds(self):
        """Test removing point at invalid index"""
        from contour_editor.api.interfaces import Segment

        segment = Segment()
        segment.add_point(QPointF(0, 0))

        # Should not raise
        segment.remove_point(5)
        assert len(segment.points) == 1

    def test_add_control_point(self):
        """Test adding a control point"""
        from contour_editor.api.interfaces import Segment

        segment = Segment()
        segment.add_point(QPointF(0, 0))
        segment.add_point(QPointF(10, 10))

        control = QPointF(5, 5)
        segment.add_control_point(0, control)

        assert segment.controls[0] == control

    def test_add_control_point_out_of_range(self):
        """Test adding control point at new index"""
        from contour_editor.api.interfaces import Segment

        segment = Segment()
        control = QPointF(5, 5)

        # Should create new slot
        segment.add_control_point(0, control)
        assert len(segment.controls) == 1
        assert segment.controls[0] == control

    def test_set_layer(self):
        """Test setting segment layer"""
        from contour_editor.api.interfaces import Segment, Layer

        segment = Segment()
        layer1 = Layer("Contour")
        layer2 = Layer("Fill")

        segment.set_layer(layer1)
        assert segment.layer is layer1

        segment.set_layer(layer2)
        assert segment.layer is layer2

    def test_set_settings(self):
        """Test setting segment settings"""
        from contour_editor.api.interfaces import Segment

        segment = Segment()
        assert segment.settings == {}

        settings = {"color": "#00FF00", "width": 3}
        segment.set_settings(settings)

        assert segment.settings == settings

    def test_segment_visibility(self):
        """Test segment visibility toggle"""
        from contour_editor.api.interfaces import Segment

        segment = Segment()
        assert segment.visible is True

        segment.visible = False
        assert segment.visible is False

    def test_segment_str_representation(self):
        """Test segment string representation"""
        from contour_editor.api.interfaces import Segment, Layer

        layer = Layer("Contour")
        segment = Segment(layer)
        segment.add_point(QPointF(0, 0))
        segment.add_point(QPointF(10, 10))

        str_repr = str(segment)
        assert "points=2" in str_repr
        assert "Contour" in str_repr


class TestLayer:
    """Tests for Layer class"""

    def test_layer_initialization(self):
        """Test basic layer initialization"""
        from contour_editor.api.interfaces import Layer

        layer = Layer("Contour")

        assert layer.name == "Contour"
        assert layer.locked is False
        assert layer.visible is True
        assert layer.segments == []

    def test_layer_with_properties(self):
        """Test layer initialization with properties"""
        from contour_editor.api.interfaces import Layer

        layer = Layer("Fill", locked=True, visible=False)

        assert layer.name == "Fill"
        assert layer.locked is True
        assert layer.visible is False

    def test_add_segment_to_layer(self):
        """Test adding segment to layer"""
        from contour_editor.api.interfaces import Layer, Segment

        layer = Layer("Contour")
        segment = Segment(layer)

        layer.add_segment(segment)

        assert len(layer.segments) == 1
        assert layer.segments[0] is segment

    def test_add_multiple_segments(self):
        """Test adding multiple segments to layer"""
        from contour_editor.api.interfaces import Layer, Segment

        layer = Layer("Contour")
        segments = [Segment(layer) for _ in range(3)]

        for segment in segments:
            layer.add_segment(segment)

        assert len(layer.segments) == 3
        assert layer.segments == segments

    def test_remove_segment(self):
        """Test removing segment from layer"""
        from contour_editor.api.interfaces import Layer, Segment

        layer = Layer("Contour")
        seg1 = Segment(layer)
        seg2 = Segment(layer)
        seg3 = Segment(layer)

        for seg in [seg1, seg2, seg3]:
            layer.add_segment(seg)

        assert len(layer.segments) == 3
        layer.remove_segment(1)
        assert len(layer.segments) == 2

    def test_remove_segment_out_of_bounds(self):
        """Test removing segment at invalid index"""
        from contour_editor.api.interfaces import Layer, Segment

        layer = Layer("Contour")
        layer.add_segment(Segment(layer))

        # Should not raise
        layer.remove_segment(5)
        assert len(layer.segments) == 1

    def test_layer_visibility_toggle(self):
        """Test toggling layer visibility"""
        from contour_editor.api.interfaces import Layer

        layer = Layer("Contour", visible=True)
        assert layer.visible is True

        layer.visible = False
        assert layer.visible is False

    def test_layer_lock_toggle(self):
        """Test toggling layer lock"""
        from contour_editor.api.interfaces import Layer

        layer = Layer("Contour", locked=False)
        assert layer.locked is False

        layer.locked = True
        assert layer.locked is True

    def test_layer_str_representation(self):
        """Test layer string representation"""
        from contour_editor.api.interfaces import Layer, Segment

        layer = Layer("Fill", visible=True, locked=False)
        layer.add_segment(Segment(layer))
        layer.add_segment(Segment(layer))

        str_repr = str(layer)
        assert "Fill" in str_repr
        assert "segments=2" in str_repr


class TestSettingsProvider:
    """Tests for ISettingsProvider interface"""

    def test_settings_provider_abstract_methods(self):
        """Test that ISettingsProvider defines required abstract methods"""
        from contour_editor.api.interfaces import ISettingsProvider

        # All these methods should exist on the interface
        abstract_methods = {
            'get_all_setting_keys',
            'get_default_values',
            'get_material_type_key',
            'get_available_material_types',
            'get_default_material_type',
            'get_setting_label',
            'get_settings_tabs_config',
        }

        for method_name in abstract_methods:
            assert hasattr(ISettingsProvider, method_name)

    def test_validate_setting_value_default_implementation(self):
        """Test that validate_setting_value has default implementation"""
        from contour_editor.api.interfaces import ISettingsProvider

        # Create a mock implementation
        class TestSettingsProvider(ISettingsProvider):
            def get_all_setting_keys(self):
                return []

            def get_default_values(self):
                return {}

            def get_material_type_key(self):
                return "Material"

            def get_available_material_types(self):
                return ["Type1"]

            def get_default_material_type(self):
                return "Type1"

            def get_setting_label(self, key):
                return "Label"

            def get_settings_tabs_config(self):
                return []

        provider = TestSettingsProvider()

        # Default validate should accept everything
        is_valid, error = provider.validate_setting_value("any_key", "any_value")
        assert is_valid is True
        assert error is None

    def test_settings_provider_contract(self):
        """Test concrete implementation of ISettingsProvider"""
        from contour_editor.api.interfaces import ISettingsProvider

        class MockSettingsProvider(ISettingsProvider):
            def get_all_setting_keys(self):
                return ["Spray Width", "Fan Speed", "Glue Type"]

            def get_default_values(self):
                return {
                    "Spray Width": 10,
                    "Fan Speed": 50,
                    "Glue Type": "Default"
                }

            def get_material_type_key(self):
                return "Glue Type"

            def get_available_material_types(self):
                return ["Default", "Premium", "Heavy"]

            def get_default_material_type(self):
                return "Default"

            def get_setting_label(self, key):
                return f"{key}:"

            def get_settings_tabs_config(self):
                return [
                    ("General", ["Spray Width", "Fan Speed"]),
                    ("Material", ["Glue Type"])
                ]

        provider = MockSettingsProvider()

        assert len(provider.get_all_setting_keys()) == 3
        assert provider.get_default_values()["Spray Width"] == 10
        assert provider.get_material_type_key() == "Glue Type"
        assert "Premium" in provider.get_available_material_types()
        assert provider.get_default_material_type() == "Default"
        assert provider.get_setting_label("Spray Width") == "Spray Width:"
        assert len(provider.get_settings_tabs_config()) == 2


@pytest.mark.unit
class TestInterfaceSegmentManager:
    """Tests for ISegmentManager interface"""

    def test_segment_manager_abstract_methods(self):
        """Test that ISegmentManager defines required abstract methods"""
        from contour_editor.api.interfaces import ISegmentManager

        abstract_methods = {
            'create_segment',
            'get_segments',
            'get_layer',
            'undo',
            'redo',
        }

        for method_name in abstract_methods:
            assert hasattr(ISegmentManager, method_name)

    def test_segment_manager_property_segments(self):
        """Test that ISegmentManager has segments property"""
        from contour_editor.api.interfaces import ISegmentManager

        # Should have segments property
        assert hasattr(ISegmentManager, 'segments')

    def test_mock_segment_manager_implementation(self):
        """Test implementing ISegmentManager with mock"""
        from contour_editor.api.interfaces import ISegmentManager, Segment, Layer

        class MockSegmentManager(ISegmentManager):
            def __init__(self):
                self._segments = []

            def create_segment(self, points, layer_name="Contour"):
                layer = Layer(layer_name)
                segment = Segment(layer)
                for point in points:
                    segment.add_point(point)
                self._segments.append(segment)
                return segment

            def get_segments(self):
                return self._segments

            def get_layer(self, name):
                for segment in self._segments:
                    if segment.layer and segment.layer.name == name:
                        return segment.layer
                return None

            def undo(self):
                pass

            def redo(self):
                pass

            @property
            def segments(self):
                return self._segments

        manager = MockSegmentManager()
        assert len(manager.get_segments()) == 0

        points = [QPointF(0, 0), QPointF(10, 10)]
        segment = manager.create_segment(points, "Contour")
        assert len(manager.get_segments()) == 1
        assert segment.layer.name == "Contour"


@pytest.mark.unit
class TestInterfaceCompliance:
    """Test interface compliance and contracts"""

    def test_segment_implements_expected_interface(self):
        """Test that Segment implements expected interface"""
        from contour_editor.api.interfaces import Segment

        segment = Segment()

        # Should have all expected attributes and methods
        assert hasattr(segment, 'points')
        assert hasattr(segment, 'controls')
        assert hasattr(segment, 'visible')
        assert hasattr(segment, 'layer')
        assert hasattr(segment, 'settings')
        assert callable(segment.add_point)
        assert callable(segment.remove_point)
        assert callable(segment.add_control_point)
        assert callable(segment.set_layer)
        assert callable(segment.set_settings)

    def test_layer_implements_expected_interface(self):
        """Test that Layer implements expected interface"""
        from contour_editor.api.interfaces import Layer

        layer = Layer("Test")

        # Should have all expected attributes and methods
        assert hasattr(layer, 'name')
        assert hasattr(layer, 'locked')
        assert hasattr(layer, 'visible')
        assert hasattr(layer, 'segments')
        assert callable(layer.add_segment)
        assert callable(layer.remove_segment)

    def test_segment_and_layer_integration(self):
        """Test integration between Segment and Layer"""
        from contour_editor.api.interfaces import Segment, Layer

        layer = Layer("Contour")
        segment = Segment(layer)

        assert segment.layer is layer
        assert segment.layer.name == "Contour"

        layer.add_segment(segment)
        assert len(layer.segments) == 1
        assert layer.segments[0] is segment


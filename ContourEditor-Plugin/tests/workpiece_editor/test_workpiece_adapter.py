import pytest
import numpy as np
from PyQt6.QtCore import QPointF
from unittest.mock import Mock
from workpiece_editor.adapters import WorkpieceAdapter
from contour_editor.persistence.data.editor_data_model import ContourEditorData
from contour_editor.models.segment import Segment, Layer
class TestWorkpieceAdapterConstants:
    def test_layer_constants(self):
        assert WorkpieceAdapter.LAYER_WORKPIECE == "Workpiece"
        assert WorkpieceAdapter.LAYER_CONTOUR == "Contour"
        assert WorkpieceAdapter.LAYER_FILL == "Fill"
class TestWorkpieceAdapterToWorkpieceData:
    def test_to_workpiece_data_basic(self):
        editor_data = ContourEditorData()
        workpiece_layer = Layer("Workpiece")
        segment = Segment(layer=workpiece_layer)
        segment.add_point(QPointF(10, 10))
        segment.add_point(QPointF(100, 10))
        workpiece_layer.add_segment(segment)
        editor_data.add_layer(workpiece_layer)
        result = WorkpieceAdapter.to_workpiece_data(editor_data)
        assert "main_contour" in result
        assert "main_settings" in result
        assert "spray_pattern" in result
        assert result["main_contour"] is not None
    def test_to_workpiece_data_empty(self):
        editor_data = ContourEditorData()
        result = WorkpieceAdapter.to_workpiece_data(editor_data)
        assert result["main_contour"] is not None
        assert result["spray_pattern"]["Contour"] == []
        assert result["spray_pattern"]["Fill"] == []
class TestWorkpieceAdapterSegmentConversion:
    def test_segment_to_contour_array(self):
        layer = Layer("Test")
        segment = Segment(layer=layer)
        segment.add_point(QPointF(10.5, 20.5))
        segment.add_point(QPointF(30.5, 40.5))
        result = WorkpieceAdapter._segment_to_contour_array(segment)
        assert isinstance(result, np.ndarray)
        assert result.dtype == np.float32
        assert result.shape == (2, 1, 2)
    def test_segment_to_contour_empty(self):
        layer = Layer("Test")
        segment = Segment(layer=layer)
        result = WorkpieceAdapter._segment_to_contour_array(segment)
        assert result is None
class TestWorkpieceAdapterPrintSummary:
    def test_print_summary(self, capsys):
        editor_data = ContourEditorData()
        workpiece_layer = Layer("Workpiece")
        segment = Segment(layer=workpiece_layer)
        segment.add_point(QPointF(10, 10))
        segment.add_point(QPointF(100, 10))
        workpiece_layer.add_segment(segment)
        editor_data.add_layer(workpiece_layer)
        WorkpieceAdapter.print_summary(editor_data)
        captured = capsys.readouterr()
        assert "WorkpieceAdapter Summary" in captured.out
        assert "segment" in captured.out.lower()
class TestWorkpieceAdapterEdgeCases:
    """Test edge cases in adapter functionality"""
    def test_to_workpiece_data_with_nan_values(self):
        """Test handling of NaN values in contour data"""
        editor_data = ContourEditorData()
        workpiece_layer = Layer("Workpiece")
        segment = Segment(layer=workpiece_layer)
        segment.add_point(QPointF(10, 20))
        segment.add_point(QPointF(float('nan'), 30))  # NaN value
        segment.add_point(QPointF(40, 50))
        workpiece_layer.add_segment(segment)
        editor_data.add_layer(workpiece_layer)
        result = WorkpieceAdapter.to_workpiece_data(editor_data)
        # Should handle NaN gracefully
        assert result is not None
        assert "main_contour" in result
    def test_to_workpiece_data_with_infinite_coordinates(self):
        """Test handling of infinite coordinates"""
        editor_data = ContourEditorData()
        workpiece_layer = Layer("Workpiece")
        segment = Segment(layer=workpiece_layer)
        segment.add_point(QPointF(10, 20))
        segment.add_point(QPointF(float('inf'), 30))  # Infinite value
        workpiece_layer.add_segment(segment)
        editor_data.add_layer(workpiece_layer)
        result = WorkpieceAdapter.to_workpiece_data(editor_data)
        # Should handle infinity gracefully
        assert result is not None
    def test_to_workpiece_data_large_contours(self):
        """Test handling of large contour data"""
        editor_data = ContourEditorData()
        workpiece_layer = Layer("Workpiece")
        segment = Segment(layer=workpiece_layer)
        # Add 10000 points
        for i in range(10000):
            segment.add_point(QPointF(float(i), float(i * 2)))
        workpiece_layer.add_segment(segment)
        editor_data.add_layer(workpiece_layer)
        result = WorkpieceAdapter.to_workpiece_data(editor_data)
        assert result is not None
        assert result["main_contour"] is not None
        # Contour should have 10000 points
        assert len(result["main_contour"]) == 10000
    def test_segment_to_contour_array_single_point(self):
        """Test conversion of single-point segment"""
        layer = Layer("Test")
        segment = Segment(layer=layer)
        segment.add_point(QPointF(10, 20))
        result = WorkpieceAdapter._segment_to_contour_array(segment)
        assert result is not None
        assert result.shape == (1, 1, 2)
        assert result[0, 0, 0] == 10.0
        assert result[0, 0, 1] == 20.0
    def test_normalize_layer_data_empty_layers(self):
        """Test normalization with empty layers"""
        editor_data = ContourEditorData()
        # Add empty layers
        editor_data.add_layer(Layer("Workpiece"))
        editor_data.add_layer(Layer("Contour"))
        editor_data.add_layer(Layer("Fill"))
        result = WorkpieceAdapter.to_workpiece_data(editor_data)
        assert result is not None
        assert result["spray_pattern"]["Contour"] == []
        assert result["spray_pattern"]["Fill"] == []
class TestWorkpieceAdapterMultiLayer:
    """Test multi-layer functionality"""
    def test_to_workpiece_data_multiple_contour_layers(self):
        """Test with multiple contour segments"""
        editor_data = ContourEditorData()
        # Add workpiece
        workpiece_layer = Layer("Workpiece")
        segment1 = Segment(layer=workpiece_layer)
        segment1.add_point(QPointF(0, 0))
        segment1.add_point(QPointF(100, 0))
        workpiece_layer.add_segment(segment1)
        editor_data.add_layer(workpiece_layer)
        # Add multiple contour segments
        contour_layer = Layer("Contour")
        for i in range(3):
            segment = Segment(layer=contour_layer)
            segment.add_point(QPointF(10 + i*10, 20))
            segment.add_point(QPointF(20 + i*10, 30))
            segment.settings = {"speed": "100", "power": "50"}
            contour_layer.add_segment(segment)
        editor_data.add_layer(contour_layer)
        result = WorkpieceAdapter.to_workpiece_data(editor_data)
        assert result["spray_pattern"]["Contour"] is not None
        assert len(result["spray_pattern"]["Contour"]) == 3
    def test_to_workpiece_data_multiple_fill_layers(self):
        """Test with multiple fill segments"""
        editor_data = ContourEditorData()
        # Add workpiece
        workpiece_layer = Layer("Workpiece")
        segment1 = Segment(layer=workpiece_layer)
        segment1.add_point(QPointF(0, 0))
        segment1.add_point(QPointF(100, 0))
        workpiece_layer.add_segment(segment1)
        editor_data.add_layer(workpiece_layer)
        # Add multiple fill segments
        fill_layer = Layer("Fill")
        for i in range(2):
            segment = Segment(layer=fill_layer)
            segment.add_point(QPointF(10 + i*20, 20))
            segment.add_point(QPointF(20 + i*20, 30))
            segment.add_point(QPointF(15 + i*20, 40))
            segment.settings = {"speed": "80", "power": "60"}
            fill_layer.add_segment(segment)
        editor_data.add_layer(fill_layer)
        result = WorkpieceAdapter.to_workpiece_data(editor_data)
        assert result["spray_pattern"]["Fill"] is not None
        assert len(result["spray_pattern"]["Fill"]) == 2
    def test_to_workpiece_data_mixed_layers_with_settings(self):
        """Test with mixed contour and fill layers with settings"""
        editor_data = ContourEditorData()
        # Add workpiece
        workpiece_layer = Layer("Workpiece")
        segment1 = Segment(layer=workpiece_layer)
        segment1.add_point(QPointF(0, 0))
        segment1.add_point(QPointF(100, 100))
        segment1.settings = {"speed": "100", "power": "50", "passes": "1"}
        workpiece_layer.add_segment(segment1)
        editor_data.add_layer(workpiece_layer)
        # Add contour
        contour_layer = Layer("Contour")
        contour_segment = Segment(layer=contour_layer)
        contour_segment.add_point(QPointF(10, 10))
        contour_segment.add_point(QPointF(20, 20))
        contour_segment.settings = {"speed": "90", "power": "55"}
        contour_layer.add_segment(contour_segment)
        editor_data.add_layer(contour_layer)
        # Add fill
        fill_layer = Layer("Fill")
        fill_segment = Segment(layer=fill_layer)
        fill_segment.add_point(QPointF(15, 15))
        fill_segment.add_point(QPointF(25, 25))
        fill_segment.settings = {"speed": "70", "power": "65"}
        fill_layer.add_segment(fill_segment)
        editor_data.add_layer(fill_layer)
        result = WorkpieceAdapter.to_workpiece_data(editor_data)
        # Check main settings
        assert result["main_settings"] is not None
        assert result["main_settings"]["speed"] == "100"
        # Check spray pattern
        assert len(result["spray_pattern"]["Contour"]) == 1
        assert len(result["spray_pattern"]["Fill"]) == 1
        assert result["spray_pattern"]["Contour"][0]["settings"]["speed"] == "90"
        assert result["spray_pattern"]["Fill"][0]["settings"]["speed"] == "70"
    def test_layer_name_mapping_consistency(self):
        """Test that layer name mapping is consistent"""
        editor_data = ContourEditorData()
        # Add all layer types
        for layer_name in ["Workpiece", "Contour", "Fill"]:
            layer = Layer(layer_name)
            segment = Segment(layer=layer)
            segment.add_point(QPointF(10, 20))
            segment.add_point(QPointF(30, 40))
            layer.add_segment(segment)
            editor_data.add_layer(layer)
        result = WorkpieceAdapter.to_workpiece_data(editor_data)
        # Verify structure
        assert "main_contour" in result
        assert "spray_pattern" in result
        assert "Contour" in result["spray_pattern"]
        assert "Fill" in result["spray_pattern"]
    def test_spray_pattern_structure_validation(self):
        """Test spray pattern data structure is valid"""
        editor_data = ContourEditorData()
        # Add workpiece
        workpiece_layer = Layer("Workpiece")
        segment = Segment(layer=workpiece_layer)
        segment.add_point(QPointF(0, 0))
        segment.add_point(QPointF(50, 50))
        workpiece_layer.add_segment(segment)
        editor_data.add_layer(workpiece_layer)
        # Add contour
        contour_layer = Layer("Contour")
        contour_seg = Segment(layer=contour_layer)
        contour_seg.add_point(QPointF(10, 10))
        contour_seg.add_point(QPointF(20, 20))
        contour_seg.settings = {"speed": "100"}
        contour_layer.add_segment(contour_seg)
        editor_data.add_layer(contour_layer)
        result = WorkpieceAdapter.to_workpiece_data(editor_data)
        # Validate spray pattern structure
        spray_pattern = result["spray_pattern"]
        assert isinstance(spray_pattern, dict)
        assert "Contour" in spray_pattern
        assert "Fill" in spray_pattern
        assert isinstance(spray_pattern["Contour"], list)
        assert isinstance(spray_pattern["Fill"], list)
        # Validate contour item structure
        if len(spray_pattern["Contour"]) > 0:
            contour_item = spray_pattern["Contour"][0]
            assert "contour" in contour_item
            assert "settings" in contour_item
            assert isinstance(contour_item["contour"], np.ndarray)
            assert isinstance(contour_item["settings"], dict)

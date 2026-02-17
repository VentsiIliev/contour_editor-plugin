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

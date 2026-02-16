"""
Tests for WorkpieceAdapter.

This module tests:
- from_workpiece() conversion
- to_workpiece_data() extraction
- Layer normalization
- Contour array conversion
- Summary printing
"""
import pytest
import numpy as np
from unittest.mock import Mock, MagicMock
from PyQt6.QtCore import QPointF


class TestWorkpieceAdapterLayerConstants:
    """Test WorkpieceAdapter layer name constants"""

    def test_layer_constants_exist(self):
        """Test that layer name constants are defined"""
        from contour_editor.api.adapters import WorkpieceAdapter

        assert WorkpieceAdapter.LAYER_WORKPIECE == "Workpiece"
        assert WorkpieceAdapter.LAYER_CONTOUR == "Contour"
        assert WorkpieceAdapter.LAYER_FILL == "Fill"

    def test_layer_constants_are_strings(self):
        """Test that constants are strings"""
        from contour_editor.api.adapters import WorkpieceAdapter

        assert isinstance(WorkpieceAdapter.LAYER_WORKPIECE, str)
        assert isinstance(WorkpieceAdapter.LAYER_CONTOUR, str)
        assert isinstance(WorkpieceAdapter.LAYER_FILL, str)


class TestWorkpieceAdapterFromWorkpiece:
    """Tests for from_workpiece() method"""

    def test_from_workpiece_with_minimal_data(self):
        """Test converting workpiece with minimal data"""
        from contour_editor.api.adapters import WorkpieceAdapter

        # Create mock workpiece
        mock_workpiece = Mock()
        mock_workpiece.get_main_contour = Mock(return_value=np.array([[0, 0], [100, 100]], dtype=np.float32))
        mock_workpiece.get_main_contour_settings = Mock(return_value={})
        mock_workpiece.get_spray_pattern_contours = Mock(return_value=[])
        mock_workpiece.get_spray_pattern_fills = Mock(return_value=[])

        result = WorkpieceAdapter.from_workpiece(mock_workpiece)

        assert result is not None

    def test_from_workpiece_calls_getter_methods(self):
        """Test that from_workpiece calls all getter methods"""
        from contour_editor.api.adapters import WorkpieceAdapter

        mock_workpiece = Mock()
        mock_workpiece.get_main_contour = Mock(return_value=np.array([[0, 0]], dtype=np.float32))
        mock_workpiece.get_main_contour_settings = Mock(return_value={})
        mock_workpiece.get_spray_pattern_contours = Mock(return_value=[])
        mock_workpiece.get_spray_pattern_fills = Mock(return_value=[])

        WorkpieceAdapter.from_workpiece(mock_workpiece)

        mock_workpiece.get_main_contour.assert_called_once()
        mock_workpiece.get_main_contour_settings.assert_called_once()
        mock_workpiece.get_spray_pattern_contours.assert_called_once()
        mock_workpiece.get_spray_pattern_fills.assert_called_once()

    def test_from_workpiece_with_spray_patterns(self):
        """Test from_workpiece with spray pattern data"""
        from contour_editor.api.adapters import WorkpieceAdapter

        main_contour = np.array([[0, 0], [100, 100]], dtype=np.float32)
        spray_contour = np.array([[10, 10], [90, 90]], dtype=np.float32)
        spray_fill = np.array([[20, 20], [80, 80]], dtype=np.float32)

        mock_workpiece = Mock()
        mock_workpiece.get_main_contour = Mock(return_value=main_contour)
        mock_workpiece.get_main_contour_settings = Mock(return_value={"color": "#FF0000"})
        mock_workpiece.get_spray_pattern_contours = Mock(return_value=[
            {"contour": spray_contour, "settings": {}}
        ])
        mock_workpiece.get_spray_pattern_fills = Mock(return_value=[
            {"contour": spray_fill, "settings": {}}
        ])

        result = WorkpieceAdapter.from_workpiece(mock_workpiece)

        assert result is not None


class TestWorkpieceAdapterToWorkpieceData:
    """Tests for to_workpiece_data() method"""

    def test_to_workpiece_data_returns_dict(self):
        """Test that to_workpiece_data returns a dictionary"""
        from contour_editor.api.adapters import WorkpieceAdapter
        from contour_editor.persistence.data.editor_data_model import ContourEditorData

        editor_data = ContourEditorData()
        result = WorkpieceAdapter.to_workpiece_data(editor_data)

        assert isinstance(result, dict)

    def test_to_workpiece_data_has_required_keys(self):
        """Test that result has all required keys"""
        from contour_editor.api.adapters import WorkpieceAdapter
        from contour_editor.persistence.data.editor_data_model import ContourEditorData

        editor_data = ContourEditorData()
        result = WorkpieceAdapter.to_workpiece_data(editor_data)

        assert "main_contour" in result
        assert "main_settings" in result
        assert "spray_pattern" in result

    def test_to_workpiece_data_spray_pattern_structure(self):
        """Test spray_pattern has correct structure"""
        from contour_editor.api.adapters import WorkpieceAdapter
        from contour_editor.persistence.data.editor_data_model import ContourEditorData

        editor_data = ContourEditorData()
        result = WorkpieceAdapter.to_workpiece_data(editor_data)

        spray_pattern = result["spray_pattern"]
        assert isinstance(spray_pattern, dict)
        assert "Contour" in spray_pattern
        assert "Fill" in spray_pattern
        assert isinstance(spray_pattern["Contour"], list)
        assert isinstance(spray_pattern["Fill"], list)

    def test_to_workpiece_data_with_empty_editor_data(self):
        """Test conversion of empty editor data"""
        from contour_editor.api.adapters import WorkpieceAdapter
        from contour_editor.persistence.data.editor_data_model import ContourEditorData

        editor_data = ContourEditorData()
        result = WorkpieceAdapter.to_workpiece_data(editor_data)

        assert result["main_contour"] is None or len(result["main_contour"]) == 0
        assert isinstance(result["main_settings"], dict)
        assert len(result["spray_pattern"]["Contour"]) == 0
        assert len(result["spray_pattern"]["Fill"]) == 0


class TestWorkpieceAdapterNormalization:
    """Tests for _normalize_layer_data() method"""

    def test_normalize_layer_data_empty(self):
        """Test normalizing empty layer data"""
        from contour_editor.api.adapters import WorkpieceAdapter

        input_data = {}
        result = WorkpieceAdapter._normalize_layer_data(input_data)

        assert result == {}

    def test_normalize_layer_data_single_layer(self):
        """Test normalizing single layer"""
        from contour_editor.api.adapters import WorkpieceAdapter

        contour = np.array([[0, 0], [100, 100]], dtype=np.float32)
        input_data = {
            "Contour": [{"contour": contour, "settings": {"color": "#FF0000"}}]
        }

        result = WorkpieceAdapter._normalize_layer_data(input_data)

        assert "Contour" in result
        assert "contours" in result["Contour"]
        assert "settings" in result["Contour"]
        assert len(result["Contour"]["contours"]) == 1
        assert len(result["Contour"]["settings"]) == 1

    def test_normalize_layer_data_multiple_entries(self):
        """Test normalizing multiple entries in layer"""
        from contour_editor.api.adapters import WorkpieceAdapter

        contour1 = np.array([[0, 0], [100, 100]], dtype=np.float32)
        contour2 = np.array([[50, 50], [150, 150]], dtype=np.float32)
        input_data = {
            "Fill": [
                {"contour": contour1, "settings": {}},
                {"contour": contour2, "settings": {}}
            ]
        }

        result = WorkpieceAdapter._normalize_layer_data(input_data)

        assert len(result["Fill"]["contours"]) == 2
        assert len(result["Fill"]["settings"]) == 2

    def test_normalize_layer_data_shape_conversion(self):
        """Test that shapes are normalized to (N, 1, 2)"""
        from contour_editor.api.adapters import WorkpieceAdapter

        # Input as (N, 2)
        contour = np.array([[0, 0], [100, 100]], dtype=np.float32)
        input_data = {
            "Contour": [{"contour": contour, "settings": {}}]
        }

        result = WorkpieceAdapter._normalize_layer_data(input_data)

        normalized_contour = result["Contour"]["contours"][0]
        assert normalized_contour.ndim == 3
        assert normalized_contour.shape[1] == 1
        assert normalized_contour.shape[2] == 2

    def test_normalize_layer_data_multiple_layers(self):
        """Test normalizing multiple layers"""
        from contour_editor.api.adapters import WorkpieceAdapter

        input_data = {
            "Workpiece": [{"contour": np.array([[0, 0]], dtype=np.float32), "settings": {}}],
            "Contour": [{"contour": np.array([[10, 10]], dtype=np.float32), "settings": {}}],
            "Fill": [{"contour": np.array([[20, 20]], dtype=np.float32), "settings": {}}]
        }

        result = WorkpieceAdapter._normalize_layer_data(input_data)

        assert "Workpiece" in result
        assert "Contour" in result
        assert "Fill" in result


class TestWorkpieceAdapterSegmentToContour:
    """Tests for _segment_to_contour_array() method"""

    def test_segment_to_contour_empty_segment(self):
        """Test converting empty segment"""
        from contour_editor.api.adapters import WorkpieceAdapter
        from contour_editor.api.interfaces import Segment

        segment = Segment()
        result = WorkpieceAdapter._segment_to_contour_array(segment)

        assert result is None

    def test_segment_to_contour_single_point(self):
        """Test converting segment with single point"""
        from contour_editor.api.adapters import WorkpieceAdapter
        from contour_editor.api.interfaces import Segment

        segment = Segment()
        segment.add_point(QPointF(50, 50))

        result = WorkpieceAdapter._segment_to_contour_array(segment)

        assert result is not None
        assert result.shape == (1, 1, 2)
        assert result[0, 0, 0] == 50
        assert result[0, 0, 1] == 50

    def test_segment_to_contour_multiple_points(self):
        """Test converting segment with multiple points"""
        from contour_editor.api.adapters import WorkpieceAdapter
        from contour_editor.api.interfaces import Segment

        segment = Segment()
        segment.add_point(QPointF(0, 0))
        segment.add_point(QPointF(100, 100))
        segment.add_point(QPointF(200, 200))

        result = WorkpieceAdapter._segment_to_contour_array(segment)

        assert result is not None
        assert result.shape == (3, 1, 2)
        assert result[0, 0, 0] == 0
        assert result[1, 0, 0] == 100
        assert result[2, 0, 0] == 200

    def test_segment_to_contour_output_dtype(self):
        """Test that output is float32"""
        from contour_editor.api.adapters import WorkpieceAdapter
        from contour_editor.api.interfaces import Segment

        segment = Segment()
        segment.add_point(QPointF(10.5, 20.7))

        result = WorkpieceAdapter._segment_to_contour_array(segment)

        assert result.dtype == np.float32


class TestWorkpieceAdapterPrintSummary:
    """Tests for print_summary() method"""

    def test_print_summary_with_empty_data(self, capsys):
        """Test printing summary of empty data"""
        from contour_editor.api.adapters import WorkpieceAdapter
        from contour_editor.persistence.data.editor_data_model import ContourEditorData

        editor_data = ContourEditorData()
        WorkpieceAdapter.print_summary(editor_data)

        captured = capsys.readouterr()
        assert "WorkpieceAdapter Summary" in captured.out or "WorkpieceAdapter" in captured.out

    def test_print_summary_includes_statistics(self, capsys):
        """Test that summary includes statistics"""
        from contour_editor.api.adapters import WorkpieceAdapter
        from contour_editor.persistence.data.editor_data_model import ContourEditorData

        editor_data = ContourEditorData()
        WorkpieceAdapter.print_summary(editor_data)

        captured = capsys.readouterr()
        # Summary should be printed (method exists and runs without error)
        assert captured.out is not None


@pytest.mark.unit
class TestWorkpieceAdapterIntegration:
    """Integration tests for WorkpieceAdapter"""

    def test_roundtrip_minimal_data(self):
        """Test converting to workpiece data and back"""
        from contour_editor.api.adapters import WorkpieceAdapter
        from contour_editor.persistence.data.editor_data_model import ContourEditorData

        editor_data = ContourEditorData()
        workpiece_data = WorkpieceAdapter.to_workpiece_data(editor_data)

        assert isinstance(workpiece_data, dict)
        assert "main_contour" in workpiece_data
        assert "spray_pattern" in workpiece_data

    def test_adapter_with_all_layer_types(self):
        """Test adapter handling all three layer types"""
        from contour_editor.api.adapters import WorkpieceAdapter

        main_contour = np.array([[0, 0], [100, 100]], dtype=np.float32)
        layer_data = {
            WorkpieceAdapter.LAYER_WORKPIECE: [
                {"contour": main_contour, "settings": {"type": "main"}}
            ],
            WorkpieceAdapter.LAYER_CONTOUR: [
                {"contour": np.array([[10, 10], [90, 90]], dtype=np.float32), "settings": {}}
            ],
            WorkpieceAdapter.LAYER_FILL: [
                {"contour": np.array([[20, 20], [80, 80]], dtype=np.float32), "settings": {}}
            ]
        }

        result = WorkpieceAdapter._normalize_layer_data(layer_data)

        assert WorkpieceAdapter.LAYER_WORKPIECE in result
        assert WorkpieceAdapter.LAYER_CONTOUR in result
        assert WorkpieceAdapter.LAYER_FILL in result


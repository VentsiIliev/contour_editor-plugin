import pytest
from PyQt6.QtCore import QPointF
from unittest.mock import Mock, MagicMock, patch
import numpy as np
from workpiece_editor.managers import WorkpieceManager
from contour_editor.models.segment import Segment, Layer
from contour_editor.persistence.data.editor_data_model import ContourEditorData
@pytest.fixture
def mock_editor():
    editor = Mock()
    editor.manager = Mock()
    editor.manager.segments = []
    editor.manager.external_layer = Layer("Main")
    editor.manager.contour_layer = Layer("Contour")
    editor.manager.fill_layer = Layer("Fill")
    editor.manager.get_segments.return_value = []
    editor.manager.clear_all_segments = Mock()
    editor.manager.contour_to_bezier = Mock(return_value=[])
    editor.update = Mock()
    editor.pointsUpdated = Mock()
    editor.pointsUpdated.emit = Mock()
    return editor
@pytest.fixture
def workpiece_manager(mock_editor):
    return WorkpieceManager(mock_editor)
class TestWorkpieceManagerInitialization:
    def test_initialization(self, workpiece_manager, mock_editor):
        assert workpiece_manager.editor == mock_editor
        assert workpiece_manager.current_workpiece is None
        assert workpiece_manager.contours is None
    def test_initialization_with_none_editor(self):
        manager = WorkpieceManager(None)
        assert manager.editor is None
class TestWorkpieceManagerLoadWorkpiece:
    def test_load_workpiece_basic(self, workpiece_manager):
        workpiece = Mock()
        workpiece.workpieceId = "123"
        with patch('workpiece_editor.managers.workpiece_manager.load_workpiece') as mock_load:
            mock_load.return_value = (workpiece, {"Main": []})
            result = workpiece_manager.load_workpiece(workpiece)
            assert result == workpiece
            assert workpiece_manager.current_workpiece == workpiece
    def test_load_workpiece_with_contours(self, workpiece_manager, mock_editor):
        workpiece = Mock()
        contours_by_layer = {
            "Main": [np.array([[10, 10], [100, 10]], dtype=np.float32)]
        }
        mock_editor.manager.contour_to_bezier.return_value = [Mock()]
        with patch('workpiece_editor.managers.workpiece_manager.load_workpiece') as mock_load:
            mock_load.return_value = (workpiece, contours_by_layer)
            workpiece_manager.load_workpiece(workpiece)
            assert workpiece_manager.current_workpiece == workpiece
class TestWorkpieceManagerInitContour:
    def test_init_contour_basic(self, workpiece_manager, mock_editor):
        contours_by_layer = {
            "Main": [np.array([[10, 10], [100, 10]], dtype=np.float32)]
        }
        mock_editor.manager.contour_to_bezier.return_value = [Mock()]
        workpiece_manager.init_contour(contours_by_layer)
        assert workpiece_manager.contours == contours_by_layer
        mock_editor.pointsUpdated.emit.assert_called()
    def test_init_contour_multiple_layers(self, workpiece_manager, mock_editor):
        contours_by_layer = {
            "Main": [np.array([[10, 10], [100, 10]], dtype=np.float32)],
            "Contour": [np.array([[20, 20], [80, 20]], dtype=np.float32)]
        }
        mock_editor.manager.contour_to_bezier.return_value = [Mock()]
        workpiece_manager.init_contour(contours_by_layer)
        assert workpiece_manager.contours == contours_by_layer
class TestWorkpieceManagerClearWorkpiece:
    def test_clear_workpiece(self, workpiece_manager):
        workpiece_manager.current_workpiece = Mock()
        workpiece_manager.contours = {"Main": [Mock()]}
        workpiece_manager.clear_workpiece()
        assert workpiece_manager.current_workpiece is None
        assert workpiece_manager.contours is None
class TestWorkpieceManagerSetCurrentWorkpiece:
    def test_set_current_workpiece(self, workpiece_manager):
        workpiece = Mock()
        workpiece_manager.set_current_workpiece(workpiece)
        assert workpiece_manager.current_workpiece == workpiece
    def test_get_current_workpiece(self, workpiece_manager):
        workpiece = Mock()
        workpiece_manager.current_workpiece = workpiece
        result = workpiece_manager.get_current_workpiece()
        assert result == workpiece
class TestWorkpieceManagerStatistics:
    def test_get_workpiece_statistics(self, workpiece_manager, mock_editor):
        workpiece_manager.current_workpiece = Mock()
        segment = Mock()
        segment.anchors = [Mock(), Mock(), Mock()]
        segment.layer = Layer("Main")
        mock_editor.manager.get_segments.return_value = [segment]
        stats = workpiece_manager.get_workpiece_statistics()
        assert stats is not None
        assert stats["total_segments"] == 1

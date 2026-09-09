from types import SimpleNamespace
from unittest.mock import MagicMock, call

from PyQt6.QtCore import QPointF

from contour_editor.ui.new_widgets.point_manager.list_builder import ListBuilder


def test_add_points_for_segment_omits_unset_control_points():
    builder = ListBuilder.__new__(ListBuilder)
    builder._add_point_item = MagicMock()
    segment = SimpleNamespace(
        points=[QPointF(1.0, 2.0), QPointF(3.0, 4.0)],
        controls=[None, QPointF(5.0, 6.0)],
    )

    builder._add_points_for_segment(7, segment)

    assert builder._add_point_item.call_args_list == [
        call("P0", "(1.0, 2.0)", 7, 0, "anchor"),
        call("P1", "(3.0, 4.0)", 7, 1, "anchor"),
        call("C1", "(5.0, 6.0)", 7, 1, "control"),
    ]

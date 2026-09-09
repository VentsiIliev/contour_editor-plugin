from types import SimpleNamespace
from unittest.mock import MagicMock

from PyQt6.QtCore import QPointF, Qt

from contour_editor.input.mouse_handler import MouseHandler


class _MouseEvent:
    def __init__(self, position, button=Qt.MouseButton.LeftButton):
        self._position = QPointF(position)
        self._button = button

    def position(self):
        return QPointF(self._position)

    def button(self):
        return self._button


def _make_handler(nearby_target=("anchor", 0, 0)):
    editor = SimpleNamespace(
        pickup_point_mode_active=False,
        press_hold_start_pos=None,
        point_info_timer=MagicMock(),
        _handle_add_control_point=MagicMock(return_value=False),
        manager=SimpleNamespace(add_point=MagicMock()),
        pointsUpdated=SimpleNamespace(emit=MagicMock()),
    )
    segments = MagicMock()
    segments.find_drag_targets.side_effect = [[], [nearby_target]]
    context = SimpleNamespace(
        widget=editor,
        overlay=SimpleNamespace(
            is_point_info_visible=lambda: False,
            is_segment_click_visible=lambda: False,
        ),
        viewport=SimpleNamespace(
            is_zooming=False,
            scale=1.0,
            screen_to_image=lambda point: QPointF(point),
        ),
        mode=SimpleNamespace(
            is_pan_active=False,
            is_ruler_active=False,
            is_rectangle_select_active=False,
            is_multi_select_active=False,
            drag=SimpleNamespace(mousePress=MagicMock(), mouseMove=MagicMock()),
        ),
        is_within_image=lambda _point: True,
        segments=segments,
        selection=SimpleNamespace(clear=MagicMock()),
        update=MagicMock(),
    )
    return MouseHandler(context), context


def test_nearby_point_is_dragged_after_pointer_moves():
    handler, context = _make_handler()
    handler.handle_press(_MouseEvent(QPointF(100, 100)))

    context.widget.manager.add_point.assert_not_called()
    handler.handle_move(_MouseEvent(QPointF(112, 100)))

    context.mode.drag.mousePress.assert_called_once()
    assert context.mode.drag.mousePress.call_args.args[2] == ("anchor", 0, 0)
    context.mode.drag.mouseMove.assert_called_once()
    context.widget.manager.add_point.assert_not_called()


def test_nearby_point_zone_still_adds_on_click_without_dragging():
    handler, context = _make_handler()
    handler.handle_press(_MouseEvent(QPointF(100, 100)))

    handler.handle_release(_MouseEvent(QPointF(100, 100)))

    context.widget._handle_add_control_point.assert_called_once_with(QPointF(100, 100))
    context.widget.manager.add_point.assert_called_once_with(QPointF(100, 100))

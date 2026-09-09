from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest
from PyQt6.QtCore import QPointF

from contour_editor.controllers.state.mode_handlers.rectangle_select_mode import (
    RectangleSelectMode,
)


@pytest.mark.parametrize(
    ("cursor", "expected_translation"),
    [
        (QPointF(25, 300), QPointF(10, 0)),
        (QPointF(775, 300), QPointF(-10, 0)),
        (QPointF(400, 25), QPointF(0, 10)),
        (QPointF(400, 575), QPointF(0, -10)),
        (QPointF(400, 300), QPointF(0, 0)),
    ],
)
def test_rectangle_drag_scrolls_at_viewport_edges(cursor, expected_translation):
    mode = RectangleSelectMode()
    mode.is_selecting = True
    mode.selection_start = QPointF(100, 100)
    editor = SimpleNamespace(
        translation=QPointF(0, 0),
        scale_factor=1.0,
        width=lambda: 800,
        height=lambda: 600,
        update=MagicMock(),
    )
    event = SimpleNamespace(position=lambda: cursor)

    mode.mouseMove(editor, event)

    assert editor.translation == expected_translation
    assert mode.selection_end == cursor
    editor.update.assert_called_once_with()

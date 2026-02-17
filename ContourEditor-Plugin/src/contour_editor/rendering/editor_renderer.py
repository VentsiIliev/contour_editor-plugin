from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPainter

from ..core.editor_context import EditorContext
from .segment_renderer import SegmentRenderer
from .renderer import (
    draw_ruler, draw_rectangle_selection, draw_pickup_point,
    draw_selection_status, draw_drag_crosshair,
    draw_highlighted_line_segment
)


class EditorRenderer:
    def __init__(self, editor):
        self.editor = editor
        self._context = EditorContext(editor)
        self._segment_renderer = SegmentRenderer(self._context)

    def render(self, painter, event):
        if not painter.isActive():
            return

        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.fillRect(self.editor.rect(), Qt.GlobalColor.white)
        
        painter.translate(self.editor.translation)
        painter.scale(self.editor.scale_factor, self.editor.scale_factor)
        painter.drawImage(0, 0, self.editor.image)

        draw_ruler(self.editor, painter)
        self._segment_renderer.render_all(painter)
        draw_rectangle_selection(self.editor, painter)
        draw_pickup_point(self.editor, painter)
        draw_selection_status(self.editor, painter)

        if self.editor.highlighted_line_segment:
            draw_highlighted_line_segment(self.editor, painter)

        painter.resetTransform()

        if (hasattr(self.editor.mode_manager, 'drag_mode') and
            self.editor.mode_manager.drag_mode.is_actually_dragging and 
            self.editor.current_cursor_pos is not None):
            draw_drag_crosshair(self.editor, painter, self.editor.current_cursor_pos)
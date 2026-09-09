from dataclasses import dataclass
from enum import Enum
from typing import FrozenSet


class EditorButton(str, Enum):
    UNDO = "undo"
    REDO = "redo"
    TOOLS = "tools"
    SETTINGS = "settings"
    CAPTURE = "capture"
    REMOVE = "remove"
    PICKUP = "pickup"
    PREVIEW = "preview"
    GENERATE_PATTERN = "generate_pattern"
    START = "start"
    SAVE = "save"
    POINT_VISIBILITY = "point_visibility"
    ZOOM_OUT = "zoom_out"
    RESET_ZOOM = "reset_zoom"
    ZOOM_IN = "zoom_in"
    PAN = "pan"


@dataclass(frozen=True)
class ContourEditorUiConfig:
    """Controls which optional editor toolbar buttons are presented to users."""

    hidden_buttons: FrozenSet[EditorButton] = frozenset()

    @classmethod
    def hide(cls, *buttons: EditorButton) -> "ContourEditorUiConfig":
        return cls(hidden_buttons=frozenset(buttons))

    def is_visible(self, button: EditorButton) -> bool:
        return button not in self.hidden_buttons

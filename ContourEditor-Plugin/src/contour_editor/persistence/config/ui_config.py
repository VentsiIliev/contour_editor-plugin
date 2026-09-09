from dataclasses import dataclass
from enum import Enum
from typing import FrozenSet, Tuple


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


class ToolbarPlacement(str, Enum):
    TOP_LEFT = "top_left"
    TOP_CENTER = "top_center"
    TOP_RIGHT = "top_right"
    BOTTOM = "bottom"


@dataclass(frozen=True)
class CustomEditorButtonSpec:
    action_id: str
    icon_name: str
    tooltip: str = ""
    placement: ToolbarPlacement = ToolbarPlacement.TOP_CENTER
    primary: bool = False


@dataclass(frozen=True)
class ContourEditorUiConfig:
    """Controls which optional editor toolbar buttons are presented to users."""

    hidden_buttons: FrozenSet[EditorButton] = frozenset()
    custom_buttons: Tuple[CustomEditorButtonSpec, ...] = ()

    @classmethod
    def hide(cls, *buttons: EditorButton) -> "ContourEditorUiConfig":
        return cls(hidden_buttons=frozenset(buttons))

    def is_visible(self, button: EditorButton) -> bool:
        return button not in self.hidden_buttons

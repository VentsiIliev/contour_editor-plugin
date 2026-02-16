"""
Commands Package - Command pattern implementation for undo/redo support
All editor operations should be wrapped in Command objects to enable
proper undo/redo functionality and better state tracking.
"""
from .base_command import Command
from .command_history import CommandHistory
from .segment_commands import (
    AddSegmentCommand,
    DeleteSegmentCommand,
    ToggleSegmentVisibilityCommand,
    ChangeSegmentLayerCommand
)
__all__ = [
    'Command',
    'CommandHistory',
    'AddSegmentCommand',
    'DeleteSegmentCommand',
    'ToggleSegmentVisibilityCommand',
    'ChangeSegmentLayerCommand',
]

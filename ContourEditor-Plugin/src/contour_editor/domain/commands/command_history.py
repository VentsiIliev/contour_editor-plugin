"""
Command History - Manages undo/redo stack

Singleton pattern: use CommandHistory.get_instance() for the shared history.
"""
from typing import List, Optional
from .base_command import Command
class CommandHistory:
    """
    Manages the history of executed commands for undo/redo functionality.

    Usage:
        # Get the shared singleton instance
        history = CommandHistory.get_instance()
        history.execute(command)  # Execute and add to history
        history.undo()  # Undo last command
        history.redo()  # Redo last undone command
    """

    _instance = None

    def __init__(self, max_history=100):
        """
        Initialize command history.
        Args:
            max_history: Maximum number of commands to keep in history
        """
        self._undo_stack: List[Command] = []
        self._redo_stack: List[Command] = []
        self._max_history = max_history

    @classmethod
    def get_instance(cls):
        """Get the singleton instance of CommandHistory"""
        if cls._instance is None:
            cls._instance = CommandHistory()
        return cls._instance

    @classmethod
    def reset_instance(cls):
        """Reset the singleton (useful for testing)"""
        cls._instance = None
    def execute(self, command: Command):
        """
        Execute a command and add it to the undo stack.
        Args:
            command: Command to execute
        """
        command.execute()
        # Check if we can merge with the previous command
        if self._undo_stack and self._undo_stack[-1].can_merge_with(command):
            self._undo_stack[-1].merge_with(command)
        else:
            self._undo_stack.append(command)
            # Limit history size
            if len(self._undo_stack) > self._max_history:
                self._undo_stack.pop(0)
        # Clear redo stack when new command is executed
        self._redo_stack.clear()
    def undo(self) -> bool:
        """
        Undo the last command.
        Returns:
            bool: True if undo was successful, False if nothing to undo
        """
        if not self._undo_stack:
            return False
        command = self._undo_stack.pop()
        command.undo()
        self._redo_stack.append(command)
        return True
    def redo(self) -> bool:
        """
        Redo the last undone command.
        Returns:
            bool: True if redo was successful, False if nothing to redo
        """
        if not self._redo_stack:
            return False
        command = self._redo_stack.pop()
        command.execute()
        self._undo_stack.append(command)
        return True
    def can_undo(self) -> bool:
        """Check if undo is available"""
        return len(self._undo_stack) > 0
    def can_redo(self) -> bool:
        """Check if redo is available"""
        return len(self._redo_stack) > 0
    def get_undo_description(self) -> Optional[str]:
        """Get description of the command that would be undone"""
        if self._undo_stack:
            return self._undo_stack[-1].get_description()
        return None
    def get_redo_description(self) -> Optional[str]:
        """Get description of the command that would be redone"""
        if self._redo_stack:
            return self._redo_stack[-1].get_description()
        return None
    def clear(self):
        """Clear all history"""
        self._undo_stack.clear()
        self._redo_stack.clear()
    def get_history_size(self) -> int:
        """Get the number of commands in undo history"""
        return len(self._undo_stack)

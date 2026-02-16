"""
Base Command - Abstract base class for all commands
"""
from abc import ABC, abstractmethod
class Command(ABC):
    """
    Abstract base class for all commands.
    Commands encapsulate operations that can be executed and undone,
    enabling proper undo/redo functionality throughout the application.
    """
    def __init__(self):
        self._executed = False
    @abstractmethod
    def execute(self):
        """
        Execute the command.
        This method should perform the actual operation and emit
        appropriate events via the EventBus.
        """
        pass
    @abstractmethod
    def undo(self):
        """
        Undo the command.
        This method should reverse the operation performed by execute()
        and emit appropriate events via the EventBus.
        """
        pass
    @abstractmethod
    def get_description(self):
        """
        Get a human-readable description of this command.
        Returns:
            str: Description of the command (e.g., "Toggle visibility of segment 0")
        """
        pass
    def can_merge_with(self, other):
        """
        Check if this command can be merged with another command.
        This is useful for operations like dragging, where multiple
        small movements can be merged into a single undo step.
        Args:
            other: Another Command instance
        Returns:
            bool: True if commands can be merged
        """
        return False
    def merge_with(self, other):
        """
        Merge this command with another command.
        Args:
            other: Another Command instance to merge with
        """
        raise NotImplementedError("This command does not support merging")

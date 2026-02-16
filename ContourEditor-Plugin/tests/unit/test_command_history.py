"""
Tests for CommandHistory.
This module tests:
- Singleton pattern
- Command execution
- Undo/redo functionality  
- Stack management
- Error handling
"""
import pytest
from unittest.mock import Mock
def test_command_history_singleton(mock_command_history):
    """Test that CommandHistory follows singleton pattern."""
    from contour_editor.commands.command_history import CommandHistory
    history1 = CommandHistory.get_instance()
    history2 = CommandHistory.get_instance()
    assert history1 is history2
def test_execute_command(mock_command_history):
    """Test command execution."""
    mock_command = Mock()
    mock_command.execute = Mock()
    mock_command.can_merge_with = Mock(return_value=False)
    mock_command_history.execute(mock_command)
    mock_command.execute.assert_called_once()
    assert mock_command_history.can_undo()
def test_undo_single_command(mock_command_history):
    """Test single undo operation."""
    mock_command = Mock()
    mock_command.execute = Mock()
    mock_command.undo = Mock()
    mock_command.can_merge_with = Mock(return_value=False)
    mock_command_history.execute(mock_command)
    result = mock_command_history.undo()
    assert result is True
    mock_command.undo.assert_called_once()
def test_redo_single_command(mock_command_history):
    """Test single redo operation."""
    mock_command = Mock()
    mock_command.execute = Mock()
    mock_command.undo = Mock()
    mock_command.can_merge_with = Mock(return_value=False)
    mock_command_history.execute(mock_command)
    mock_command_history.undo()
    result = mock_command_history.redo()
    assert result is True
    # redo() calls execute() again
    assert mock_command.execute.call_count == 2
def test_undo_multiple_commands(mock_command_history):
    """Test undo with multiple commands."""
    commands = []
    for i in range(3):
        cmd = Mock()
        cmd.execute = Mock()
        cmd.undo = Mock()
        cmd.can_merge_with = Mock(return_value=False)
        commands.append(cmd)
        mock_command_history.execute(cmd)
    # Undo all three
    mock_command_history.undo()
    mock_command_history.undo()
    mock_command_history.undo()
    # All should be undone
    for cmd in commands:
        cmd.undo.assert_called_once()
def test_redo_multiple_commands(mock_command_history):
    """Test redo with multiple commands."""
    commands = []
    for i in range(3):
        cmd = Mock()
        cmd.execute = Mock()
        cmd.undo = Mock()
        cmd.can_merge_with = Mock(return_value=False)
        commands.append(cmd)
        mock_command_history.execute(cmd)
    # Undo all
    for _ in range(3):
        mock_command_history.undo()
    # Redo all
    for _ in range(3):
        mock_command_history.redo()
    # execute() is called twice per command (initial + redo)
    for cmd in commands:
        assert cmd.execute.call_count == 2
def test_can_undo(mock_command_history):
    """Test can_undo state tracking."""
    assert not mock_command_history.can_undo()
    mock_command = Mock()
    mock_command.execute = Mock()
    mock_command.can_merge_with = Mock(return_value=False)
    mock_command_history.execute(mock_command)
    assert mock_command_history.can_undo()
    mock_command.undo = Mock()
    mock_command_history.undo()
    assert not mock_command_history.can_undo()
def test_can_redo(mock_command_history):
    """Test can_redo state tracking."""
    assert not mock_command_history.can_redo()
    mock_command = Mock()
    mock_command.execute = Mock()
    mock_command.undo = Mock()
    mock_command.can_merge_with = Mock(return_value=False)
    mock_command_history.execute(mock_command)
    assert not mock_command_history.can_redo()
    mock_command_history.undo()
    assert mock_command_history.can_redo()
def test_clear_history(mock_command_history):
    """Test clearing command history."""
    commands = []
    for i in range(3):
        cmd = Mock()
        cmd.execute = Mock()
        cmd.can_merge_with = Mock(return_value=False)
        commands.append(cmd)
        mock_command_history.execute(cmd)
    assert mock_command_history.can_undo()
    mock_command_history.clear()
    assert not mock_command_history.can_undo()
    assert not mock_command_history.can_redo()
def test_execute_clears_redo_stack(mock_command_history):
    """Test that executing a new command clears the redo stack."""
    cmd1 = Mock()
    cmd1.execute = Mock()
    cmd1.undo = Mock()
    cmd1.can_merge_with = Mock(return_value=False)
    cmd2 = Mock()
    cmd2.execute = Mock()
    cmd2.can_merge_with = Mock(return_value=False)
    # Execute, undo, then execute new command
    mock_command_history.execute(cmd1)
    mock_command_history.undo()
    assert mock_command_history.can_redo()
    mock_command_history.execute(cmd2)
    # Redo stack should be cleared
    assert not mock_command_history.can_redo()
def test_command_execution_failure(mock_command_history):
    """Test handling of command execution failure."""
    mock_command = Mock()
    mock_command.execute = Mock(side_effect=Exception("Test error"))
    mock_command.can_merge_with = Mock(return_value=False)
    # Should raise the exception
    with pytest.raises(Exception, match="Test error"):
        mock_command_history.execute(mock_command)
    # Command should not be in history (execute failed before adding)
    assert not mock_command_history.can_undo()

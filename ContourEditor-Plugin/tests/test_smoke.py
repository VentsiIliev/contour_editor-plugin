"""Smoke test to verify test infrastructure is working."""
def test_smoke():
    """Simple smoke test to verify pytest is working."""
    assert True

def test_imports():
    """Test that we can import our modules."""
    from contour_editor.core.event_bus import EventBus
    from contour_editor.services.commands.command_history import CommandHistory
    assert EventBus is not None
    assert CommandHistory is not None

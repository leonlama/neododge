import pytest
import arcade
from unittest.mock import MagicMock, patch

@pytest.fixture(scope="function")
def setup_arcade_window():
    """Fixture to set up an actual arcade window when needed."""
    try:
        arcade.get_window()
    except RuntimeError:
        arcade.open_window(800, 600, "Test Window")
    yield
    try:
        window = arcade.get_window()
        if window:
            window.close()
    except RuntimeError:
        pass  # Ignore if the window is already closed

@pytest.fixture(scope="function", autouse=True)
def mock_arcade_window():
    """Mock arcade window for headless test environments.
    This prevents 'No window is active' errors in CI environments.
    """
    with patch('arcade.get_window', return_value=MagicMock()):
        yield
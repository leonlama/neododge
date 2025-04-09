import pytest
import arcade

@pytest.fixture(scope="function", autouse=True)
def setup_arcade_window():
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
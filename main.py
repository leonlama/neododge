import arcade
import arcade.gl
import array

# Views
from src.views.start_view import StartView

# Utilities
from src.core.constants import SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE
from src.core.resource_manager import resource_path
from src.skins.skin_manager import skin_manager

def preload_all_skins():
    # Initialize skin manager
    skin_manager.load_skins()
    skin_manager.select("default")

def main():
    window = arcade.Window(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    preload_all_skins()
    start_view = StartView()
    window.show_view(start_view)
    arcade.run()

if __name__ == "__main__":
    main()

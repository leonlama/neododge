import arcade
import os
import appdirs
from src.views.start_view import StartView
from src.core.constants import SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE
from src.skins.skin_manager import skin_manager

def main():
    """Main function to start the game"""
    # Create the game window
    window = arcade.Window(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    
    # Load UI textures
    skin_manager.load_ui_textures()

    # Create and show the start view
    start_view = StartView()
    window.show_view(start_view)

    # Run the arcade loop
    arcade.run()

if __name__ == "__main__":
    main()
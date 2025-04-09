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
    
    # Initialize UI textures dictionary if it doesn't exist
    if "ui" not in skin_manager.textures:
        skin_manager.textures["ui"] = {}
    
    # Load UI textures
    skin_manager.load_ui_textures()
    
    # Confirm UI textures were loaded correctly
    print("✅ UI Texture Keys:", skin_manager.textures["ui"].keys())
    
    # Test getting a texture
    heart_texture = skin_manager.get_texture("ui", "heart_red")
    if heart_texture:
        print("🎯 Successfully retrieved heart_red texture")
    else:
        print("❌ Failed to retrieve heart_red texture")

    # Create and show the start view
    start_view = StartView()
    window.show_view(start_view)

    # Run the arcade loop
    arcade.run()

if __name__ == "__main__":
    main()
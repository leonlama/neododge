import arcade
import arcade.gl
from scripts.views.start_view import StartView
from scripts.utils.constants import SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE
from scripts.skins.skin_manager import skin_manager

def main():
    """
    Main function to start the game.
    """
    # Create the game window
    window = arcade.Window(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)

    # Attach skin manager to window
    window.skin_manager = skin_manager
    print(f"Using skin manager class: {type(window.skin_manager).__name__}")

    # Unlock all skins for testing
    _unlock_all_skins(window.skin_manager)

    # Preload assets
    _preload_assets(window.skin_manager)

    # Start with the start view
    start_view = StartView()
    window.show_view(start_view)

    # Run the game
    arcade.run()

def _unlock_all_skins(skin_manager):
    """
    Unlock all skins for testing purposes.

    Args:
        skin_manager: The skin manager instance
    """
    # Make sure mdma skin is unlocked
    if "mdma" not in skin_manager.data["unlocked"]:
        skin_manager.data["unlocked"].append("mdma")
        skin_manager.save()

def _preload_assets(skin_manager):
    """
    Preload assets for all skins.

    Args:
        skin_manager: The skin manager instance
    """
    try:
        # Preload player textures
        for skin in skin_manager.data["unlocked"]:
            skin_manager.data["selected"] = skin
            skin_manager.get_texture("player", "player")

        # Reset to default skin
        skin_manager.data["selected"] = "default"
        print("✅ All assets preloaded successfully")
    except Exception as e:
        print(f"❌ Error preloading assets: {e}")

if __name__ == "__main__":
    main()
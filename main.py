import arcade
from src.views.start_view import StartView
from src.core.constants import SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE
from src.skins.skin_manager import skin_manager

def preload_all_skins():
    """Preload all skin assets to avoid lag during gameplay"""
    print("Preloading skin assets...")

    # Create a sprite list for preloading
    preload_list = arcade.SpriteList()

    # Preload player textures for all skins
    for skin_name in skin_manager.skin_data:
        try:
            # Get player texture path
            player_path = skin_manager.skin_data[skin_name].get("player")
            if player_path and arcade.os.path.exists(player_path):
                texture = arcade.load_texture(player_path)
                scale = skin_manager.skin_data[skin_name].get("scale", 0.5)
                sprite = arcade.Sprite(texture=texture, center_x=-9999, center_y=-9999, scale=scale)
                preload_list.append(sprite)
        except Exception as e:
            print(f"Error preloading skin {skin_name}: {e}")

    # Preload UI elements
    ui_elements = ["heart_red.png", "heart_gray.png", "heart_gold.png"]
    for element in ui_elements:
        try:
            path = f"assets/ui/{element}"
            if arcade.os.path.exists(path):
                texture = arcade.load_texture(path)
                sprite = arcade.Sprite(texture=texture, center_x=-9999, center_y=-9999)
                preload_list.append(sprite)
        except Exception:
            pass

    # Draw the list once (off-screen) to load into GPU memory
    with arcade.get_window().ctx.pyglet_rendering():
        preload_list.draw()

    # Clear the preload list from memory
    preload_list = None
    print("✅ All assets preloaded successfully")

def main():
    """Main function to start the game"""
    window = arcade.Window(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    preload_all_skins()
    start_view = StartView()
    window.show_view(start_view)
    arcade.run()

if __name__ == "__main__":
    main()
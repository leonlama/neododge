import arcade
import arcade.gl
import array

# Views
from scripts.views.start_view import StartView

# Utilities
from scripts.utils.constants import SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE, DEFAULT_SKIN_PATH, MDMA_SKIN_PATH
from scripts.utils.resource_helper import resource_path
from scripts.skins.skin_manager import skin_manager

def preload_all_skins():
    preload_list = arcade.SpriteList()

    # Preload all skins (default and mdma)
    for skin_name in ["default", "mdma"]:
        # Temporarily switch skin for preloading
        original_skin = skin_manager.data["selected"]
        skin_manager.select(skin_name)
        
        # Preload all categories and common asset types
        categories = ["orbs", "hearts", "artifacts", "coins", "bullets", "enemies", "player"]
        asset_types = ["cooldown", "shield", "speed", "health", "damage", "gold", "dash", 
                      "magnet", "slow", "bullet_time", "clone"]
        
        for category in categories:
            for asset_type in asset_types:
                try:
                    texture = skin_manager.get_texture(category, asset_type)
                    # Get appropriate scale based on category
                    if category == "orbs":
                        scale = skin_manager.get_orb_scale()
                    elif category == "hearts":
                        scale = skin_manager.get_heart_scale()
                    elif category == "artifacts":
                        scale = skin_manager.get_artifact_scale()
                    else:
                        scale = 1.0
                    sprite = arcade.Sprite(texture=texture, center_x=-9999, center_y=-9999, scale=scale)
                    preload_list.append(sprite)
                except Exception:
                    # Skip if texture not found
                    continue
        
        # Restore original skin
        skin_manager.select(original_skin)
    
    # Preload all orb types
    orb_types = ["speed", "shield", "cooldown", "multiplier", "vision", "hitbox"]
    for orb_type in orb_types:
        try:
            # Load orb texture using skin manager
            path = resource_path(skin_manager.get_texture_path("orbs", orb_type))
            if arcade.os.path.exists(path):
                texture = arcade.load_texture(path)
                scale = skin_manager.get_orb_scale()
                sprite = arcade.Sprite(texture=texture, center_x=-9999, center_y=-9999, scale=scale)
                preload_list.append(sprite)
        except Exception:
            continue
    
    # Preload all artifact types
    artifact_types = ["dash", "magnet", "slow", "bullet_time", "clone"]
    for artifact_type in artifact_types:
        try:
            path = resource_path(skin_manager.get_texture_path("artifacts", artifact_type))
            if arcade.os.path.exists(path):
                texture = arcade.load_texture(path)
                scale = skin_manager.get_artifact_scale()
                sprite = arcade.Sprite(texture=texture, center_x=-9999, center_y=-9999, scale=scale)
                preload_list.append(sprite)
        except Exception:
            continue
    
    # Preload coin animations
    for i in range(1, 9):  # Assuming 8 frames for coin animation
        try:
            path = resource_path(f"assets/coins/coin_{i}.png")
            if arcade.os.path.exists(path):
                texture = arcade.load_texture(path)
                sprite = arcade.Sprite(texture=texture, center_x=-9999, center_y=-9999)
                preload_list.append(sprite)
        except Exception:
            continue

    # Preload sound effects
    sounds = ["buff.wav", "debuff.wav", "coin.flac", "damage.wav"]
    for sound in sounds:
        try:
            arcade.load_sound(resource_path(f"assets/audio/{sound}"))
        except Exception:
            continue

    # Draw the list once (off-screen)
    with arcade.get_window().ctx.pyglet_rendering():
        preload_list.draw()

    # Clear the preload list from memory
    preload_list = None
    print("✅ All assets preloaded successfully")


def main():
    window = arcade.Window(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    preload_all_skins()
    start_view = StartView()
    window.show_view(start_view)
    arcade.run()


if __name__ == "__main__":
    main()

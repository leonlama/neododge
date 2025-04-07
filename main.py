import arcade
import arcade.gl
import array

# Views
from scripts.views.start_view import StartView

# Utilities
from scripts.utils.constants import SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE, ARTIFACT_SCALE, SKINS_DIR
from scripts.utils.resource_helper import resource_path
from scripts.skins.skin_manager import skin_manager

class GameWindow(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
        
        # Unlock all skins for testing
        if "mdma" not in skin_manager.data["unlocked"]:
            skin_manager.data["unlocked"].append("mdma")
            if hasattr(skin_manager, 'save'):
                skin_manager.save()
        
        print(f"🎨 [INIT] Using skin: {skin_manager.current_skin}")
        print(f"Using skin manager class: {type(skin_manager).__name__}")
        self.preload_all_skins()

    def preload_all_skins(self):
        preload_list = arcade.SpriteList()

        # Preload all skins (default and mdma)
        for skin_name in ["default", "mdma"]:
            # Temporarily switch skin for preloading
            original_skin = skin_manager.current_skin
            skin_manager.select(skin_name)
            
            # Preload all categories and common asset types
            categories = ["orbs", "hearts", "artifacts", "coins", "bullets", "enemies", "player"]
            asset_types = ["cooldown", "shield", "speed", "health", "damage", "gold", "dash", 
                          "magnet", "slow", "bullet_time", "clone"]
            
            for category in categories:
                for asset_type in asset_types:
                    try:
                        texture = skin_manager.get_asset(category, asset_type)
                        # Get appropriate scale based on category
                        if category == "orbs":
                            scale = 0.5  # Example scale, adjust as needed
                        elif category == "hearts":
                            scale = 0.5  # Example scale, adjust as needed
                        elif category == "artifacts":
                            scale = ARTIFACT_SCALE
                        else:
                            scale = 1.0
                        sprite = arcade.Sprite(texture=texture, center_x=-9999, center_y=-9999, scale=scale)
                        preload_list.append(sprite)
                    except Exception:
                        # Skip if texture not found
                        continue
            
            # Restore original skin
            skin_manager.select(original_skin)
        
        # Preload sound effects
        sounds = ["buff.wav", "debuff.wav", "coin.flac", "damage.wav"]
        for sound in sounds:
            try:
                arcade.load_sound(resource_path(f"assets/audio/{sound}"))
            except Exception:
                continue

        # Draw the list once (off-screen)
        with self.ctx.pyglet_rendering():
            preload_list.draw()

        # Clear the preload list from memory
        preload_list = None
        print("✅ All assets preloaded successfully")


def main():
    window = GameWindow()
    start_view = StartView()
    window.show_view(start_view)
    arcade.run()


if __name__ == "__main__":
    main()

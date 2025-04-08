# src/skins/skin_manager.py

import json
import os
import arcade
import appdirs

# Define app-specific user data dir
APP_NAME = "Neododge"
USER_DATA_DIR = os.path.join(appdirs.user_data_dir(APP_NAME), "data")
os.makedirs(USER_DATA_DIR, exist_ok=True)

# Cross-platform safe JSON file location
UNLOCKS_FILE = os.path.join(USER_DATA_DIR, "unlocks.json")

class SkinManager:
    def __init__(self):
        print("🎨 [INIT] Initializing skin manager")
        self.skin_data = {
            "default": {
                "path": "assets/skins/default",
                "name": "Default",
                "description": "The default skin"
            },
            "mdma": {
                "path": "assets/skins/mdma",
                "name": "MDMA",
                "description": "Psychedelic skin"
            }
        }

        # Load unlocked skins from file
        self.load_unlocks()

        # Set default skin
        self.current_skin = "default"
        print(f"🎨 [INIT] Using skin: {self.current_skin}")

        # Preload assets
        self.preload_assets()

    def load_unlocks(self):
        """Load unlocked skins from file"""
        try:
            if os.path.exists(UNLOCKS_FILE):
                with open(UNLOCKS_FILE, 'r') as f:
                    self.data = json.load(f)
            else:
                # Default unlocks
                self.data = {
                    "unlocked": ["default", "mdma"]
                }
                # Save default unlocks
                self.save_unlocks()
        except Exception as e:
            print(f"⚠️ Error loading unlocks: {e}")
            self.data = {
                "unlocked": ["default"]
            }

    def save_unlocks(self):
        """Save unlocked skins to file"""
        try:
            with open(UNLOCKS_FILE, 'w') as f:
                json.dump(self.data, f)
        except Exception as e:
            print(f"⚠️ Error saving unlocks: {e}")

    def get_selected(self):
        """Get the currently selected skin"""
        return self.current_skin

    def set_skin(self, skin_name):
        """Set the current skin by name"""
        if skin_name in self.skin_data:
            self.current_skin = skin_name
            print(f"🎨 Skin set to: {skin_name}")
            return True
        else:
            print(f"⚠️ Skin '{skin_name}' not found")
            return False

    def unlock(self, skin_name):
        """Unlock a skin"""
        if skin_name in self.skin_data and skin_name not in self.data["unlocked"]:
            self.data["unlocked"].append(skin_name)
            self.save_unlocks()
            return True
        return False

    def preload_assets(self):
        """Preload all skin assets to avoid loading during gameplay"""
        print("Preloading skin assets...")
        try:
            # Preload all skin textures
            for skin_name, skin_info in self.skin_data.items():
                # Preload player texture
                self.get_texture("player", skin_name=skin_name)

                # Preload orb textures
                for orb_type in ["speed", "shield", "multiplier", "cooldown", "hitbox", "vision"]:
                    self.get_texture(f"orbs/{orb_type}", skin_name=skin_name)

                # Preload artifact textures
                for artifact_type in ["dash", "magnet", "slow", "bullet_time", "clone"]:
                    self.get_texture(f"artifacts/{artifact_type}", skin_name=skin_name)

            print("✅ All assets preloaded successfully")
        except Exception as e:
            print(f"⚠️ Error preloading assets: {e}")

    def get_texture(self, texture_name, fallback_path=None, skin_name=None):
        """Get a texture by name, with optional fallback path"""
        # Use specified skin or current skin
        skin = skin_name if skin_name else self.current_skin

        if skin in self.skin_data:
            skin_path = self.skin_data[skin]["path"]

            # Determine the texture path based on the texture name
            if texture_name == "player":
                texture_path = f"{skin_path}/player/default.png"
            elif texture_name == "heart_red":
                texture_path = "assets/ui/heart_red.png"
            elif texture_name == "heart_gray":
                texture_path = "assets/ui/heart_gray.png"
            elif texture_name == "heart_gold":
                texture_path = "assets/ui/heart_gold.png"
            elif "/" in texture_name:
                # For paths like "orbs/speed"
                texture_path = f"{skin_path}/{texture_name}.png"
            else:
                # For other textures, use a generic approach
                texture_path = f"{skin_path}/{texture_name}.png"

            try:
                return arcade.load_texture(texture_path)
            except Exception as e:
                print(f"⚠️ Error loading texture '{texture_name}' from '{texture_path}': {e}")

                # Try fallback path if provided
                if fallback_path:
                    try:
                        return arcade.load_texture(fallback_path)
                    except Exception as e2:
                        print(f"⚠️ Error loading fallback texture from '{fallback_path}': {e2}")

                # Return a placeholder texture
                return arcade.make_soft_square_texture(32, arcade.color.PURPLE, outer_alpha=255)
        else:
            print(f"⚠️ Skin '{skin}' not found")

            # Try fallback path if provided
            if fallback_path:
                try:
                    return arcade.load_texture(fallback_path)
                except Exception as e:
                    print(f"⚠️ Error loading fallback texture from '{fallback_path}': {e}")

            # Return a placeholder texture
            return arcade.make_soft_square_texture(32, arcade.color.PURPLE, outer_alpha=255)

    def get_orb_scale(self):
        """Get the scale for orbs based on the current skin"""
        return 0.5  # Default scale for all skins

# Global instance (singleton)
skin_manager = SkinManager()
# src/skins/skin_manager.py

import arcade
import os
import json
from src.core.resource_manager import load_texture

class SkinManager:
    """Manages game skins and textures."""

    def __init__(self):
        """Initialize the skin manager."""
        self.current_skin = "default"
        self.skins_path = "assets/skins"
        self.textures = {}
        self.scales = {
            "player": 1.0,
            "enemy": 1.0,
            "bullet": 1.0,
            "orb": 1.0,
            "artifact": 1.0,
            "coin": 1.0
        }

        # Create default textures for fallbacks
        self.create_default_textures()

        # Discover available skins
        self.skin_data = self.discover_skins()

        # Load skin settings
        self.load_skin(self.current_skin)
        print(f"🎨 [INIT] Initializing skin manager")
        print(f"🎨 [INIT] Using skin: {self.current_skin}")

    def create_default_textures(self):
        """Create default textures for fallbacks."""
        self.default_textures = {
            # UI elements
            "ui/background": arcade.make_soft_circle_texture(
                800, (20, 20, 40), outer_alpha=255, center_alpha=200
            ),
            "ui/logo": arcade.make_soft_square_texture(
                200, (255, 255, 255), center_alpha=255
            ),
            "ui/start_button": arcade.make_soft_square_texture(
                100, (0, 100, 200), center_alpha=200
            ),
            "ui/options_button": arcade.make_soft_square_texture(
                100, (0, 150, 0), center_alpha=200
            ),
            "ui/quit_button": arcade.make_soft_square_texture(
                100, (200, 0, 0), center_alpha=200
            ),
            "ui/heart": arcade.make_soft_circle_texture(
                30, (255, 0, 0), center_alpha=255
            ),
            "ui/shield": arcade.make_soft_circle_texture(
                30, (0, 100, 255), center_alpha=255
            ),

            # Player textures
            "player/idle": arcade.make_soft_circle_texture(
                30, (0, 150, 255), center_alpha=255
            ),
            "player/dash": arcade.make_soft_circle_texture(
                30, (100, 200, 255), center_alpha=255
            ),
            "player/default": arcade.make_soft_circle_texture(
                30, (0, 150, 255), center_alpha=255
            ),

            # Orb textures
            "orbs/speed": arcade.make_soft_circle_texture(
                30, (0, 255, 0), center_alpha=255
            ),
            "orbs/shield": arcade.make_soft_circle_texture(
                30, (0, 200, 255), center_alpha=255
            ),
            "orbs/health": arcade.make_soft_circle_texture(
                30, (255, 0, 0), center_alpha=255
            ),
            "orbs/cooldown": arcade.make_soft_circle_texture(
                30, (255, 255, 0), center_alpha=255
            ),
            "orbs/slow": arcade.make_soft_circle_texture(
                30, (255, 0, 0), center_alpha=255
            ),
            "orbs/damage": arcade.make_soft_circle_texture(
                30, (255, 100, 0), center_alpha=255
            ),
            "orbs/vision": arcade.make_soft_circle_texture(
                30, (100, 0, 100), center_alpha=255
            ),
            "orbs/hitbox": arcade.make_soft_circle_texture(
                30, (255, 100, 100), center_alpha=255
            ),
            "orbs/multiplier": arcade.make_soft_circle_texture(
                30, (255, 255, 0), center_alpha=255
            ),

            # Artifact textures
            "artifacts/dash": arcade.make_soft_circle_texture(
                30, (0, 100, 255), center_alpha=255
            ),
            "artifacts/clone": arcade.make_soft_circle_texture(
                30, (100, 0, 255), center_alpha=255
            ),
            "artifacts/bullet_time": arcade.make_soft_circle_texture(
                30, (255, 255, 0), center_alpha=255
            ),
            "artifacts/magnet": arcade.make_soft_circle_texture(
                30, (255, 100, 0), center_alpha=255
            ),
            "artifacts/slow": arcade.make_soft_circle_texture(
                30, (0, 255, 255), center_alpha=255
            )
        }

    def discover_skins(self):
        """Discover available skins in the skins directory.

        Returns:
            dict: Dictionary of skin names and their metadata.
        """
        skins = {}

        # Check if skins directory exists
        if not os.path.exists(self.skins_path):
            print(f"⚠️ Skins directory not found: {self.skins_path}")
            return {"default": {"name": "Default", "description": "Default skin"}}

        # List all subdirectories in the skins directory
        for skin_dir in os.listdir(self.skins_path):
            skin_path = os.path.join(self.skins_path, skin_dir)

            # Skip if not a directory or if it's a special file
            if not os.path.isdir(skin_path) or skin_dir.startswith("__"):
                continue

            # Add skin with default metadata
            skins[skin_dir] = {
                "name": skin_dir.capitalize(),
                "description": f"{skin_dir.capitalize()} skin",
                "path": skin_path
            }

        # If no skins were found, add at least the default
        if not skins:
            skins["default"] = {
                "name": "Default",
                "description": "Default skin",
                "path": os.path.join(self.skins_path, "default")
            }

        return skins

    def get_available_skins(self):
        """Get a list of available skin names.

        Returns:
            list: List of skin names.
        """
        return list(self.skin_data.keys())

    def load_skin(self, skin_name):
        """Load a skin by name.

        Args:
            skin_name: Name of the skin to load.
        """
        # Default to "default" if the requested skin doesn't exist
        if skin_name not in self.skin_data:
            print(f"⚠️ Skin '{skin_name}' not found, using default")
            skin_name = "default"

        self.current_skin = skin_name
        self.textures = {}

        # Preload textures
        self.preload_textures()

    def preload_textures(self):
        """Preload all textures for the current skin."""
        print("Preloading skin assets...")

        # Define categories and their items based on your actual asset structure
        categories = {
            "player": ["default"],
            "orbs": ["speed", "shield", "cooldown", "hitbox", "multiplier", "vision"],
            "artifacts": ["dash", "clone", "bullet_time", "magnet", "slow"]
        }

        # Preload all textures
        for category, items in categories.items():
            for item in items:
                self.get_texture(category, item, preload=True)

        # Also preload UI textures from the main assets folder
        try:
            # Fix: Create direct texture keys for UI elements
            heart_red_path = "assets/ui/heart_red.png"
            heart_gold_path = "assets/ui/heart_gold.png"
            heart_gray_path = "assets/ui/heart_gray.png"

            if os.path.exists(heart_red_path):
                self.textures["ui/heart_red"] = arcade.load_texture(heart_red_path)
            else:
                self.textures["ui/heart_red"] = arcade.make_soft_circle_texture(30, arcade.color.RED)

            if os.path.exists(heart_gold_path):
                self.textures["ui/heart_gold"] = arcade.load_texture(heart_gold_path)
            else:
                self.textures["ui/heart_gold"] = arcade.make_soft_circle_texture(30, arcade.color.GOLD)

            if os.path.exists(heart_gray_path):
                self.textures["ui/heart_gray"] = arcade.load_texture(heart_gray_path)
            else:
                self.textures["ui/heart_gray"] = arcade.make_soft_circle_texture(30, arcade.color.GRAY)
        except Exception as e:
            print(f"⚠️ Error loading UI textures: {e}")
            # Create fallback textures
            self.textures["ui/heart_red"] = arcade.make_soft_circle_texture(30, arcade.color.RED)
            self.textures["ui/heart_gold"] = arcade.make_soft_circle_texture(30, arcade.color.GOLD)
            self.textures["ui/heart_gray"] = arcade.make_soft_circle_texture(30, arcade.color.GRAY)

        print("✅ All assets preloaded successfully")

    def get_texture(self, category, name=None, preload=False):
        """Get a texture by category and name.

        Args:
            category: Category of the texture (player, orbs, etc.).
            name: Name of the texture. If None, uses 'default'.
            preload: Whether this is being called during preloading.

        Returns:
            arcade.Texture: The requested texture.
        """
        # If name is not provided, use 'default'
        if name is None:
            name = 'default'

        # Check if texture is already loaded
        texture_key = f"{category}/{name}"
        if texture_key in self.textures:
            return self.textures[texture_key]

        # Special case for UI elements that are in the main assets folder
        if category == "ui":
            if name in ["heart_red", "heart_gold", "heart_gray"]:
                try:
                    # Fix: Load directly from assets/ui folder with proper path
                    texture_path = f"assets/ui/{name}.png"
                    if os.path.exists(texture_path):
                        texture = arcade.load_texture(texture_path)
                        self.textures[texture_key] = texture
                        return texture
                    else:
                        return self.get_default_texture(category, name)
                except Exception as e:
                    if not preload:
                        print(f"⚠️ Error loading UI texture '{name}': {e}")
                    return self.get_default_texture(category, name)

        # Try to load from current skin
        try:
            texture_path = os.path.join(self.skins_path, self.current_skin, category, f"{name}.png")
            texture = arcade.load_texture(texture_path)
            self.textures[texture_key] = texture
            return texture
        except Exception as e:
            if not preload:
                print(f"⚠️ Error loading texture '{name}' from '{texture_path}': {e}")

            # Try to load from default skin if not already using default
            if self.current_skin != "default":
                try:
                    default_path = os.path.join(self.skins_path, "default", category, f"{name}.png")
                    texture = arcade.load_texture(default_path)
                    self.textures[texture_key] = texture
                    return texture
                except Exception as e2:
                    if not preload:
                        print(f"⚠️ Error loading default texture '{name}' from '{default_path}': {e2}")

            # Use default texture from our predefined set
            return self.get_default_texture(category, name)

    def get_default_texture(self, category, name):
        """Get a default texture for a category and name.

        Args:
            category: Category of the texture.
            name: Name of the texture.

        Returns:
            arcade.Texture: A default texture.
        """
        texture_key = f"{category}/{name}"

        # Check if we have a predefined default texture
        if texture_key in self.default_textures:
            return self.default_textures[texture_key]

        # Create a new default texture based on category
        if category == "orbs":
            if name in ["speed", "shield", "health", "cooldown", "multiplier"]:
                color = arcade.color.GREEN
            else:
                color = arcade.color.RED
        elif category == "artifacts":
            color = arcade.color.BLUE
        elif category == "player":
            color = arcade.color.LIGHT_BLUE
        elif category == "ui":
            if name.startswith("heart"):
                color = arcade.color.RED
            elif name == "shield":
                color = arcade.color.BLUE
            else:
                color = arcade.color.WHITE
        else:
            color = arcade.color.WHITE

        # Create and store the texture
        texture = arcade.make_soft_circle_texture(30, color)
        self.default_textures[texture_key] = texture
        return texture

    def set_skin(self, skin_name):
        """Set the current skin.

        Args:
            skin_name: Name of the skin to use.
        """
        if skin_name != self.current_skin:
            self.load_skin(skin_name)
            print(f"🎨 Skin set to: {skin_name}")

    def get_player_scale(self):
        """Get the scale for player sprites.

        Returns:
            float: The scale value.
        """
        return self.scales.get("player", 1.0)

    def get_enemy_scale(self):
        """Get the scale for enemy sprites.

        Returns:
            float: The scale value.
        """
        return self.scales.get("enemy", 1.0)

    def get_bullet_scale(self):
        """Get the scale for bullet sprites.

        Returns:
            float: The scale value.
        """
        return self.scales.get("bullet", 1.0)

    def get_orb_scale(self):
        """Get the scale for orb sprites.

        Returns:
            float: The scale value.
        """
        return self.scales.get("orb", 1.0)

    def get_artifact_scale(self):
        """Get the scale for artifact sprites.

        Returns:
            float: The scale value.
        """
        return self.scales.get("artifact", 1.0)

    def get_coin_scale(self):
        """Get the scale for coin sprites.

        Returns:
            float: The scale value.
        """
        return self.scales.get("coin", 1.0)

# Global instance (singleton)
skin_manager = SkinManager()
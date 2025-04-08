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
        self.scales = {}  # Add scales dictionary to store scaling factors

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
            skin_data = {
                "name": skin_dir.capitalize(),
                "description": f"{skin_dir.capitalize()} skin",
                "path": skin_path
            }

            # Try to load config file if it exists
            config_path = os.path.join(skin_path, "config.json")
            if os.path.exists(config_path):
                try:
                    with open(config_path, "r") as f:
                        config = json.load(f)
                        # Update skin data with config values
                        if "name" in config:
                            skin_data["name"] = config["name"]
                        if "description" in config:
                            skin_data["description"] = config["description"]
                except Exception as e:
                    print(f"⚠️ Error loading skin config: {e}")

            skins[skin_dir] = skin_data

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

        # Set default scales
        self.scales = {
            "player": 1.0,
            "enemy": 1.0,
            "bullet": 1.0,
            "orb": 1.0,
            "artifact": 1.0,
            "coin": 1.0
        }

        # Try to load skin-specific scales from config file
        config_path = os.path.join(self.skins_path, skin_name, "config.json")
        if os.path.exists(config_path):
            try:
                with open(config_path, "r") as f:
                    config = json.load(f)
                    # Update scales if defined in config
                    if "scales" in config:
                        self.scales.update(config["scales"])
                        print(f"🎨 Loaded scales from config: {self.scales}")
            except Exception as e:
                print(f"⚠️ Error loading skin config: {e}")

        # Preload textures
        self.preload_textures()
        print(f"🎨 Skin set to: {skin_name}")

    def preload_textures(self):
        """Preload all textures for the current skin."""
        print(f"🎨 Preloading skin assets for '{self.current_skin}'...")

        # Define categories and their items based on your actual asset structure
        categories = {
            "player": ["default", "idle", "dash"],
            "orbs": ["speed", "shield", "cooldown", "hitbox", "multiplier", "vision", "health"],
            "artifacts": ["dash", "clone", "bullet_time", "magnet", "slow"],
            "enemy": ["default"],
            "bullet": ["default"],
            "coin": ["default"]
        }

        # Preload all textures
        for category, items in categories.items():
            for item in items:
                self.get_texture(category, item, preload=True)

        # Also preload UI textures from the main assets folder
        try:
            # UI elements to preload
            ui_elements = ["heart_red", "heart_gold", "heart_gray", "shield", "background", "logo"]
            
            for element in ui_elements:
                element_path = f"assets/ui/{element}.png"
                if os.path.exists(element_path):
                    self.textures[f"ui/{element}"] = arcade.load_texture(element_path)
                else:
                    # Create fallback textures based on element type
                    if "heart_red" in element:
                        self.textures[f"ui/{element}"] = arcade.make_soft_circle_texture(30, arcade.color.RED)
                    elif "heart_gold" in element:
                        self.textures[f"ui/{element}"] = arcade.make_soft_circle_texture(30, arcade.color.GOLD)
                    elif "heart_gray" in element:
                        self.textures[f"ui/{element}"] = arcade.make_soft_circle_texture(30, arcade.color.GRAY)
                    elif "shield" in element:
                        self.textures[f"ui/{element}"] = arcade.make_soft_circle_texture(30, arcade.color.CYAN)
                    else:
                        # Default fallback to the default textures
                        if f"ui/{element}" in self.default_textures:
                            self.textures[f"ui/{element}"] = self.default_textures[f"ui/{element}"]
        except Exception as e:
            print(f"⚠️ Error loading UI textures: {e}")
            # Use default textures as fallback
            for key, texture in self.default_textures.items():
                if key.startswith("ui/") and key not in self.textures:
                    self.textures[key] = texture

        print(f"✅ All assets preloaded successfully for skin '{self.current_skin}'")

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

        # Try to load from current skin
        try:
            texture_path = os.path.join(self.skins_path, self.current_skin, category, f"{name}.png")
            if os.path.exists(texture_path):
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
                if os.path.exists(default_path):
                    texture = arcade.load_texture(default_path)
                    self.textures[texture_key] = texture
                    return texture
            except Exception as e2:
                if not preload:
                    print(f"⚠️ Error loading default texture '{name}' from '{default_path}': {e2}")

        # Create fallback textures based on category
        if not preload:
            print(f"🎨 Creating fallback texture for {category}/{name}")
            texture = None

            # Choose color based on category and name
            if category == "orbs":
                # Different colors for different orb types
                if "buff" in name or name in ["speed", "shield", "multiplier"]:
                    color = arcade.color.GREEN
                else:
                    color = arcade.color.RED
            elif category == "artifacts":
                color = arcade.color.PURPLE
            elif category == "speed" or category == "effects":
                color = arcade.color.YELLOW
            elif category == "player":
                color = arcade.color.BLUE
            else:
                # Default fallback
                color = arcade.color.WHITE

            # Create the texture - remove the 'soft' parameter
            texture = arcade.make_circle_texture(32, color)

            if texture:
                self.textures[texture_key] = texture
                return texture

        return None

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
        return self.scales.get("player", 0.035)
    
    def get_orb_scale(self):
        """Get the scale for orb sprites.

        Returns:
            float: The scale value.
        """
        scale = self.scales.get("orb", 1.0)
        print(f"🔍 Getting orb scale: {scale} for skin: {self.current_skin}")
        return scale
        
    def get_enemy_scale(self):
        """Get the scale for enemy sprites.

        Returns:
            float: The scale value.
        """
        return self.scales.get("enemy", 1.0)

# Global instance (singleton)
skin_manager = SkinManager()
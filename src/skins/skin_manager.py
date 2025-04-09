# src/skins/skin_manager.py

import arcade
import os
import json
from src.core.resource_manager import load_texture

# Import skin paths from constants
from src.core.constants import DEFAULT_SKIN_PATH, MDMA_SKIN_PATH

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
        """Create default textures for missing assets."""
        # Create default player texture if missing
        if "player/player" not in self.textures:
            texture = arcade.make_soft_circle_texture(64, arcade.color.WHITE)
            self.textures["player/player"] = texture
            print(f"  ✓ Created default texture: player/player")

        # Create default enemy textures if missing
        enemy_colors = {
            "wanderer": arcade.color.BLUE,
            "chaser": arcade.color.RED,
            "shooter": arcade.color.PURPLE
        }

        for enemy_type, color in enemy_colors.items():
            texture_key = f"enemies/{enemy_type}"
            if texture_key not in self.textures:
                texture = arcade.make_soft_circle_texture(64, color)
                self.textures[texture_key] = texture
                print(f"  ✓ Created default texture: {texture_key}")

        # Create default projectile texture if missing
        if "projectiles/enemy_bullet" not in self.textures:
            texture = arcade.make_soft_circle_texture(16, arcade.color.YELLOW)
            self.textures["projectiles/enemy_bullet"] = texture
            print(f"  ✓ Created default texture: projectiles/enemy_bullet")

        # Create default orb textures if missing
        orb_types = ["slow", "vision", "hitbox"]
        orb_colors = {
            "slow": arcade.color.ORANGE,
            "vision": arcade.color.PURPLE,
            "hitbox": arcade.color.PINK
        }

        for orb_type in orb_types:
            texture_key = f"orbs/{orb_type}"
            if texture_key not in self.textures:
                color = orb_colors.get(orb_type, arcade.color.WHITE)
                texture = arcade.make_soft_circle_texture(32, color)
                self.textures[texture_key] = texture
                print(f"  ✓ Created default texture: {texture_key}")

        # Create default UI textures
        ui_elements = {
            "heart_red": arcade.color.RED,
            "heart_gray": arcade.color.GRAY,
            "heart_gold": arcade.color.GOLD
        }

        for ui_element, color in ui_elements.items():
            texture_key = f"ui/{ui_element}"
            if texture_key not in self.textures:
                texture = arcade.make_soft_circle_texture(30, color)
                self.textures[texture_key] = texture
                print(f"  ✓ Created default texture: {texture_key}")

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
        """Load a skin by name."""
        if skin_name == "default":
            skin_path = DEFAULT_SKIN_PATH
        elif skin_name == "mdma":
            skin_path = MDMA_SKIN_PATH
        else:
            print(f"⚠️ Unknown skin: {skin_name}, using default")
            skin_path = DEFAULT_SKIN_PATH

        print(f"🎨 Loading skin: {skin_name} from {skin_path}")

        # Load textures
        self.textures = {}

        # Load player textures
        self._load_texture(skin_path, "player", "player")

        # Load enemy textures
        self._load_texture(skin_path, "enemies", "wanderer")
        self._load_texture(skin_path, "enemies", "chaser")
        self._load_texture(skin_path, "enemies", "shooter")

        # Load orb textures
        self._load_texture(skin_path, "orbs", "speed")
        self._load_texture(skin_path, "orbs", "shield")
        self._load_texture(skin_path, "orbs", "multiplier")
        self._load_texture(skin_path, "orbs", "cooldown")
        self._load_texture(skin_path, "orbs", "slow")
        self._load_texture(skin_path, "orbs", "vision")
        self._load_texture(skin_path, "orbs", "hitbox")

        # Load projectile textures
        self._load_texture(skin_path, "projectiles", "enemy_bullet")

        # Load scales from config
        self._load_scales(skin_path)

        self.current_skin = skin_name
        print(f"🎨 Loaded skin: {skin_name}")

    def _load_texture(self, skin_path, category, name):
        """Load a texture from the skin."""
        # Try different file extensions
        extensions = [".png", ".jpg", ".jpeg"]

        for ext in extensions:
            texture_path = f"{skin_path}/{category}/{name}{ext}"
            if os.path.exists(texture_path):
                texture = arcade.load_texture(texture_path)
                texture_key = f"{category}/{name}"
                self.textures[texture_key] = texture
                print(f"  ✓ Loaded texture: {texture_key}")
                return

        print(f"  ✗ Texture not found: {category}/{name}")

    def _load_scales(self, skin_path):
        """Load scales from skin config."""
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
        config_path = os.path.join(skin_path, "config.json")
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

    def get_texture(self, category, name=None):
        """Get a texture by category and name."""
        if name is None:
            # Legacy support for old format
            texture_key = category
        else:
            texture_key = f"{category}/{name}"

        if texture_key in self.textures:
            return self.textures[texture_key]

        print(f"⚠️ Texture not found: {texture_key}")
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
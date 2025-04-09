# src/skins/skin_manager.py

import arcade
import os
import json
from src.core.resource_manager import load_texture
from src.core.scaling import get_scale, set_scale

# Import skin paths from constants
from src.core.constants import DEFAULT_SKIN_PATH, MDMA_SKIN_PATH

class SkinManager:
    """Manages game skins and textures."""
    def __init__(self):
        """Initialize the skin manager."""
        self.current_skin = "default"
        self.skins_path = "assets/skins"
        self.textures = {}

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

    def load_ui_textures(self):
        import os

        ui_dir = "assets/skins/default/ui"
        effects_dir = os.path.join(ui_dir, "effects")

        ui_textures = ["heart_red", "heart_gray", "heart_gold"]
        effect_textures = ["speed", "shield", "multiplier", "slow", "vision", "hitbox", "cooldown"]

        if "ui" not in self.textures:
            self.textures["ui"] = {}

        for tex in ui_textures:
            path = os.path.join(ui_dir, f"{tex}.png")
            if os.path.exists(path):
                self.textures["ui"][tex] = arcade.load_texture(path)
                print(f"✅ Loaded UI texture: {tex}")
            else:
                print(f"❌ Missing UI texture: {tex}")

        for tex in effect_textures:
            path = os.path.join(effects_dir, f"{tex}.png")
            key = f"effects/{tex}"
            if os.path.exists(path):
                self.textures["ui"][key] = arcade.load_texture(path)
                print(f"✅ Loaded effect icon: {key}")
            else:
                print(f"❌ Missing effect icon: {key}")

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
        config_path = os.path.join(skin_path, "config.json")
        if os.path.exists(config_path):
            try:
                with open(config_path, "r") as f:
                    config = json.load(f)
                    self.load_scales(config)
            except Exception as e:
                print(f"⚠️ Error loading skin config: {e}")
        else:
            print("⚠️ No config file found, using default scales")

        self.current_skin = skin_name
        print(f"🎨 Loaded skin: {skin_name}")

    def _load_texture(self, skin_path, category, name):
        """Load a texture from the skin."""
        # Try different file extensions
        extensions = [".png", ".jpg", ".jpeg"]

        print(f"🔍 Looking for texture: {category}/{name}")

        for ext in extensions:
            texture_path = f"{skin_path}/{category}/{name}{ext}"
            print(f"  - Checking path: {texture_path}")
            if os.path.exists(texture_path):
                try:
                    texture = arcade.load_texture(texture_path)
                    texture_key = f"{category}/{name}"
                    self.textures[texture_key] = texture
                    print(f"  ✓ Loaded texture: {texture_key} (size: {texture.width}x{texture.height})")
                    return
                except Exception as e:
                    print(f"  ✗ Error loading texture: {texture_path} - {e}")

        print(f"  ✗ Texture not found: {category}/{name}")

    def load_scales(self, config_data):
        """Load scales from config data."""
        if 'scales' in config_data:
            print(f"🎨 Loaded scales from config: {config_data['scales']}")
            # Update the centralized scaling system
            for entity_type, scale in config_data['scales'].items():
                set_scale(entity_type, scale)
        else:
            print("⚠️ No scales found in config, using defaults")

    def get_scale(self, entity_type):
        """Get the scale for a specific entity type."""
        return get_scale(entity_type)

    def get_texture(self, category, name=None, force_reload=False):
        """Get a texture by category and name.
        
        Args:
            category: Category of the texture (e.g., "ui").
            name: Name of the texture (e.g., "heart_red" or "effects/speed").
            force_reload: Whether to force reload the texture from disk.
            
        Returns:
            arcade.Texture: The texture if found, None otherwise.
        """
        # Handle the case where name contains a slash (from old format)
        if name and "/" in name:
            parts = name.split("/", 1)
            if len(parts) == 2:
                subcategory, item_name = parts
                texture_key = f"{category}/{subcategory}/{item_name}"
            else:
                texture_key = f"{category}/{name}"
        elif name is None:
            # Legacy support for old format where category contained the full path
            texture_key = category
        else:
            texture_key = f"{category}/{name}"

        if texture_key in self.textures and not force_reload:
            return self.textures[texture_key]

        print(f"⚠️ Texture not found: {texture_key}")
        return None

    def has_texture(self, category: str, name: str) -> bool:
        """Check if a texture exists in the specified category.
        
        Args:
            category: Category of the texture (e.g., "ui").
            name: Name of the texture (e.g., "effects/speed").
            
        Returns:
            bool: True if the texture exists, False otherwise.
        """
        texture_key = f"{category}/{name}"
        return texture_key in self.textures

    def load_texture(self, category: str, name: str, path: str):
        """Load a texture from a file path and store it in the specified category.
        
        Args:
            category: Category to store the texture in (e.g., "ui").
            name: Name to give the texture (e.g., "effects/speed").
            path: File path to the texture.
            
        Raises:
            FileNotFoundError: If the texture file doesn't exist.
        """
        import arcade
        from PIL import Image
        from pathlib import Path

        texture_key = f"{category}/{name}"
        
        # Load the texture file manually
        if Path(path).exists():
            texture = arcade.load_texture(path)
            self.textures[texture_key] = texture
        else:
            raise FileNotFoundError(f"Texture not found: {path}")

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
        return self.get_scale("player")
    
    def get_orb_scale(self):
        """Get the scale for orb sprites.

        Returns:
            float: The scale value.
        """
        scale = self.get_scale("orb")
        print(f"🔍 Getting orb scale: {scale} for skin: {self.current_skin}")
        return scale
        
    def get_enemy_scale(self):
        """Get the scale for enemy sprites.

        Returns:
            float: The scale value.
        """
        return self.get_scale("enemy")
        
    def get_artifact_scale(self):
        """Get the scale for artifact sprites.
        
        Returns:
            float: The scale value.
        """
        return self.get_scale("artifact")

# Global instance (singleton)
skin_manager = SkinManager()
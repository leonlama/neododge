"""
Skin management system for loading and managing game skins.
"""
import os
import json
import arcade
import appdirs
from scripts.utils.constants import SKINS_DIR, DEFAULT_SKIN_PATH, MDMA_SKIN_PATH
from scripts.utils.resource_helper import resource_path
from scripts.mechanics.event_manager import event_manager

# Define app-specific user data dir for skin unlocks
APP_NAME = "Neododge"
USER_DATA_DIR = os.path.join(appdirs.user_data_dir(APP_NAME), "data")
os.makedirs(USER_DATA_DIR, exist_ok=True)
UNLOCKS_FILE = os.path.join(USER_DATA_DIR, "unlocks.json")

class SkinManager:
    """
    Manages loading and caching of game skin textures.

    Attributes:
        data: Dictionary containing skin data and settings
        skins: Dictionary of loaded skin textures by category and type
    """
    def __init__(self):
        """Initialize the skin manager"""
        print("🎨 [INIT] Initializing skin manager")

        # Initialize data structure
        self.data = {
            "selected": "default",
            "unlocked": ["default", "mdma"],
            "available": ["default", "mdma"],  # Keep original key for compatibility
            "paths": {
                "default": DEFAULT_SKIN_PATH,
                "mdma": MDMA_SKIN_PATH
            },
            "scales": {
                "default": {
                    "player": 0.045,
                    "heart": 0.035,
                    "artifact": 0.17,
                    "orb": 0.17,
                    "enemy": 0.045
                },
                "mdma": {
                    "player": 0.045,
                    "heart": 0.035,
                    "artifact": 0.035,
                    "orb": 0.035,
                    "enemy": 0.045
                }
            }
        }

        # Initialize skins dictionary
        self.skins = {}

        # Initialize shared assets dictionary
        self.shared_assets = {}

        # Load unlocks from file
        self._load_unlocks()

        # Cache for loaded textures (backward compatibility)
        self.textures = {}

        # Load all available skins
        self.load_skins()

        # Load shared assets
        self._load_shared_assets()

        print(f"🎨 [INIT] Using skin: {self.data['selected']}")

    @property
    def current_skin(self):
        """Property for backward compatibility with old code"""
        return self.data["selected"]

    @current_skin.setter
    def current_skin(self, value):
        """Setter for backward compatibility with old code"""
        if value in self.data["unlocked"]:
            self.data["selected"] = value
            self._save_unlocks()

    def _load_unlocks(self):
        """Load unlocked skins from file"""
        if os.path.exists(UNLOCKS_FILE):
            try:
                with open(UNLOCKS_FILE, "r") as f:
                    saved_data = json.load(f)
                    # Update only the keys we care about
                    if "unlocked" in saved_data:
                        self.data["unlocked"] = saved_data["unlocked"]
                        self.data["available"] = saved_data["unlocked"]  # Keep both in sync
                    if "selected" in saved_data:
                        self.data["selected"] = saved_data["selected"]
            except (json.JSONDecodeError, FileNotFoundError):
                self._save_unlocks()  # Fallback to fresh file
        else:
            self._save_unlocks()

    def _save_unlocks(self):
        """Save unlocked skins to file"""
        try:
            save_data = {
                "unlocked": self.data["unlocked"],
                "selected": self.data["selected"]
            }
            with open(UNLOCKS_FILE, "w") as f:
                json.dump(save_data, f, indent=4)
        except Exception as e:
            print(f"Error saving skin unlocks: {e}")

    def load_skins(self):
        """Load all available skin textures"""
        for skin_name in self.data["available"]:
            self._load_skin(skin_name)

    def _load_shared_assets(self):
        """Load shared assets that are the same for all skins"""
        # Define shared asset categories and their paths
        shared_assets = {
            "hearts": {
                "red": "assets/ui/heart_red.png",
                "gray": "assets/ui/heart_gray.png",
                "gold": "assets/ui/heart_gold.png",
            },
            "coins": {
                #"default": "assets/items/coin/coin_1.png",  # First frame of animation
                "gold": "assets/items/coin/gold_coin.png"  # First frame of gold coin animation
            },
            #"enemies": {
            #    "basic": "assets/enemies/basic.png",
            #    "shooter": "assets/enemies/shooter.png",
            #    "bomber": "assets/enemies/bomber.png"
            #},
            #"bullets": {
            #    "default": "assets/bullets/default.png",
            #    "enemy": "assets/bullets/enemy.png"
            #}
        }

        # Load each shared asset
        for category, assets in shared_assets.items():
            if category not in self.shared_assets:
                self.shared_assets[category] = {}

            for asset_type, path in assets.items():
                try:
                    full_path = resource_path(path)
                    if os.path.exists(full_path):
                        texture = arcade.load_texture(full_path)
                        self.shared_assets[category][asset_type] = texture
                    else:
                        print(f"Warning: Shared asset not found: {full_path}")
                except Exception as e:
                    print(f"Error loading shared asset {category}/{asset_type}: {e}")

    def _load_skin(self, skin_name):
        """
        Load a specific skin's textures

        Args:
            skin_name: Name identifier for the skin
        """
        if skin_name not in self.data["paths"]:
            print(f"Error: Skin path not found for {skin_name}")
            return

        skin_path = self.data["paths"][skin_name]
        self.skins[skin_name] = {}

        # Define categories and their asset types
        categories = {
            "player": ["default"],
            "orbs": ["speed", "shield", "cooldown", "multiplier", "vision", "hitbox"],
            "artifacts": ["dash", "magnet", "slow", "bullet_time", "clone"],
        }

        # Load textures for each category and type
        for category, types in categories.items():
            self.skins[skin_name][category] = {}

            for asset_type in types:
                try:
                    # Construct path to texture
                    texture_path = os.path.join(skin_path, category, f"{asset_type}.png")
                    full_path = resource_path(texture_path)

                    if os.path.exists(full_path):
                        texture = arcade.load_texture(full_path)
                        self.skins[skin_name][category][asset_type] = texture
                    else:
                        print(f"Warning: Texture not found: {full_path}")
                except Exception as e:
                    print(f"Error loading texture {category}/{asset_type} for skin {skin_name}: {e}")

    def _create_fallback_texture(self, category, asset_type):
        """
        Create a fallback texture when the requested texture is not found

        Args:
            category: Category of the texture
            asset_type: Type of the asset

        Returns:
            arcade.Texture: A fallback texture
        """
        # Default color and size
        color = arcade.color.WHITE
        size = 30

        # Customize based on category and type
        if category == "player":
            color = arcade.color.BLUE
            size = 30
        elif category == "orbs":
            size = 18
            if asset_type == "speed":
                color = arcade.color.BLUE
            elif asset_type == "shield":
                color = arcade.color.LIGHT_GREEN
            elif asset_type == "cooldown":
                color = arcade.color.PURPLE
            elif asset_type == "multiplier":
                color = arcade.color.GOLD
            elif asset_type == "vision":
                color = arcade.color.GRAY
            elif asset_type == "hitbox":
                color = arcade.color.RED
        elif category == "hearts":
            size = 24
            if asset_type == "red" or asset_type == "health":
                color = arcade.color.RED
            elif asset_type == "gray":
                color = arcade.color.GRAY
            elif asset_type == "gold":
                color = arcade.color.GOLD
        elif category == "artifacts":
            size = 24
            color = arcade.color.PURPLE

        # Create and return the texture
        if category == "player":
            return arcade.make_soft_square_texture(size, color, outer_alpha=255)
        else:
            return arcade.make_soft_circle_texture(size, color, outer_alpha=255)

    def select(self, skin_name):
        """
        Select a skin to use

        Args:
            skin_name: Name of the skin to select

        Returns:
            bool: True if skin was found and selected, False otherwise
        """
        if skin_name in self.data["available"]:
            self.data["selected"] = skin_name
            self._save_unlocks()
            print(f"Skin changed to: {skin_name}")
            return True
        return False

    def toggle_skin(self):
        """
        Toggle between available skins (for backward compatibility)

        Returns:
            str: Name of the newly selected skin
        """
        current_index = self.data["unlocked"].index(self.data["selected"])
        next_index = (current_index + 1) % len(self.data["unlocked"])
        next_skin = self.data["unlocked"][next_index]
        self.select(next_skin)
        print(f"Skin changed to: {next_skin}")
        return next_skin

    def unlock(self, skin_name):
        """
        Unlock a new skin

        Args:
            skin_name: Name of the skin to unlock
        """
        if skin_name not in self.data["unlocked"]:
            self.data["unlocked"].append(skin_name)
            self.data["available"].append(skin_name)  # Keep both in sync
            self._load_skin(skin_name)  # Load the newly unlocked skin
            self._save_unlocks()

    def is_unlocked(self, skin_name):
        """
        Check if a skin is unlocked

        Args:
            skin_name: Name of the skin to check

        Returns:
            bool: True if skin is unlocked, False otherwise
        """
        return skin_name in self.data["unlocked"]
    
    def get_texture(self, category, asset_type, force_reload=False):
        """
        Get a texture from the currently selected skin or shared assets

        Args:
            category: Category of the texture (player, orbs, etc.)
            asset_type: Type of the asset within the category
            force_reload: Whether to force reload the texture (ignored in this implementation)

        Returns:
            arcade.Texture: The requested texture or a fallback texture if not found
        """
        try:
            skin_name = self.data["selected"]

            # Special case for hearts - always use shared assets
            if category == "hearts":
                # Map "health" to "red" for compatibility
                if asset_type == "health":
                    asset_type = "red"

                if category in self.shared_assets and asset_type in self.shared_assets[category]:
                    return self.shared_assets[category][asset_type]

            # Special case for coins - always use shared assets
            if category == "coins":
                if category in self.shared_assets and asset_type in self.shared_assets[category]:
                    return self.shared_assets[category][asset_type]

            # Special case for enemies - always use shared assets
            if category == "enemies":
                if category in self.shared_assets and asset_type in self.shared_assets[category]:
                    return self.shared_assets[category][asset_type]

            # Special case for bullets - always use shared assets
            if category == "bullets":
                if category in self.shared_assets and asset_type in self.shared_assets[category]:
                    return self.shared_assets[category][asset_type]

            # Try to get from selected skin
            if (skin_name in self.skins and 
                category in self.skins[skin_name] and 
                asset_type in self.skins[skin_name][category]):
                return self.skins[skin_name][category][asset_type]

            # Try to get from shared assets
            if category in self.shared_assets and asset_type in self.shared_assets[category]:
                return self.shared_assets[category][asset_type]

            # Fall back to default skin if not found and not already using default
            if (skin_name != "default" and 
                "default" in self.skins and 
                category in self.skins["default"] and 
                asset_type in self.skins["default"][category]):
                return self.skins["default"][category][asset_type]

            # Create fallback texture if all else fails
            return self._create_fallback_texture(category, asset_type)

        except Exception as e:
            print(f"Error in get_texture({category}, {asset_type}): {e}")
            import traceback
            traceback.print_exc()
            return self._create_fallback_texture(category, asset_type)

    def get_texture_path(self, category, asset_type):
        """
        Get the path to a texture in the currently selected skin

        Args:
            category: Category of the texture
            asset_type: Type of the asset

        Returns:
            str: Path to the texture file
        """
        skin_name = self.data["selected"]

        # Special case for hearts - always use shared assets
        if category == "hearts":
            # Map "health" to "red" for compatibility
            if asset_type == "health":
                asset_type = "red"
            return f"assets/ui/heart_{asset_type}.png"

        # Special case for coins - always use shared assets
        if category == "coins":
            if asset_type == "gold":
                return "assets/items/coin/gold_coin_1.png"
            return "assets/items/coin/coin_1.png"

        # Special case for enemies - always use shared assets
        if category == "enemies":
            return f"assets/enemies/{asset_type}.png"

        # Special case for bullets - always use shared assets
        if category == "bullets":
            return f"assets/bullets/{asset_type}.png"

        # Use skin-specific path for other assets
        skin_path = self.data["paths"].get(skin_name, self.data["paths"]["default"])
        return os.path.join(skin_path, category, f"{asset_type}.png")

    def get_scale(self, category):
        """
        Get the scale for a specific category in the current skin

        Args:
            category: Category to get scale for (player, heart, etc.)

        Returns:
            float: Scale value for the category
        """
        skin_name = self.data["selected"]
        category_key = category.lower()

        # Map some categories to their scale keys
        if category_key == "hearts":
            category_key = "heart"
        elif category_key == "orbs":
            category_key = "orb"
        elif category_key == "artifacts":
            category_key = "artifact"
        elif category_key == "enemies":
            category_key = "enemy"

        return self.data["scales"].get(skin_name, {}).get(category_key, 1.0)

    # Compatibility methods for old code
    def get_player_scale(self):
        """Get the scale for player sprites in the current skin"""
        skin_name = self.data["selected"]
        return self.data["scales"][skin_name]["player"]

    def get_heart_scale(self):
        """Get the scale for heart sprites in the current skin"""
        skin_name = self.data["selected"]
        return self.data["scales"][skin_name]["heart"]

    def get_artifact_scale(self):
        """Get the scale for artifact sprites in the current skin"""
        skin_name = self.data["selected"]
        return self.data["scales"][skin_name]["artifact"]

    def get_orb_scale(self):
        """Get the scale for orb sprites in the current skin"""
        skin_name = self.data["selected"]
        return self.data["scales"][skin_name]["orb"]

    def get_enemy_scale(self):
        """Get the scale for enemy sprites in the current skin"""
        skin_name = self.data["selected"]
        return self.data["scales"][skin_name]["enemy"]

    def get_path(self):
        """Return the active skin path (for compatibility)"""
        skin_name = self.data["selected"]
        return self.data["paths"].get(skin_name, self.data["paths"]["default"])

    def get_selected(self):
        """Return the currently selected skin name (for compatibility)"""
        return self.data["selected"]

    def clear_cache(self):
        """Clear the texture cache (for compatibility)"""
        self.textures = {}

# Create singleton instance
skin_manager = SkinManager()
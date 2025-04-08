"""
Skin management system for loading and managing player skins.
"""
import os
import arcade
from .constants import SKINS_DIR, DEFAULT_SKIN_PATH, MDMA_SKIN_PATH
from scripts.utils.resource_helper import resource_path

class SkinManager:
    """
    Manages loading and caching of player skin textures.

    Attributes:
        skins: Dictionary of loaded skin textures
        current_skin: Currently selected skin name
    """
    def __init__(self):
        """Initialize the skin manager and load available skins"""
        self.skins = {}
        self.current_skin = "default"
        self.load_skins()

    def load_skins(self):
        """Load all available skin textures"""
        # Load default skin
        self._load_skin("default", DEFAULT_SKIN_PATH)

        # Load MDMA skin
        self._load_skin("mdma", MDMA_SKIN_PATH)

        # Load any additional skins from the skins directory
        self._discover_additional_skins()

    def _load_skin(self, skin_name, skin_path):
        """
        Load a specific skin's textures

        Args:
            skin_name: Name identifier for the skin
            skin_path: File path to the skin assets
        """
        try:
            # Create a dictionary to store this skin's textures
            skin_textures = {}

            # Load player textures
            player_path = resource_path(os.path.join(skin_path, "player.png"))
            if os.path.exists(player_path):
                skin_textures["player"] = arcade.load_texture(player_path)

            # Load other textures as needed
            # Example:
            # bullet_path = resource_path(os.path.join(skin_path, "bullet.png"))
            # if os.path.exists(bullet_path):
            #     skin_textures["bullet"] = arcade.load_texture(bullet_path)

            # Store the skin if we loaded at least one texture
            if skin_textures:
                self.skins[skin_name] = skin_textures
        except Exception as e:
            print(f"Error loading skin {skin_name}: {e}")

    def _discover_additional_skins(self):
        """Discover and load any additional skins in the skins directory"""
        try:
            skins_dir = resource_path(SKINS_DIR)
            if os.path.exists(skins_dir) and os.path.isdir(skins_dir):
                for item in os.listdir(skins_dir):
                    item_path = os.path.join(skins_dir, item)
                    if os.path.isdir(item_path) and item not in ["default", "mdma"]:
                        self._load_skin(item, os.path.join(SKINS_DIR, item))
        except Exception as e:
            print(f"Error discovering additional skins: {e}")

    def get_skin(self, skin_name=None):
        """
        Get a skin's textures by name

        Args:
            skin_name: Name of the skin to get (uses current_skin if None)

        Returns:
            dict: Dictionary of skin textures or default skin if not found
        """
        if skin_name is None:
            skin_name = self.current_skin

        return self.skins.get(skin_name, self.skins.get("default", {}))

    def set_current_skin(self, skin_name):
        """
        Set the current skin

        Args:
            skin_name: Name of the skin to set as current

        Returns:
            bool: True if skin was found and set, False otherwise
        """
        if skin_name in self.skins:
            self.current_skin = skin_name
            return True
        return False

    def get_selected(self):
        """
        Get the name of the currently selected skin

        Returns:
            str: Name of the current skin
        """
        return self.current_skin

# Create a singleton instance
#skin_manager = SkinManager()
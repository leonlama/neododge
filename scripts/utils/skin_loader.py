"""
Skin management system for loading and managing player skins.
"""
import arcade
import os
from .constants import SKINS_DIR, DEFAULT_SKIN_PATH, MDMA_SKIN_PATH

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
            # Original skin loading code
            # ...

            # Add better error handling and logging
            self.skins[skin_name] = {
                # Skin textures
            }
        except Exception as e:
            print(f"Error loading skin {skin_name}: {e}")

    def _discover_additional_skins(self):
        """Discover and load any additional skins in the skins directory"""
        try:
            # New functionality to discover skins
            pass  # Placeholder until actual implementation
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

        return self.skins.get(skin_name, self.skins.get("default"))

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
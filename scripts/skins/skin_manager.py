import os
import json
import arcade
import appdirs  # Cross-platform user data dir
from scripts.utils.resource_helper import resource_path
from scripts.utils.constants import DEFAULT_SKIN_PATH, MDMA_SKIN_PATH, DEFAULT_SKIN
from scripts.skins.skin_sets import SKIN_SETS

# Define app-specific user data dir
APP_NAME = "Neododge"
USER_DATA_DIR = os.path.join(appdirs.user_data_dir(APP_NAME), "data")
os.makedirs(USER_DATA_DIR, exist_ok=True)

# Cross-platform safe JSON file location (not inside dist/)
UNLOCKS_FILE = os.path.join(USER_DATA_DIR, "unlocks.json")

class SkinManager:
    """
    Manages game skins, including loading, caching, and switching between visual themes.

    Responsibilities:
    - Load and cache textures for different skins
    - Track unlocked and selected skins
    - Provide methods to toggle between skins
    - Persist skin selection between game sessions
    """

    def __init__(self):
        """Initialize the skin manager with default settings and load saved data."""
        # Default data
        self.data = {
            "unlocked": ["default", "mdma"],
            "selected": DEFAULT_SKIN
        }

        self._load_data()
        self._validate_selected_skin()
        self.textures = {}  # In-memory texture cache

    def _load_data(self):
        """Load unlocked skins data from disk."""
        if os.path.exists(UNLOCKS_FILE):
            try:
                with open(UNLOCKS_FILE, "r") as f:
                    self.data = json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                self.save()  # Fallback to fresh file
        else:
            self.save()

    def _validate_selected_skin(self):
        """Ensure the selected skin exists, fallback to default if not."""
        if self.data["selected"] not in SKIN_SETS:
            self.data["selected"] = DEFAULT_SKIN

    def get_scale(self, category):
        """
        Return the scale value for a given category.

        Args:
            category (str): Asset category like 'player', 'orb', 'artifact', 'heart'

        Returns:
            float: Scale value for the specified category
        """
        current_skin = self.data["selected"]
        return SKIN_SETS.get(current_skin, SKIN_SETS[DEFAULT_SKIN]).get(f"{category}_scale", 1.0)

    def get_path(self):
        """Return the active skin path."""
        skin_name = self.data["selected"]
        return SKIN_SETS.get(skin_name, SKIN_SETS[DEFAULT_SKIN])["path"]

    def get_texture_path(self, category, name):
        """
        Return relative path to a texture.

        Args:
            category (str): Asset category folder name
            name (str): Asset file name without extension

        Returns:
            str: Path like 'assets/skins/mdma/hearts/red.png'
        """
        return os.path.join(self.get_path(), category, f"{name}.png")

    def get_texture(self, category, name):
        """
        Load and cache texture via resource_path (PyInstaller-safe).

        Args:
            category (str): Asset category folder name
            name (str): Asset file name without extension

        Returns:
            arcade.Texture: The loaded texture
        """
        key = f"{self.get_path()}/{category}/{name}"

        if key not in self.textures:
            texture_path = self.get_texture_path(category, name)
            self.textures[key] = arcade.load_texture(resource_path(texture_path))

        return self.textures[key]

    def unlock(self, skin_name):
        """
        Unlock a new skin.

        Args:
            skin_name (str): Name of the skin to unlock
        """
        if skin_name not in self.data["unlocked"]:
            self.data["unlocked"].append(skin_name)
            self.save()

    def toggle_skin(self):
        """
        Toggle between available skins.

        Returns:
            str: The newly selected skin name
        """
        current_skin = self.data["selected"]
        next_skin = "mdma" if current_skin == "default" else "default"

        # Make sure the skin is unlocked
        if next_skin not in self.data["unlocked"]:
            self.data["unlocked"].append(next_skin)

        # Update the selected skin
        self.data["selected"] = next_skin
        self.clear_cache()
        self.save()

        print(f"🎨 Toggled skin to: {next_skin}")
        return next_skin

    def clear_cache(self):
        """Clear the texture cache to force reloading textures."""
        self.textures = {}

    def get_selected(self):
        """Return the currently selected skin name."""
        return self.data["selected"]

    def is_unlocked(self, skin_name):
        """Check if a skin is unlocked."""
        return skin_name in self.data["unlocked"]

    def save(self):
        """Save unlock data to disk."""
        with open(UNLOCKS_FILE, "w") as f:
            json.dump(self.data, f, indent=4)


# Create a singleton instance
skin_manager = SkinManager()
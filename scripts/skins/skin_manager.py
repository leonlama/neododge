import json
import os
import arcade
import appdirs  # Cross-platform user data dir
from scripts.utils.resource_helper import resource_path
from scripts.utils.constants import DEFAULT_SKIN_PATH, MDMA_SKIN_PATH
from scripts.skins.skin_sets import SKIN_SETS, DEFAULT_SKIN

# Define app-specific user data dir
APP_NAME = "Neododge"
USER_DATA_DIR = os.path.join(appdirs.user_data_dir(APP_NAME), "data")
os.makedirs(USER_DATA_DIR, exist_ok=True)

# Cross-platform safe JSON file location (not inside dist/)
UNLOCKS_FILE = os.path.join(USER_DATA_DIR, "unlocks.json")

class SkinManager:
    def __init__(self):
        # Default data
        self.data = {
            "unlocked": ["default", "mdma"],
            "selected": DEFAULT_SKIN
        }

        # Load unlocks safely
        if os.path.exists(UNLOCKS_FILE):
            try:
                with open(UNLOCKS_FILE, "r") as f:
                    self.data = json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                self.save()  # Fallback to fresh file
        else:
            self.save()

        # Make sure selected skin exists, fallback to default if not
        if self.data["selected"] not in SKIN_SETS:
            self.data["selected"] = DEFAULT_SKIN

        self.textures = {}  # In-memory texture cache

    def get_scale(self, category):
        """Return the scale value for a given category like 'player', 'orb', 'artifact', 'heart'."""
        current_skin = self.data["selected"]
        return SKIN_SETS.get(current_skin, SKIN_SETS[DEFAULT_SKIN]).get(f"{category}_scale", 1.0)

    def get_artifact_scale(self):
        """Return the scale value for artifacts based on current skin."""
        skin_name = self.data["selected"]
        return SKIN_SETS.get(skin_name, SKIN_SETS[DEFAULT_SKIN])["artifact_scale"]

    def get_orb_scale(self):
        """Return the scale value for orbs based on current skin."""
        skin_name = self.data["selected"]
        return SKIN_SETS.get(skin_name, SKIN_SETS[DEFAULT_SKIN])["orb_scale"]

    def get_heart_scale(self):
        skin_name = self.data["selected"]
        return SKIN_SETS.get(skin_name, SKIN_SETS[DEFAULT_SKIN])["heart_scale"]

    def get_path(self):
        """Return the active skin path."""
        skin_name = self.data["selected"]
        return SKIN_SETS.get(skin_name, SKIN_SETS[DEFAULT_SKIN])["path"]

    def get_texture_path(self, category, name):
        """Return relative path like assets/skins/mdma/hearts/red.png."""
        return os.path.join(self.get_path(), category, f"{name}.png")

    def get_texture(self, category, name, force_reload=False):
        """Load and cache texture via resource_path (PyInstaller-safe)."""
        key = f"{category}/{name}"
        if force_reload or key not in self.textures:
            texture_path = os.path.join(self.get_path(), category, f"{name}.png")
            self.textures[key] = arcade.load_texture(resource_path(texture_path))
        return self.textures[key]

    def unlock(self, skin_name):
        if skin_name not in self.data["unlocked"]:
            self.data["unlocked"].append(skin_name)
            self.save()

    def select(self, skin_name):
        """Select a skin and save the selection"""
        if skin_name in SKIN_SETS:
            # Check if skin is unlocked before selecting
            if skin_name in self.data["unlocked"]:
                self.data["selected"] = skin_name
                self.clear_cache()
                self.save()  # Save to config file for persistence between game sessions
                print(f"✅ Selected skin: {skin_name} (Cache cleared)")  # Debug log
                return True
            else:
                print(f"❌ Cannot select locked skin: {skin_name}")
                return False
        print(f"❌ Failed to select skin: {skin_name} (not found in SKIN_SETS)")
        return False
    
    def clear_cache(self):
        """Clear the texture cache to force reloading textures."""
        self.textures = {}
        
    def get_selected(self):
        """Return the currently selected skin name."""
        return self.data["selected"]

    def is_unlocked(self, skin_name):
        return skin_name in self.data["unlocked"]

    def save(self):
        """Save unlock data to disk."""
        with open(UNLOCKS_FILE, "w") as f:
            json.dump(self.data, f, indent=4)

# Global instance (singleton)
skin_manager = SkinManager()

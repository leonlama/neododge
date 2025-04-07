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
        
        # Current skin tracking
        self.current_skin = self.data["selected"]
        
        # Add this line to track unlocked skins
        self.unlocked_skins = self.data["unlocked"]

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
    
    def get_asset(self, category, name, force_reload=False):
        """Alias for get_texture for compatibility."""
        return self.get_texture(category, name, force_reload)

    def unlock(self, skin_name):
        if skin_name not in self.data["unlocked"]:
            self.data["unlocked"].append(skin_name)
            self.unlocked_skins = self.data["unlocked"]
            self.save()

    def select(self, skin_name):
        """Select a skin and save the selection"""
        if skin_name in SKIN_SETS:
            # Check if skin is unlocked before selecting
            if skin_name in self.data["unlocked"]:
                self.data["selected"] = skin_name
                self.current_skin = skin_name
                self.clear_cache()
                self.save()  # Save to config file for persistence between game sessions
                print(f"✅ Selected skin: {skin_name} (Cache cleared)")  # Debug log
                return True
            else:
                print(f"❌ Cannot select locked skin: {skin_name}")
                return False
        print(f"❌ Failed to select skin: {skin_name} (not found in SKIN_SETS)")
        return False
    
    def load_skin(self, skin_name):
        """Alias for select for compatibility."""
        return self.select(skin_name)
    
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
    
    def save_unlocks(self):
        """Alias for save for compatibility."""
        self.save()
            
    def toggle_skin(self):
        """Toggle between available skins"""
        current_skin = self.data["selected"]
        next_skin = "mdma" if current_skin == "default" else "default"

        # Make sure the skin is unlocked
        if next_skin not in self.data["unlocked"]:
            self.data["unlocked"].append(next_skin)

        # Update the selected skin
        self.data["selected"] = next_skin
        self.current_skin = next_skin
        self.clear_cache()

        # Save changes
        if hasattr(self, 'save'):
            self.save()

        print(f"🎨 Toggled skin to: {next_skin}")
        return next_skin

    def unlock_skin(self, skin_name):
        """Unlock a skin"""
        if skin_name not in self.data["unlocked"]:
            self.data["unlocked"].append(skin_name)
            self.unlocked_skins = self.data["unlocked"]
            self.save()
            print(f"🔓 Unlocked skin: {skin_name}")
            return True
        return False

# Global instance (singleton)
skin_manager = SkinManager()

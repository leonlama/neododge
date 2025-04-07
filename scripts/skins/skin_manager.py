import json
import os
import arcade
import appdirs  # ✅ add this
from scripts.utils.resource_helper import resource_path
from scripts.utils.constants import DEFAULT_SKIN_PATH, MDMA_SKIN_PATH

# Path to user config folder (cross-platform safe)
APP_NAME = "Neododge"
USER_DATA_DIR = os.path.join(appdirs.user_data_dir(APP_NAME), "data")
os.makedirs(USER_DATA_DIR, exist_ok=True)

UNLOCKS_FILE = os.path.join(USER_DATA_DIR, "unlocks.json")

class SkinManager:
    def __init__(self, skin_path=DEFAULT_SKIN_PATH):
        self.skin_path = skin_path
        self.textures = {}  # Cache
        self.data = {
            "unlocked": ["default"],
            "selected": "default"
        }
        if os.path.exists(UNLOCKS_FILE):
            try:
                with open(UNLOCKS_FILE, "r") as f:
                    self.data = json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                self.save()
        else:
            self.save()

        self.skin_paths = {
            "default": DEFAULT_SKIN_PATH,
            "mdma": MDMA_SKIN_PATH
        }

    def get_path(self):
        return self.skin_paths.get(self.data["selected"], DEFAULT_SKIN_PATH)

    def get_texture_path(self, category, name):
        """Return full path to a skin texture like 'hearts/red.png' or 'orbs/shield.png'."""
        return os.path.join(self.skin_path, category, f"{name}.png")

    def get_texture(self, category, name):
        key = f"{category}/{name}"
        if key not in self.textures:
            texture_path = os.path.join(self.skin_path, category, f"{name}.png")
            self.textures[key] = arcade.load_texture(resource_path(texture_path))
        return self.textures[key]

    def unlock(self, skin_name):
        if skin_name not in self.data["unlocked"]:
            self.data["unlocked"].append(skin_name)
            self.save()

    def select(self, skin_name):
        if skin_name in self.data["unlocked"]:
            self.data["selected"] = skin_name
            self.save()

    def is_unlocked(self, skin_name):
        return skin_name in self.data["unlocked"]

    def save(self):
        with open(UNLOCKS_FILE, "w") as f:
            json.dump(self.data, f, indent=4)

# Create a global instance of SkinManager that can be imported by other modules
skin_manager = SkinManager(MDMA_SKIN_PATH)  # You can later use get_path() to switch dynamically

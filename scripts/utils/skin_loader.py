import os
import arcade
from pathlib import Path
from .constants import SKINS_DIR, DEFAULT_SKIN_PATH, MDMA_SKIN_PATH  # Import the skin paths

class SkinManager:
    def __init__(self):
        self.assets = {
            "default": {
                "player": {},
                "orbs": {},
                "artifacts": {},
                "enemies": {},
                "bullets": {},
                "hearts": {},
                "coins": {},
            },
            "mdma": {
                "player": {},
                "orbs": {},
                "artifacts": {},
                "enemies": {},
                "bullets": {},
                "hearts": {},
                "coins": {},
            }
        }
        self.current_skin = "default"
        self.skin_paths = {
            "default": DEFAULT_SKIN_PATH,
            "mdma": MDMA_SKIN_PATH
        }
        # Add this line to track unlocked skins
        self.unlocked_skins = ["default", "mdma"]  # Unlock all skins for testing
        
    def load_skin(self, skin_name: str) -> bool:
        if skin_name not in self.skin_paths:
            print(f"❌ Skin {skin_name} not found in available skins")
            return False
            
        skin_path = Path(self.skin_paths[skin_name])
        
        if not skin_path.exists():
            print(f"❌ Skin path not found: {skin_path}")
            return False
            
        try:
            self.assets[skin_name] = {
                "player": self._load_textures(skin_path / "player"),
                "hearts": self._load_textures(skin_path / "hearts"),
                "orbs": self._load_textures(skin_path / "orbs"),
                "artifacts": self._load_textures(skin_path / "artifacts")
            }
            self.current_skin = skin_name
            arcade.cleanup_texture_cache()
            print(f"✅ Loaded skin: {skin_name}")
            return True
            
        except Exception as e:
            print(f"❌ Error loading skin {skin_name}: {str(e)}")
            return False
            
    def _load_textures(self, folder: Path) -> dict:
        textures = {}
        for file in folder.glob("*.png"):
            textures[file.stem] = arcade.load_texture(file)
        return textures

    def get_asset(self, category: str, name: str):
        return self.assets[self.current_skin][category][name]
        
    def unlock_skin(self, skin_name):
        """Unlock a skin"""
        if skin_name not in self.unlocked_skins:
            self.unlocked_skins.append(skin_name)
            print(f"🔓 Unlocked skin: {skin_name}")
            return True
        return False
"""Skin manager for handling different visual styles."""

import os
import json
import arcade
from src.core.resource_manager import resource_path

class SkinManager:
    def __init__(self):
        self.data = {
            "skins": {},
            "selected": "default",
            "shared": {},
            "unlocked": ["default", "mdma"]
        }
        self.textures = {}
        self.scales = {
            "default": {
                "player": 0.045,
                "heart": 0.035,
                "artifact": 0.17,
                "orb": 0.17
            },
            "mdma": {
                "player": 0.045,
                "heart": 0.035,
                "artifact": 0.035,
                "orb": 0.035
            }
        }

    def load_skins(self):
        """Load all available skins from the skins directory."""
        print("?? [INIT] Initializing skin manager")

        # Load skin data from JSON file
        try:
            with open(resource_path("assets/skins/skins.json"), "r") as f:
                self.data = json.load(f)
                # Ensure unlocked list exists
                if "unlocked" not in self.data:
                    self.data["unlocked"] = ["default", "mdma"]
        except Exception as e:
            print(f"Error loading skins.json: {e}")
            # Create default skin data
            self.data = {
                "skins": {
                    "default": {
                        "name": "Default",
                        "description": "The default skin"
                    },
                    "mdma": {
                        "name": "MDMA",
                        "description": "Trippy skin"
                    }
                },
                "selected": "default",
                "shared": {},
                "unlocked": ["default", "mdma"]
            }

        # Preload all textures
        self.textures = {}

        # Load textures for each skin
        for skin_id in self.data["skins"]:
            self.textures[skin_id] = {}

            # Player texture
            try:
                self.textures[skin_id]["player/default"] = arcade.load_texture(
                    resource_path(f"assets/skins/{skin_id}/player/default.png")
                )
            except Exception as e:
                print(f"Error loading texture player/default for skin {skin_id}: {e}")

            # Orb textures
            for orb_type in ["speed", "shield", "cooldown", "multiplier", "vision", "hitbox"]:
                try:
                    self.textures[skin_id][f"orbs/{orb_type}"] = arcade.load_texture(
                        resource_path(f"assets/skins/{skin_id}/orbs/{orb_type}.png")
                    )
                except Exception as e:
                    print(f"Error loading texture orbs/{orb_type} for skin {skin_id}: {e}")

            # Artifact textures
            for artifact_type in ["dash", "magnet", "slow", "bullet_time", "clone"]:
                try:
                    self.textures[skin_id][f"artifacts/{artifact_type}"] = arcade.load_texture(
                        resource_path(f"assets/skins/{skin_id}/artifacts/{artifact_type}.png")
                    )
                except Exception as e:
                    print(f"Error loading texture artifacts/{artifact_type} for skin {skin_id}: {e}")

        # Load shared assets
        self.textures["shared"] = {}

        # Heart textures
        try:
            self.textures["shared"]["hearts/red"] = arcade.load_texture(
                resource_path("assets/ui/heart_red.png")
            )
            self.textures["shared"]["hearts/gray"] = arcade.load_texture(
                resource_path("assets/ui/heart_gray.png")
            )
            self.textures["shared"]["hearts/gold"] = arcade.load_texture(
                resource_path("assets/ui/heart_gold.png")
            )
        except Exception as e:
            print(f"Error loading heart textures: {e}")

        # Coin textures
        try:
            self.textures["shared"]["coins/gold"] = arcade.load_texture(
                resource_path("assets/items/coin/gold_coin.png")
            )
        except Exception as e:
            print(f"Error loading coin texture: {e}")

    def select(self, skin_id):
        """Select a skin by ID."""
        if skin_id in self.data["skins"]:
            self.data["selected"] = skin_id
            print(f"?? [INIT] Using skin: {skin_id}")
            return True
        else:
            print(f"Skin {skin_id} not found, using default")
            self.data["selected"] = "default"
            return False

    def get_texture(self, category, item_id):
        """Get a texture by category and item ID for the currently selected skin."""
        skin_id = self.data["selected"]
        texture_id = f"{category}/{item_id}"

        # Check if texture exists in current skin
        if skin_id in self.textures and texture_id in self.textures[skin_id]:
            return self.textures[skin_id][texture_id]

        # Check if texture exists in shared assets
        if texture_id.startswith("hearts/") or texture_id.startswith("coins/"):
            if "shared" in self.textures and texture_id in self.textures["shared"]:
                return self.textures["shared"][texture_id]

        # Check if texture exists in default skin as fallback
        if "default" in self.textures and texture_id in self.textures["default"]:
            return self.textures["default"][texture_id]

        # Return None if texture not found
        print(f"Texture {texture_id} not found in skin {skin_id}")
        return None

    def get_player_scale(self):
        """Get the scale for player based on the current skin."""
        skin_id = self.data["selected"]
        return self.scales.get(skin_id, {}).get("player", 0.045)

    def get_heart_scale(self):
        """Get the scale for hearts based on the current skin."""
        skin_id = self.data["selected"]
        return self.scales.get(skin_id, {}).get("heart", 0.035)

    def get_artifact_scale(self):
        """Get the scale for artifacts based on the current skin."""
        skin_id = self.data["selected"]
        return self.scales.get(skin_id, {}).get("artifact", 0.17)

    def get_orb_scale(self):
        """Get the scale for orbs based on the current skin."""
        skin_id = self.data["selected"]
        return self.scales.get(skin_id, {}).get("orb", 0.17)

    def get_selected(self):
        """Get the currently selected skin ID."""
        return self.data["selected"]

# Create a singleton instance
skin_manager = SkinManager()

def preload_all_skins():
    """Preload all skins."""
    skin_manager.load_skins()
    skin_manager.select("default")

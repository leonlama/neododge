import arcade

from scripts.utils.constants import MDMA_SKIN_PATH
from scripts.skins.skin_manager import skin_manager
from scripts.utils.orb_utils import get_texture_name_from_orb_type

class BuffOrb(arcade.Sprite):
    def __init__(self, x, y, orb_type="gray"):
        super().__init__()
        self.orb_type = orb_type
        self.age = 0

        self.color_map = {
            "gray": arcade.color.GRAY,
            "red": arcade.color.RED,
            "gold": arcade.color.GOLD,
            "speed_10": arcade.color.BLUE_BELL,
            "speed_20": arcade.color.BLUE_VIOLET,
            "speed_35": arcade.color.DARK_BLUE,
            "mult_1_5": arcade.color.ORANGE,
            "mult_2": arcade.color.YELLOW_ORANGE,
            "cooldown": arcade.color.PURPLE,
            "shield": arcade.color.LIGHT_GREEN,
        }

        self.update_texture()
        
        self.center_x = x
        self.center_y = y

        self.message = {
            "gray": "🩶 Bonus heart slot gained!",
            "red": "❤️ Heart restored!",
            "gold": "💛 Golden heart gained!",
            "speed_10": "⚡ Speed +10%",
            "speed_20": "⚡ Speed +20%",
            "speed_35": "⚡ Speed +35%",
            "mult_1_5": "💥 Score x1.5 for 30s",
            "mult_2": "💥 Score x2 for 30s",
            "cooldown": "🔁 Cooldown reduced!",
            "shield": "🛡️ Shield acquired!",
        }.get(self.orb_type, "✨ Buff Orb")

    def update_texture(self):
        """Update the texture based on current skin settings"""
        # Get the texture name for this orb type
        texture_name = get_texture_name_from_orb_type(self.orb_type)
        
        # Get the texture from skin manager with force_reload=True to ensure we get the latest texture
        self.texture = skin_manager.get_texture("orbs", texture_name, force_reload=True)
        
        # If texture is None, use the fallback
        if self.texture is None:
            # Create a fallback texture
            color = self.color_map.get(self.orb_type, arcade.color.WHITE)
            self.texture = arcade.make_soft_circle_texture(18, color, outer_alpha=255)
            
        # Apply the appropriate scale
        self.scale = skin_manager.get_orb_scale()

    def update(self, delta_time: float = 1 / 60):
        self.age += delta_time
        # Update texture each frame to ensure current skin is used
        self.update_texture()

    def apply_effect(self, player):
        """Apply the orb effect to the player"""
        if self.orb_type == "gray":
            player.max_slots += 1
            print(self.message)
        elif self.orb_type == "red":
            if player.current_hearts < player.max_slots:
                player.current_hearts += 1
                print(self.message)
            else:
                print("❌ No empty slot for red orb.")
        elif self.orb_type == "gold":
            player.gold_hearts += 1
            print(self.message)
        elif "speed" in self.orb_type:
            if self.orb_type == "speed_10":
                player.apply_orb_effect("speed", 45.0, 1.1)
                player.active_orbs.append(["⚡ Speed +10%", 45])
            elif self.orb_type == "speed_20":
                player.apply_orb_effect("speed", 40.0, 1.2)
                player.active_orbs.append(["⚡ Speed +20%", 40])
            elif self.orb_type == "speed_35":
                player.apply_orb_effect("speed", 30.0, 1.35)
                player.active_orbs.append(["⚡ Speed +35%", 30])
            print(self.message)
        elif "mult" in self.orb_type:
            if self.orb_type == "mult_1_5":
                player.apply_orb_effect("multiplier", 30.0, 1.5)
                player.active_orbs.append(["Score x1.5", 30])
            elif self.orb_type == "mult_2":
                player.apply_orb_effect("multiplier", 30.0, 2.0)
                player.active_orbs.append(["Score x2", 30])
            print(self.message)
        elif "cooldown" in self.orb_type:
            self.message = "🔁 Cooldown reduced! (20%)"
            player.apply_orb_effect("cooldown", 30.0, 0.8)
            print(self.message)
        elif "shield" in self.orb_type:
            player.shield = True
            print(self.message)

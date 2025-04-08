import arcade

from src.core.constants import MDMA_SKIN_PATH
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
            player.max_slots += 1  # Use max_slots instead of max_hearts
            self.message = "Max Health Increased!"
        elif self.orb_type == "red":
            if player.current_hearts < player.max_slots:
                player.current_hearts += 1
                self.message = "Health Restored!"
            else:
                self.message = "Health Already Full!"
        elif self.orb_type == "gold":
            player.gold_hearts += 1  # Use gold_hearts instead of golden_hearts
            self.message = "Gold Heart Added!"
        elif self.orb_type == "speed_10":
            player.apply_orb_effect("speed", 10.0, 1.1)
            self.message = "Speed +10%!"
        elif self.orb_type == "speed_20":
            player.apply_orb_effect("speed", 10.0, 1.2)
            self.message = "Speed +20%!"
        elif self.orb_type == "speed_35":
            player.apply_orb_effect("speed", 10.0, 1.35)
            self.message = "Speed +35%!"
        elif self.orb_type == "mult_1_5":
            player.apply_orb_effect("multiplier", 30.0, 1.5)
            self.message = "Score x1.5!"
        elif self.orb_type == "mult_2":
            player.apply_orb_effect("multiplier", 30.0, 2.0)
            self.message = "Score x2!"
        elif self.orb_type == "cooldown":
            player.apply_orb_effect("cooldown", 10.0, 0.8)
            self.message = "Cooldown -20%!"
        elif self.orb_type == "shield":
            player.shield = True
            self.message = "Shield Active!"


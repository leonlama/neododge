import arcade
import random

class Orb(arcade.Sprite):
    def __init__(self, x, y, orb_type="gray"):
        super().__init__()
        self.orb_type = orb_type
        self.age = 0

        # 10% chance to make it a debuff
        self.is_debuff = random.random() < 0.1
        if self.is_debuff:
            self.orb_type = self.convert_to_debuff(orb_type)

        # Colors (same visuals for now)
        color_map = {
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
            # Debuffs use same colors to trick player
            "slow": arcade.color.BLUE_BELL,
            "mult_down_0_5": arcade.color.ORANGE,
            "mult_down_0_25": arcade.color.YELLOW_ORANGE,
            "cooldown_up": arcade.color.PURPLE,
            "inverse_move": arcade.color.GRAY,
            "vision_blur": arcade.color.GOLD,
            "big_hitbox": arcade.color.RED,
        }

        color = color_map.get(self.orb_type, arcade.color.WHITE)
        self.texture = arcade.make_soft_circle_texture(18, color, outer_alpha=255)
        self.center_x = x
        self.center_y = y

    def update(self, delta_time: float = 1 / 60):
        self.age += delta_time

    def convert_to_debuff(self, orb_type):
        """Map a good orb type to a similar debuff type."""
        mapping = {
            "gray": "big_hitbox",
            "red": "slow",
            "gold": "vision_blur",
            "speed_10": "slow",
            "speed_20": "slow",
            "speed_35": "slow",
            "mult_1_5": "mult_down_0_5",
            "mult_2": "mult_down_0_25",
            "cooldown": "cooldown_up",
            "shield": "inverse_move"
        }
        return mapping.get(orb_type, orb_type)  # fallback to same if no mapping

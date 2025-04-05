import arcade
import random

class DebuffOrb(arcade.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.orb_type = random.choice([
            "slow", "big_hitbox", "mult_down_0_5",
            "mult_down_0_25", "cooldown_up", "inverse_move", "vision_blur"
        ])
        self.age = 0
        self.message = {
            "slow": "🐢 Speed -20%",
            "mult_down_0_5": "💥 Score x0.5 for 30s",
            "mult_down_0_25": "💥 Score x0.25 for 30s",
            "cooldown_up": "🔁 Cooldown increased!",
            "inverse_move": "🔄 Inverse Move",
            "vision_blur": "👁️ Vision Blur",
            "big_hitbox": "⬛ Big Hitbox",
        }.get(self.orb_type, "⚠️ Debuff Orb")

        color_map = {
            "slow": arcade.color.DARK_BLUE_GRAY,
            "big_hitbox": arcade.color.DARK_GRAY,
            "mult_down_0_5": arcade.color.DARK_GOLDENROD,
            "mult_down_0_25": arcade.color.DARK_ORANGE,
            "cooldown_up": arcade.color.DARK_MAGENTA,
            "inverse_move": arcade.color.DARK_BROWN,
            "vision_blur": arcade.color.DARK_SLATE_GRAY
        }

        color = color_map.get(self.orb_type, arcade.color.GRAY)
        self.texture = arcade.make_soft_circle_texture(18, color, outer_alpha=255)
        self.center_x = x
        self.center_y = y

    def apply_effect(self, player):
        if self.orb_type == "slow":
            player.speed_bonus -= 0.2
            player.active_orbs.append(["🐢 Speed -20%", 30])
            print(self.message)

        elif self.orb_type == "big_hitbox":
            player.hitbox_scale = 2.0
            player.active_orbs.append(["⬛ Big Hitbox", 30])
            print(self.message)

        elif self.orb_type == "mult_down_0_5":
            player.multiplier = 0.5
            player.mult_timer = 30
            player.active_orbs.append(["💥 Score x0.5", 30])
            print(self.message)

        elif self.orb_type == "mult_down_0_25":
            player.multiplier = 0.25
            player.mult_timer = 30
            player.active_orbs.append(["💥 Score x0.25", 30])
            print(self.message)

        elif self.orb_type == "cooldown_up":
            player.cooldown_factor = 2.0
            player.active_orbs.append(["🔁 Cooldown ↑", 15])
            print(self.message)

        elif self.orb_type == "inverse_move":
            player.inverse_move = True
            player.active_orbs.append(["🔄 Inverse Move", 30])
            print(self.message)

        elif self.orb_type == "vision_blur":
            player.vision_blur = True
            player.vision_timer = 15.0
            player.active_orbs.append(["👁️ Vision Blur", 30])
            print(self.message)

    def update(self, delta_time: float = 1 / 60):
        self.age += delta_time

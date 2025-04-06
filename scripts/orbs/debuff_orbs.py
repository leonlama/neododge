import arcade

class DebuffOrb(arcade.Sprite):
    def __init__(self, x, y, orb_type="inverse"):
        super().__init__()
        self.orb_type = orb_type
        self.age = 0
        self.message = {
            "slow": "🐢 Speed -20%",
            "mult_down_0_5": "💥 Score x0.5 for 30s",
            "mult_down_0_25": "💥 Score x0.25 for 30s",
            "cooldown_up": "🔁 Cooldown increased!",
            "inverse_move": "🔄 Inverse Move",
            "vision_blur": "👁️ Vision Blur",
            "big_hitbox": "⬛ Big Hitbox"
        }.get(orb_type, "⚠️ Debuff Orb")

        color_map = {
            "slow": arcade.color.LIGHT_GRAY,
            "mult_down_0_5": arcade.color.DARK_GOLDENROD,
            "mult_down_0_25": arcade.color.BRONZE,
            "cooldown_up": arcade.color.DARK_MAGENTA,
            "inverse_move": arcade.color.DARK_BROWN,
            "vision_blur": arcade.color.DARK_SLATE_GRAY,
            "big_hitbox": arcade.color.LIGHT_YELLOW,
            "inverse": arcade.color.LIGHT_PINK  # default color for inverse if not specified
        }
        color = color_map.get(orb_type, arcade.color.WHITE)
        self.texture = arcade.make_soft_circle_texture(18, color, outer_alpha=255)
        self.center_x = x
        self.center_y = y

    def update(self, delta_time: float = 1 / 60):
        self.age += delta_time

    def apply_effect(self, player):
        if self.orb_type == "slow":
            player.speed_bonus -= 0.2
            player.active_orbs.append(["🐢 Speed -20%", 30])
            print("🐢 Speed -20%")
        elif self.orb_type == "big_hitbox":
            if not hasattr(player, "original_size"):
                player.original_size = (player.width, player.height)
            player.width = player.original_size[0] * 1.5
            player.height = player.original_size[1] * 1.5
            player.set_hit_box(player.texture.hit_box_points)
            player.active_orbs.append(["⬛ Big Hitbox", 30])
            print("⬛ Big Hitbox applied")
        elif self.orb_type == "mult_down_0_5":
            player.multiplier = 0.5
            player.mult_timer = 30
            player.active_orbs.append(["Score x0.5", 30])
            print("💥 Score x0.5 for 30s")
        elif self.orb_type == "mult_down_0_25":
            player.multiplier = 0.25
            player.mult_timer = 30
            player.active_orbs.append(["Score x0.25", 30])
            print("💥 Score x0.25 for 30s")
        elif self.orb_type == "cooldown_up":
            player.cooldown_factor = 2.0
            player.active_orbs.append(["⏱️ Cooldown ↑", 15])
            print("🔁 Cooldown increased!")
        elif self.orb_type == "inverse_move":
            player.inverse_move = True
            player.active_orbs.append(["🔄 Inverse Move", 30])
            print("🔄 Inverse Move")
        elif self.orb_type == "vision_blur":
            player.vision_blur = True
            player.vision_timer = 30
            player.active_orbs.append(["👁️ Vision Blur", 30])
            print("👁️ Vision Blur")
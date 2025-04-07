import arcade
from scripts.skins.skin_manager import skin_manager
from scripts.utils.orb_utils import get_texture_name_from_orb_type

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
            #"inverse_move": "🔄 Inverse Move",
            "vision": "👁️ Vision Blur",
            "hitbox": "⬛ Big Hitbox"
        }.get(orb_type, "⚠️ Debuff Orb")

        self.color_map = {
            "slow": arcade.color.LIGHT_GRAY,
            "mult_down_0_5": arcade.color.DARK_GOLDENROD,
            "mult_down_0_25": arcade.color.BRONZE,
            "cooldown_up": arcade.color.DARK_MAGENTA,
            #"inverse_move": arcade.color.DARK_BROWN,
            "vision": arcade.color.DARK_SLATE_GRAY,
            "hitbox": arcade.color.LIGHT_YELLOW,
            "inverse": arcade.color.LIGHT_PINK  # default color for inverse if not specified
        }
        
        self.update_texture()
        
        self.center_x = x
        self.center_y = y

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
        if self.orb_type == "slow":
            self.message = "🐢 Speed -20%"
            player.speed_bonus -= 0.2
            player.active_orbs.append(["🐢 Speed -20%", 30])
            print(self.message)
        elif self.orb_type == "hitbox":
            self.message = "⬛ Big Hitbox applied"
            if not hasattr(player, "original_size"):
                player.original_size = (player.width, player.height)
            player.width = player.original_size[0] * 1.5
            player.height = player.original_size[1] * 1.5
            player.set_hit_box(player.texture.hit_box_points)
            player.active_orbs.append(["⬛ Big Hitbox", 30])
            print(self.message)
        elif self.orb_type == "mult_down_0_5":
            self.message = "💥 Score x0.5 for 30s"
            player.multiplier = 0.5
            player.mult_timer = 30
            player.active_orbs.append(["Score x0.5", 30])
            print(self.message)
        elif self.orb_type == "mult_down_0_25":
            self.message = "💥 Score x0.25 for 30s"
            player.multiplier = 0.25
            player.mult_timer = 30
            player.active_orbs.append(["Score x0.25", 30])
            print(self.message)
        elif self.orb_type == "cooldown_up":
            self.message = "🔁 Cooldown increased!"
            player.cooldown_factor = 2.0
            player.active_orbs.append(["⏱️ Cooldown ↑", 15])
            print(self.message)
        elif self.orb_type == "inverse_move":
            self.message = "🔄 Inverse Move"
            player.inverse_move = True
            player.active_orbs.append(["🔄 Inverse Move", 30])
            print(self.message)
        elif self.orb_type == "vision":
            self.message = "👁️ Vision Blur"
            player.vision_blur = True
            player.vision_timer = 30
            player.active_orbs.append(["👁️ Vision Blur", 30])
            print(self.message)
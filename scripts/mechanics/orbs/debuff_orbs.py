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
        """Apply the debuff effect to the player"""
        if self.orb_type == "slow":
            player.apply_orb_effect("speed", 5.0, 0.8)
        elif self.orb_type == "mult_down_0_5":
            player.apply_orb_effect("multiplier", 30.0, 0.5)
        elif self.orb_type == "mult_down_0_25":
            player.apply_orb_effect("multiplier", 30.0, 0.25)
        elif self.orb_type == "cooldown_up":
            player.apply_orb_effect("cooldown", 5.0, 1.5)
        elif self.orb_type == "vision":
            player.apply_orb_effect("vision", 5.0, True)
        elif self.orb_type == "hitbox":
            player.apply_orb_effect("hitbox", 5.0, 1.3)
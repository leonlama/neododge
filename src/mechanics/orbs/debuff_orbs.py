import arcade
import random
from src.mechanics.orbs.orb import Orb
from src.skins.skin_manager import skin_manager
from src.core.scaling import get_scale

class DebuffOrb(Orb):
    """Orb that provides negative effects to the player"""

    def __init__(self, x, y, orb_type="slow"):
        super().__init__(x, y, orb_type)

        # Set properties specific to debuff orbs
        self.effect_duration = random.uniform(3, 7)  # Duration of the debuff effect

        # Set texture based on orb type
        self.set_texture()
        
        # Set scale using centralized system
        self.scale = get_scale('orb')

    def set_texture(self):
        """Set the texture based on orb type."""
        # Get texture from skin manager based on orb type
        texture_name = self.get_texture_name()
        self.texture = skin_manager.get_texture("orbs", texture_name)

        # If no texture found, create a default one
        if not self.texture:
            # Use make_soft_circle_texture instead of make_circle_texture with soft=True
            self.texture = arcade.make_soft_circle_texture(
                32, 
                arcade.color.RED
            )

    def get_texture_name(self):
        """Get the texture name based on orb type."""
        if "slow" in self.orb_type:
            return "slow"
        elif "mult_down" in self.orb_type:
            return "multiplier"
        elif "cooldown_up" in self.orb_type:
            return "cooldown"
        elif "vision_blur" in self.orb_type:
            return "vision"
        elif "big_hitbox" in self.orb_type:
            return "hitbox"
        else:
            return "slow"  # Default

    def apply_effect(self, player):
        """Apply the debuff effect to the player."""
        if "slow" in self.orb_type:
            player.apply_effect("speed", -30, self.effect_duration)  # 30% speed reduction
            
        elif "mult_down" in self.orb_type:
            # Extract multiplier value from orb type
            try:
                mult_parts = self.orb_type.split('_')
                if len(mult_parts) > 2:
                    # Handle format like "mult_down_0_5" (0.5x)
                    mult_value = float(f"{mult_parts[2]}.{mult_parts[3]}")
                    # Convert to percentage (e.g., 0.5 -> -50%)
                    percentage = int((mult_value - 1) * 100)
                else:
                    # Direct percentage format
                    percentage = -int(mult_parts[2])
                    
                player.apply_effect("mult", percentage, self.effect_duration)
            except:
                # Default multiplier if parsing fails
                player.apply_effect("mult", -50, self.effect_duration)
                
        elif "cooldown_up" in self.orb_type:
            player.apply_effect("cooldown", -50, self.effect_duration)  # 50% cooldown increase
            
        elif "vision_blur" in self.orb_type:
            player.apply_effect("vision", 1, self.effect_duration, is_percentage=False)
            
        elif "big_hitbox" in self.orb_type:
            player.apply_effect("hitbox", 50, self.effect_duration)  # 50% larger hitbox
            
        # Play debuff sound if available
        if hasattr(player.parent_view, 'play_debuff_sound'):
            player.parent_view.play_debuff_sound()
        elif hasattr(player.parent_view, 'debuff_sound'):
            arcade.play_sound(player.parent_view.debuff_sound)
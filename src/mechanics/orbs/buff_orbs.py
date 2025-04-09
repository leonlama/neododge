import arcade
import random
from src.mechanics.orbs.orb import Orb
from src.skins.skin_manager import skin_manager
from src.core.scaling import get_scale

class BuffOrb(Orb):
    """Orb that provides positive effects to the player"""

    def __init__(self, x, y, orb_type="speed_10"):
        super().__init__(x, y, orb_type)

        # Set properties specific to buff orbs
        self.color = arcade.color.GREEN
        self.effect_duration = random.uniform(5, 10)  # Duration of the buff effect

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
                self.color
            )

    def get_texture_name(self):
        """Get the texture name based on orb type."""
        if "speed" in self.orb_type:
            return "speed"
        elif "mult" in self.orb_type:
            return "multiplier"
        elif "cooldown" in self.orb_type:
            return "cooldown"
        elif "shield" in self.orb_type:
            return "shield"
        else:
            return "speed"  # Default

    def apply_effect(self, player):
        """Apply the buff effect to the player."""
        if "speed" in self.orb_type:
            # Extract speed value from orb type (e.g., "speed_10" -> 10% speed increase)
            try:
                speed_value = int(self.orb_type.split('_')[1])
                player.apply_effect("speed", speed_value, self.effect_duration)
            except:
                # Default speed boost if parsing fails
                player.apply_effect("speed", 20, self.effect_duration)
                
        elif "shield" in self.orb_type:
            player.apply_effect("shield", 1, self.effect_duration, is_percentage=False)
            
        elif "mult" in self.orb_type:
            # Extract multiplier value from orb type
            try:
                mult_parts = self.orb_type.split('_')
                if len(mult_parts) > 2:
                    # Handle format like "mult_1_5" (1.5x)
                    mult_value = float(f"{mult_parts[1]}.{mult_parts[2]}")
                    # Convert to percentage (e.g., 1.5 -> 50%)
                    percentage = int((mult_value - 1) * 100)
                else:
                    # Direct percentage format
                    percentage = int(mult_parts[1])
                    
                player.apply_effect("mult", percentage, self.effect_duration)
            except:
                # Default multiplier if parsing fails
                player.apply_effect("mult", 50, self.effect_duration)
                
        elif "cooldown" in self.orb_type:
            # 25% cooldown reduction
            player.apply_effect("cooldown", 25, self.effect_duration)
            
        # Play buff sound if available
        if hasattr(player.parent_view, 'play_buff_sound'):
            player.parent_view.play_buff_sound()
        elif hasattr(player.parent_view, 'buff_sound'):
            arcade.play_sound(player.parent_view.buff_sound)
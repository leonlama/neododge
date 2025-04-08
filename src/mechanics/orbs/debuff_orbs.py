import arcade
import random
from src.mechanics.orbs.orb import Orb
from src.skins.skin_manager import skin_manager

class DebuffOrb(Orb):
    """Orb that provides negative effects to the player"""

    def __init__(self, x, y, orb_type="slow"):
        super().__init__(x, y, orb_type)

        # Set properties specific to debuff orbs
        self.color = arcade.color.RED
        self.effect_duration = random.uniform(3, 7)  # Duration of the debuff effect

        # Set texture based on orb type
        self.set_texture()

    def set_texture(self):
        """Set the texture based on orb type"""
        # Get texture from skin manager based on orb type
        texture_name = self.get_texture_name()
        self.texture = skin_manager.get_texture(texture_name)

        # If no texture found, create a default one
        if not self.texture:
            self.texture = arcade.make_circle_texture(
                32, 
                self.color, 
                soft=True
            )

    def get_texture_name(self):
        """Get the texture name based on orb type"""
        if "slow" in self.orb_type:
            return "speed"  # Use same texture but will be red
        elif "mult_down" in self.orb_type:
            return "multiplier"
        elif "cooldown_up" in self.orb_type:
            return "cooldown"
        elif "vision_blur" in self.orb_type:
            return "vision"
        elif "big_hitbox" in self.orb_type:
            return "hitbox"
        else:
            return "speed"  # Default

    def apply_effect(self, player):
        """Apply the debuff effect to the player"""
        # Apply different effects based on orb type
        if "slow" in self.orb_type:
            # Slow down player
            player.base_speed *= 0.7

            # Add effect to player's active effects
            player.parent_view.add_effect(
                "slow", 
                0.7, 
                self.effect_duration,
                arcade.color.RED,
                "speed"
            )

            # Add pickup message
            if hasattr(player, 'pickup_texts'):
                player.pickup_texts.append([
                    "-30% Speed", 
                    player.center_x, 
                    player.center_y, 
                    2.0
                ])

        elif "mult_down" in self.orb_type:
            # Extract multiplier value from orb type (e.g., "mult_down_0_5" -> 0.5x score multiplier)
            try:
                mult_parts = self.orb_type.split('_')
                mult_value = float(f"{mult_parts[2]}.{mult_parts[3]}" if len(mult_parts) > 3 else mult_parts[2])
                player.score_multiplier *= mult_value

                # Add effect to player's active effects
                player.parent_view.add_effect(
                    "multiplier_down", 
                    mult_value, 
                    self.effect_duration,
                    arcade.color.RED,
                    "multiplier"
                )

                # Add pickup message
                if hasattr(player, 'pickup_texts'):
                    player.pickup_texts.append([
                        f"{mult_value}x Score", 
                        player.center_x, 
                        player.center_y, 
                        2.0
                    ])
            except:
                pass

        elif "cooldown_up" in self.orb_type:
            # Increase dash cooldown
            player.dash_cooldown_max *= 1.5

            # Add effect to player's active effects
            player.parent_view.add_effect(
                "cooldown_up", 
                1.5, 
                self.effect_duration,
                arcade.color.RED,
                "cooldown"
            )

            # Add pickup message
            if hasattr(player, 'pickup_texts'):
                player.pickup_texts.append([
                    "+50% Dash Cooldown", 
                    player.center_x, 
                    player.center_y, 
                    2.0
                ])

        elif "vision_blur" in self.orb_type:
            # Add vision blur effect
            player.vision_blur = True

            # Add effect to player's active effects
            player.parent_view.add_effect(
                "vision_blur", 
                1.0, 
                self.effect_duration,
                arcade.color.PURPLE,
                "vision"
            )

            # Add pickup message
            if hasattr(player, 'pickup_texts'):
                player.pickup_texts.append([
                    "Vision Blurred", 
                    player.center_x, 
                    player.center_y, 
                    2.0
                ])

        elif "big_hitbox" in self.orb_type:
            # Increase player hitbox
            player.scale *= 1.5

            # Add effect to player's active effects
            player.parent_view.add_effect(
                "big_hitbox", 
                1.5, 
                self.effect_duration,
                arcade.color.ORANGE,
                "hitbox"
            )

            # Add pickup message
            if hasattr(player, 'pickup_texts'):
                player.pickup_texts.append([
                    "+50% Hitbox Size", 
                    player.center_x, 
                    player.center_y, 
                    2.0
                ])

        # Play debuff sound if available
        if hasattr(player.parent_view, 'debuff_sound'):
            arcade.play_sound(player.parent_view.debuff_sound)
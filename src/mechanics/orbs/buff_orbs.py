import arcade
import random
from src.mechanics.orbs.orb import Orb
from src.skins.skin_manager import skin_manager

class BuffOrb(Orb):
    """Orb that provides positive effects to the player"""

    def __init__(self, x, y, orb_type="speed_10"):
        super().__init__(x, y, orb_type)

        # Set properties specific to buff orbs
        self.color = arcade.color.GREEN
        self.effect_duration = random.uniform(5, 10)  # Duration of the buff effect

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
        """Apply the buff effect to the player"""
        # Apply different effects based on orb type
        if "speed" in self.orb_type:
            # Extract speed value from orb type (e.g., "speed_10" -> 10% speed increase)
            try:
                speed_value = int(self.orb_type.split('_')[1])
                speed_multiplier = 1 + (speed_value / 100)
                player.base_speed *= speed_multiplier

                # Add effect to player's active effects
                player.parent_view.add_effect(
                    "speed", 
                    speed_multiplier, 
                    self.effect_duration,
                    arcade.color.GREEN,
                    "speed"
                )

                # Add pickup message
                if hasattr(player, 'pickup_texts'):
                    player.pickup_texts.append([
                        f"+{speed_value}% Speed", 
                        player.center_x, 
                        player.center_y, 
                        2.0
                    ])
            except:
                pass

        elif "mult" in self.orb_type:
            # Extract multiplier value from orb type (e.g., "mult_1_5" -> 1.5x score multiplier)
            try:
                mult_parts = self.orb_type.split('_')
                mult_value = float(f"{mult_parts[1]}.{mult_parts[2]}" if len(mult_parts) > 2 else mult_parts[1])
                player.score_multiplier *= mult_value

                # Add effect to player's active effects
                player.parent_view.add_effect(
                    "multiplier", 
                    mult_value, 
                    self.effect_duration,
                    arcade.color.GOLD,
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

        elif "cooldown" in self.orb_type:
            # Reduce dash cooldown
            player.dash_cooldown_max *= 0.75

            # Add effect to player's active effects
            player.parent_view.add_effect(
                "cooldown", 
                0.75, 
                self.effect_duration,
                arcade.color.BLUE,
                "cooldown"
            )

            # Add pickup message
            if hasattr(player, 'pickup_texts'):
                player.pickup_texts.append([
                    "-25% Dash Cooldown", 
                    player.center_x, 
                    player.center_y, 
                    2.0
                ])

        elif "shield" in self.orb_type:
            # Add shield effect
            player.invincible = True
            player.invincible_timer = self.effect_duration

            # Add effect to player's active effects
            player.parent_view.add_effect(
                "shield", 
                1.0, 
                self.effect_duration,
                arcade.color.CYAN,
                "shield"
            )

            # Add pickup message
            if hasattr(player, 'pickup_texts'):
                player.pickup_texts.append([
                    "Shield Activated", 
                    player.center_x, 
                    player.center_y, 
                    2.0
                ])

        # Play buff sound if available
        if hasattr(player.parent_view, 'buff_sound'):
            arcade.play_sound(player.parent_view.buff_sound)
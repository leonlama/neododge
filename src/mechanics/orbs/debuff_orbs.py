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
        if self.orb_type == "slow":
            # Check if player has speed attribute
            if hasattr(player, 'speed'):
                player.speed *= 0.7  # Reduce speed by 30%
            elif hasattr(player, 'speed_multiplier'):
                player.speed_multiplier *= 0.7
            else:
                # Fallback - create a speed multiplier attribute
                player.speed_multiplier = 0.7

            # Set a timer for the effect if possible
            if hasattr(player, 'effect_timers'):
                player.effect_timers['slow'] = 5.0  # 5 seconds
            print("🐢 Player slowed!")

            # Add pickup message
            if hasattr(player, 'pickup_texts'):
                player.pickup_texts.append([
                    "-30% Speed", 
                    player.center_x, 
                    player.center_y, 
                    2.0
                ])

        elif self.orb_type == "mult_down_0_5":
            if hasattr(player, 'score_multiplier'):
                player.score_multiplier = 0.5
            elif hasattr(player, 'multiplier'):
                player.multiplier = 0.5

            # Set a timer for the effect if possible
            if hasattr(player, 'effect_timers'):
                player.effect_timers['multiplier'] = 30.0  # 30 seconds
            print("💥 Score x0.5 for 30s")

            # Add pickup message
            if hasattr(player, 'pickup_texts'):
                player.pickup_texts.append([
                    "0.5x Score", 
                    player.center_x, 
                    player.center_y, 
                    2.0
                ])

        elif self.orb_type == "mult_down_0_25":
            if hasattr(player, 'score_multiplier'):
                player.score_multiplier = 0.25
            elif hasattr(player, 'multiplier'):
                player.multiplier = 0.25

            # Set a timer for the effect if possible
            if hasattr(player, 'effect_timers'):
                player.effect_timers['multiplier'] = 30.0  # 30 seconds
            print("💥 Score x0.25 for 30s")

            # Add pickup message
            if hasattr(player, 'pickup_texts'):
                player.pickup_texts.append([
                    "0.25x Score", 
                    player.center_x, 
                    player.center_y, 
                    2.0
                ])

        elif self.orb_type == "cooldown_up":
            if hasattr(player, 'cooldown_multiplier'):
                player.cooldown_multiplier = 1.5  # Increase cooldown by 50%
            elif hasattr(player, 'dash_cooldown'):
                player.dash_cooldown *= 1.5
            print("🔁 Cooldown increased!")

            # Add pickup message
            if hasattr(player, 'pickup_texts'):
                player.pickup_texts.append([
                    "+50% Dash Cooldown", 
                    player.center_x, 
                    player.center_y, 
                    2.0
                ])

        elif self.orb_type == "vision_blur":
            player.vision_blur = True

            # Set a timer for the effect if possible
            if hasattr(player, 'effect_timers'):
                player.effect_timers['vision_blur'] = 10.0  # 10 seconds
            print("👁️ Vision blurred!")

            # Add pickup message
            if hasattr(player, 'pickup_texts'):
                player.pickup_texts.append([
                    "Vision Blurred", 
                    player.center_x, 
                    player.center_y, 
                    2.0
                ])

        elif self.orb_type == "big_hitbox":
            # Store original scale if not already stored
            if not hasattr(player, 'original_scale'):
                player.original_scale = player.scale

            # Increase hitbox size
            player.scale = player.original_scale * 1.5

            # Set a timer for the effect if possible
            if hasattr(player, 'effect_timers'):
                player.effect_timers['big_hitbox'] = 15.0  # 15 seconds
            print("⬛ Hitbox increased!")

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
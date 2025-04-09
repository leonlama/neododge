import arcade
import random
from src.core.scaling import get_scale

class Orb(arcade.Sprite):
    def __init__(self, x, y, orb_type="speed"):
        super().__init__()
        self.center_x = x
        self.center_y = y
        self.orb_type = orb_type
        self.effect_duration = 5.0  # seconds

        # Set appearance based on type
        self._set_appearance()
        
        # Set scale using centralized system
        self.scale = get_scale('orb')

    def _set_appearance(self):
        if self.orb_type in ["speed", "shield", "invincibility"]:
            color = arcade.color.BLUE
        else:
            color = arcade.color.PURPLE

        self.texture = arcade.make_soft_circle_texture(20, color)

    def apply_effect(self, player):
        """Apply orb effect to the player."""
        if self.orb_type == "speed":
            player.speed_multiplier = 1.5
            player.speed_boost_timer = self.effect_duration
        elif self.orb_type == "shield":
            player.has_shield = True
            player.shield_timer = self.effect_duration
        elif self.orb_type == "slow":
            player.speed_multiplier = 0.5
            player.slow_timer = self.effect_duration
        elif self.orb_type == "damage":
            player.take_damage(1)
        # Add more effects as needed

class OrbManager:
    """Manages orb creation and effects."""

    def __init__(self):
        self.orb_types = {
            "buff": ["speed", "shield", "invincibility"],
            "debuff": ["slow", "damage"]
        }

    def create_orb(self, orb_type, x, y):
        """Create an orb of the specified type."""
        return Orb(x, y, orb_type)

    def create_random_orb(self, x, y, favor_buffs=True):
        """Create a random orb, with optional bias toward buffs."""
        if favor_buffs and random.random() < 0.7:
            orb_type = random.choice(self.orb_types["buff"])
        else:
            orb_type = random.choice(self.orb_types["buff"] + self.orb_types["debuff"])

        return self.create_orb(orb_type, x, y)

    def update_player_orb_effects(self, player, delta_time):
        """Update orb effect timers on the player."""
        # Speed boost
        if hasattr(player, "speed_boost_timer") and player.speed_boost_timer > 0:
            player.speed_boost_timer -= delta_time
            if player.speed_boost_timer <= 0:
                player.speed_multiplier = 1.0

        # Shield
        if hasattr(player, "shield_timer") and player.shield_timer > 0:
            player.shield_timer -= delta_time
            if player.shield_timer <= 0:
                player.has_shield = False

        # Slow
        if hasattr(player, "slow_timer") and player.slow_timer > 0:
            player.slow_timer -= delta_time
            if player.slow_timer <= 0:
                player.speed_multiplier = 1.0
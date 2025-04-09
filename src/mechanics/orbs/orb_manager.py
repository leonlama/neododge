import random
from src.mechanics.orbs.orb import Orb

class OrbManager:
    """Manages orb creation and effects."""

    def __init__(self):
        pass

    def create_orb(self, orb_type, x, y):
        """Create an orb of the specified type."""
        return Orb(x, y, orb_type)

    def create_random_orb(self, x, y, favor_buffs=True):
        """Create a random orb, with optional bias toward buffs."""
        buff_types = Orb.get_orb_types_by_category("buff")
        debuff_types = Orb.get_orb_types_by_category("debuff")

        if favor_buffs and random.random() < 0.7:
            orb_type = random.choice(buff_types)
        else:
            orb_type = random.choice(buff_types + debuff_types)

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

        # Invincibility
        if hasattr(player, "invincibility_timer") and player.invincibility_timer > 0:
            player.invincibility_timer -= delta_time
            if player.invincibility_timer <= 0:
                player.is_invincible = False

        # Slow
        if hasattr(player, "slow_timer") and player.slow_timer > 0:
            player.slow_timer -= delta_time
            if player.slow_timer <= 0:
                player.speed_multiplier = 1.0
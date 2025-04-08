import random
import arcade
from src.core.constants import SCREEN_WIDTH, SCREEN_HEIGHT

class OrbSpawner:
    """Handles spawning orbs with appropriate types and frequencies"""

    def __init__(self, game_view):
        self.game_view = game_view
        self.orb_timer = 0

        # Define orb types
        self.buff_orbs = [
            "speed_10",
            "speed_20",
            "speed_35",
            "mult_1_5",
            "mult_2",
            "cooldown",
            "shield",
        ]

        self.debuff_orbs = [
            "slow",
            "mult_down_0_5",
            "mult_down_0_25",
            "cooldown_up",
            "vision",
            "hitbox"
        ]

    def update(self, delta_time):
        """Update the orb spawner and spawn orbs as needed"""
        # Don't spawn during wave transitions
        if self.game_view.wave_manager.wave_transition_active:
            return

        # Update orb timer
        self.orb_timer += delta_time

        # Get orb interval from wave manager
        orb_interval = self.game_view.wave_manager.get_orb_interval()

        # Apply special event modifiers
        if self.game_view.wave_manager.special_event == "Orb Storm":
            orb_interval *= 0.3  # Spawn 3x as fast

        # Check if it's time to spawn an orb
        if self.orb_timer >= orb_interval:
            self.orb_timer = 0
            self._spawn_orb()

    def _spawn_orb(self):
        """Spawn a single orb with appropriate type based on current wave"""
        # TODO: Implement actual orb class
        # For now, just print what would be spawned

        # Get current buff/debuff ratio
        buff_ratio, debuff_ratio = self.game_view.wave_manager.get_orb_ratio()

        # Override ratio for No Buffs event
        if self.game_view.wave_manager.special_event == "No Buffs":
            buff_ratio, debuff_ratio = 0.0, 1.0

        # Determine if this is a buff or debuff
        is_buff = random.random() < buff_ratio / (buff_ratio + debuff_ratio)

        # Generate random position (not too close to edges)
        margin = 50
        x = random.randint(margin, SCREEN_WIDTH - margin)
        y = random.randint(margin, SCREEN_HEIGHT - margin)

        # For now, just print what would be spawned
        if is_buff:
            orb_type = random.choice(self.buff_orbs)
            print(f"Would spawn buff orb: {orb_type} at ({x}, {y})")
        else:
            orb_type = random.choice(self.debuff_orbs)
            print(f"Would spawn debuff orb: {orb_type} at ({x}, {y})")

        # TODO: Create and return actual orb object
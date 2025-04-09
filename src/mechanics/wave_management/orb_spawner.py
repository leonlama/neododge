import random
import arcade
from src.core.constants import SCREEN_WIDTH, SCREEN_HEIGHT
from src.mechanics.orbs.buff_orb import BuffOrb
from src.mechanics.orbs.debuff_orb import DebuffOrb

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
        # Get current buff/debuff ratio
        buff_ratio, debuff_ratio = self.game_view.wave_manager.get_orb_ratio()
        
        # Override ratio for No Buffs event
        if self.game_view.wave_manager.special_event == "No Buffs":
            buff_ratio, debuff_ratio = 0.0, 1.0
        
        # Adaptive logic: struggling players get more buffs
        if hasattr(self.game_view.player, 'health') and self.game_view.player.health <= 1:
            buff_ratio += 0.3
        
        # Normalize ratios
        total = buff_ratio + debuff_ratio
        is_buff = random.random() < buff_ratio / total

        # Confusing orb swap
        orb_type = None
        if is_buff:
            orb_type = random.choices(["speed", "mult_1_5", "cooldown", "shield"], weights=[30, 20, 25, 25])[0]
        else:
            orb_type = random.choices(["slow", "mult_down_0_5", "cooldown_up", "vision"], weights=[30, 20, 25, 25])[0]

        # 5% chance to swap visual between slow/speed for confusion
        if orb_type in ["slow", "speed"] and random.random() < 0.05:
            orb_type = "speed" if orb_type == "slow" else "slow"

        # Generate random position (not too close to edges)
        margin = 60
        x = random.randint(margin, SCREEN_WIDTH - margin)
        y = random.randint(margin, SCREEN_HEIGHT - margin)
        
        # Create and add orb to game
        orb = BuffOrb(x, y, orb_type) if is_buff else DebuffOrb(x, y, orb_type)
        self.game_view.orbs.append(orb)
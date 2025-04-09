import random
import arcade
from src.core.constants import SCREEN_WIDTH, SCREEN_HEIGHT
from src.mechanics.orbs.buff_orb import BuffOrb
from src.mechanics.orbs.debuff_orb import DebuffOrb

class OrbSpawner:
    """Spawns orbs during waves using adaptive AI-based configuration"""

    def __init__(self, game_view):
        self.game_view = game_view
        self.orb_timer = 0
        self.orbs_to_spawn = 0
        self.spawned_count = 0
        self.interval = 6.0  # Default fallback

    def setup_wave(self, orb_count, orb_types, override_event=None):
        """Set up spawner for a new wave"""
        self.orbs_to_spawn = orb_count
        self.spawned_count = 0
        self.orb_timer = 0
        self.interval = self.game_view.wave_manager.get_orb_interval()

        # Special event overrides
        if override_event == "Orb Storm":
            self.interval *= 0.3

        self.current_orb_weights = orb_types

    def update(self, delta_time):
        """Update the orb spawner and spawn orbs as needed"""
        if self.game_view.wave_manager.wave_transition_active:
            return

        if self.spawned_count >= self.orbs_to_spawn:
            return

        self.orb_timer += delta_time
        if self.orb_timer >= self.interval:
            self.orb_timer = 0
            self.spawned_count += 1
            self._spawn_orb()

    def _spawn_orb(self):
        """Spawn a single orb using weights defined by wave_config"""
        orb_type = self._choose_orb_type()
        is_buff = orb_type in ["speed", "mult_1_5", "cooldown", "shield"]

        # Generate random screen position with margin
        margin = 60
        x = random.randint(margin, SCREEN_WIDTH - margin)
        y = random.randint(margin, SCREEN_HEIGHT - margin)

        orb = BuffOrb(x, y, orb_type) if is_buff else DebuffOrb(x, y, orb_type)
        self.game_view.orbs.append(orb)
        self.game_view.scene.add_sprite("orbs", orb)

    def _choose_orb_type(self):
        """Choose orb type based on current wave's configuration"""
        # Example structure:
        # self.current_orb_weights = {"speed": 0.3, "mult_1_5": 0.2, "cooldown": 0.2, "shield": 0.3}
        keys = list(self.current_orb_weights.keys())
        weights = list(self.current_orb_weights.values())
        return random.choices(keys, weights=weights, k=1)[0]

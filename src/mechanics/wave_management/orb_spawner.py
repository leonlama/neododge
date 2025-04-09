import random
import arcade
from src.core.constants import SCREEN_WIDTH, SCREEN_HEIGHT
from src.mechanics.orbs.buff_orbs import BuffOrb
from src.mechanics.orbs.debuff_orbs import DebuffOrb
from src.mechanics.orbs.orb_pool import get_random_orb

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
        
        # Generate random screen position with margin
        margin = 60
        x = random.randint(margin, SCREEN_WIDTH - margin)
        y = random.randint(margin, SCREEN_HEIGHT - margin)
        
        orbs = spawn_orbs(self.game_view, count=1, orb_type=orb_type, positions=[(x, y)])
        return orbs[0] if orbs else None

    def _choose_orb_type(self):
        """Choose orb type based on current wave's configuration"""
        # Example structure:
        # self.current_orb_weights = {"speed": 0.3, "mult_1_5": 0.2, "cooldown": 0.2, "shield": 0.3}
        keys = list(self.current_orb_weights.keys())
        weights = list(self.current_orb_weights.values())
        return random.choices(keys, weights=weights, k=1)[0]

def spawn_orbs(game_view, count=1, orb_type=None, positions=None):
    """Spawn orbs into the game."""
    from src.mechanics.orbs.orb_pool import get_random_orb

    orbs_spawned = []
    for i in range(count):
        if positions and i < len(positions):
            x, y = positions[i]
        else:
            x, y = random.randint(100, 700), random.randint(100, 500)

        orb = get_random_orb(x, y, orb_type)
        game_view.orbs.append(orb)
        game_view.scene.add_sprite("orbs", orb)
        orbs_spawned.append(orb)

    print(f"🔵 Spawned {len(orbs_spawned)} orbs")
    return orbs_spawned

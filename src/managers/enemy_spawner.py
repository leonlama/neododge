import random
import arcade
from src.core.constants import SCREEN_WIDTH, SCREEN_HEIGHT

class EnemySpawner:
    """Handles spawning enemies with appropriate types and frequencies"""

    def __init__(self, game_view):
        self.game_view = game_view
        self.spawn_timer = 0
        self.spawn_count = 0
        self.max_enemies = 0

    def update(self, delta_time):
        """Update the enemy spawner and spawn enemies as needed"""
        # Don't spawn during wave transitions
        if self.game_view.wave_manager.wave_transition_active:
            return

        # Update spawn timer
        self.spawn_timer += delta_time

        # Get spawn interval from wave manager
        spawn_interval = self.game_view.wave_manager.get_spawn_interval()

        # Apply special event modifiers
        if self.game_view.wave_manager.special_event == "Double Enemies":
            spawn_interval *= 0.5  # Spawn twice as fast

        # Check if it's time to spawn an enemy
        if self.spawn_timer >= spawn_interval:
            self.spawn_timer = 0

            # Get max enemies for this wave
            if self.spawn_count == 0:
                self.max_enemies = self.game_view.wave_manager.get_enemy_count()

                # Apply special event modifiers
                if self.game_view.wave_manager.special_event == "Double Enemies":
                    self.max_enemies *= 2

            # Check if we've spawned enough enemies for this wave
            if self.spawn_count < self.max_enemies:
                self._spawn_enemy()
                self.spawn_count += 1

    def _spawn_enemy(self):
        """Spawn a single enemy with appropriate type based on current wave"""
        # TODO: Implement actual enemy spawning
        print(f"Would spawn enemy (wave {self.game_view.wave_manager.wave})")
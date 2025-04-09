import random
import arcade
from src.core.constants import SCREEN_WIDTH, SCREEN_HEIGHT
from src.entities.enemies import Chaser, Wanderer, Shooter, Bomber, Flight

class EnemySpawner:
    """Handles spawning enemies with appropriate types and frequencies"""

    def __init__(self, game_view):
        self.game_view = game_view
        self.spawn_timer = 0
        self.spawn_count = 0
        self.max_enemies = 0
        self.enemy_types = []
        self.enemy_positions = []

    def setup_wave(self, enemy_types, positions):
        """Prepare for a new wave of enemies"""
        self.spawn_timer = 0
        self.spawn_count = 0
        self.enemy_types = enemy_types
        self.enemy_positions = positions
        self.max_enemies = len(enemy_types)

    def update(self, delta_time):
        """Update the enemy spawner and spawn enemies as needed"""
        if self.game_view.wave_manager.wave_transition_active:
            return

        self.spawn_timer += delta_time
        spawn_interval = self.game_view.wave_manager.get_spawn_interval()

        if self.game_view.wave_manager.special_event == "Double Enemies":
            spawn_interval *= 0.5

        if self.spawn_timer >= spawn_interval:
            self.spawn_timer = 0

            if self.spawn_count < self.max_enemies:
                self._spawn_enemy(self.enemy_types[self.spawn_count],
                                  self.enemy_positions[self.spawn_count])
                self.spawn_count += 1

    def _spawn_enemy(self, enemy_type, position):
        """Spawn a single enemy based on type and position"""
        x, y = position
        enemy = None

        if enemy_type == "chaser":
            enemy = Chaser(x, y)
        elif enemy_type == "wander":
            enemy = Wanderer(x, y)
        elif enemy_type == "shooter":
            enemy = Shooter(x, y)
        elif enemy_type == "bomber":
            enemy = Bomber(x, y)
        elif enemy_type == "flight":
            direction = random.choice(["horizontal", "vertical"])
            speed = random.randint(250, 400)
            enemy = Flight(x, y, direction=direction, speed=speed)
        else:
            print(f"⚠️ Unknown enemy type: {enemy_type}")
            return

        enemy.game_view = self.game_

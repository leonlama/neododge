import random
import arcade
from scripts.enemies.chaser_enemy import ChaserEnemy
from scripts.enemies.shooter_enemy import ShooterEnemy
from scripts.utils.constants import SCREEN_WIDTH, SCREEN_HEIGHT

class EnemyManager:
    """Manages enemy spawning and behavior."""

    def __init__(self, game_view):
        self.game_view = game_view
        self.enemy_types = {
            "chaser": ChaserEnemy,
            "shooter": ShooterEnemy
        }

    def spawn_enemies(self, enemy_list, wave_number, screen_width, screen_height):
        """Spawn enemies for a wave."""
        # Clear existing enemies
        enemy_list.clear()

        # Calculate number of enemies based on wave
        num_enemies = 3 + wave_number

        # Cap at reasonable number
        num_enemies = min(num_enemies, 20)

        # Determine enemy type distribution
        enemy_distribution = self._get_enemy_distribution(wave_number)

        # Spawn enemies
        for _ in range(num_enemies):
            # Choose enemy type
            enemy_type = random.choices(
                list(enemy_distribution.keys()),
                weights=list(enemy_distribution.values()),
                k=1
            )[0]

            # Determine spawn position (off-screen)
            side = random.randint(0, 3)  # 0: top, 1: right, 2: bottom, 3: left

            if side == 0:  # Top
                x = random.randint(0, screen_width)
                y = screen_height + 50
            elif side == 1:  # Right
                x = screen_width + 50
                y = random.randint(0, screen_height)
            elif side == 2:  # Bottom
                x = random.randint(0, screen_width)
                y = -50
            else:  # Left
                x = -50
                y = random.randint(0, screen_height)

            # Create enemy
            enemy_class = self.enemy_types[enemy_type]
            enemy = enemy_class(x, y)

            # Set reference to game view
            enemy.game_view = self.game_view

            # Add to list
            enemy_list.append(enemy)

        return len(enemy_list)

    def _get_enemy_distribution(self, wave_number):
        """Get the distribution of enemy types based on wave number."""
        if wave_number <= 3:
            return {
                "chaser": 0.8,
                "shooter": 0.2
            }
        elif wave_number <= 6:
            return {
                "chaser": 0.6,
                "shooter": 0.4
            }
        else:
            return {
                "chaser": 0.5,
                "shooter": 0.5
            }
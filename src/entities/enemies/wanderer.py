from src.entities.enemies.enemy import Enemy
import random

class WandererEnemy(Enemy):
    """Enemy that moves in straight lines and bounces off walls."""

    def __init__(self, x, y, target=None):
        super().__init__(x, y, target, "wanderer")

        # Set wanderer-specific properties
        self.speed = random.uniform(120, 180)  # Faster than other types
        self.health = 1
        self.max_health = 1
        self.damage = 1
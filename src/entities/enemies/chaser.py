from src.entities.enemies.enemy import Enemy
import random

class ChaserEnemy(Enemy):
    """Enemy that chases the player."""

    def __init__(self, x, y, target=None):
        super().__init__(x, y, target, "chaser")

        # Set chaser-specific properties
        self.speed = random.uniform(100, 140)  # Medium speed
        self.health = 2
        self.max_health = 2
        self.damage = 1
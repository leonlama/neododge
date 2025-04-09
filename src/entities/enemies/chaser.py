from src.entities.enemies.enemy import Enemy
import random
import math
import arcade
from src.core.scaling import get_scale

class Chaser(Enemy):
    """Enemy that chases the player."""

    def __init__(self, x, y, target=None):
        super().__init__(x, y, target, "chaser")

        # Set chaser-specific properties
        self.speed = random.uniform(70, 100)  # Reduced speed (was 100-140)
        self.health = 2
        self.max_health = 2
        self.damage = 1
        
        # Add acceleration for smoother movement
        self.max_speed = self.speed
        self.acceleration = 200  # Units per second²
        self.current_speed = 0
        self.change_x = 0
        self.change_y = 0
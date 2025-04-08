import arcade
import math
import random
from src.core.constants import SCREEN_WIDTH, SCREEN_HEIGHT

class Enemy(arcade.Sprite):
    """Base class for all enemies in the game"""

    def __init__(self, x=None, y=None):
        super().__init__()

        # Set position (random if not specified)
        self.center_x = x if x is not None else random.randint(50, SCREEN_WIDTH - 50)
        self.center_y = y if y is not None else random.randint(50, SCREEN_HEIGHT - 50)

        # Set properties
        self.speed = random.uniform(50, 100)
        self.health = 1
        self.damage = 1
        self.score_value = 10
        self.scale = 0.5

        # Set default texture
        self.texture = arcade.make_soft_square_texture(
            32, 
            arcade.color.RED, 
            outer_alpha=255
        )

    def update(self, delta_time=1/60):
        """Update the enemy's position and behavior"""
        # Basic movement - to be overridden by subclasses
        pass

    def take_damage(self, amount=1):
        """Take damage and check if enemy is defeated"""
        self.health -= amount

        # Flash effect
        self.alpha = 128

        # Check if enemy is defeated
        if self.health <= 0:
            self.on_death()
            return True

        return False

    def on_death(self):
        """Handle enemy death"""
        # Remove from sprite list
        self.remove_from_sprite_lists()

        # Spawn particles or other effects
        self.spawn_death_particles()

    def spawn_death_particles(self):
        """Spawn particles when enemy dies"""
        # This would be implemented in the game view
        pass

    def move_towards_player(self, player, delta_time):
        """Move towards the player"""
        if player:
            # Calculate direction vector
            dx = player.center_x - self.center_x
            dy = player.center_y - self.center_y
            distance = math.sqrt(dx*dx + dy*dy)

            if distance > 0:
                # Normalize direction vector
                dx = dx / distance
                dy = dy / distance

                # Move towards player
                self.center_x += dx * self.speed * delta_time
                self.center_y += dy * self.speed * delta_time
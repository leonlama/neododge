import arcade
import math
import random
from src.entities.enemies.enemy import Enemy

class ChaserEnemy(Enemy):
    """Enemy that chases the player"""

    def __init__(self, x=None, y=None):
        super().__init__(x, y)

        # Set properties specific to chaser enemies
        self.speed = random.uniform(70, 120)
        self.health = 2
        self.damage = 1
        self.score_value = 15

        # Set texture
        self.texture = arcade.make_soft_circle_texture(
            32, 
            arcade.color.RED, 
            outer_alpha=255
        )

        # Movement properties
        self.acceleration = random.uniform(50, 100)
        self.max_speed = random.uniform(100, 200)
        self.velocity_x = 0
        self.velocity_y = 0
        self.friction = 0.9  # Slow down when not accelerating

    def update(self, delta_time=1/60):
        """Update the chaser enemy's position and behavior"""
        # Movement is handled by move_towards_player

        # Apply friction to velocity
        self.velocity_x *= self.friction
        self.velocity_y *= self.friction

        # Update position based on velocity
        self.center_x += self.velocity_x * delta_time
        self.center_y += self.velocity_y * delta_time

        # Keep enemy on screen
        self.center_x = max(self.width/2, min(self.center_x, arcade.get_window().width - self.width/2))
        self.center_y = max(self.height/2, min(self.center_y, arcade.get_window().height - self.height/2))

        # Reset alpha (for damage flash effect)
        self.alpha = 255

    def move_towards_player(self, player, delta_time):
        """Move towards the player with acceleration"""
        if player:
            # Calculate direction vector
            dx = player.center_x - self.center_x
            dy = player.center_y - self.center_y
            distance = math.sqrt(dx*dx + dy*dy)

            if distance > 0:
                # Normalize direction vector
                dx = dx / distance
                dy = dy / distance

                # Apply acceleration in the direction of the player
                self.velocity_x += dx * self.acceleration * delta_time
                self.velocity_y += dy * self.acceleration * delta_time

                # Limit speed
                speed = math.sqrt(self.velocity_x**2 + self.velocity_y**2)
                if speed > self.max_speed:
                    self.velocity_x = (self.velocity_x / speed) * self.max_speed
                    self.velocity_y = (self.velocity_y / speed) * self.max_speed
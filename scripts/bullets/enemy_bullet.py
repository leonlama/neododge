import arcade
from src.core.constants import SCREEN_WIDTH, SCREEN_HEIGHT
from src.core.resource_manager import resource_path

class EnemyBullet(arcade.Sprite):
    """Bullet fired by enemies."""

    def __init__(self, x, y, scale=0.5):
        super().__init__(scale=scale)

        # Set texture
        self.texture = arcade.make_soft_circle_texture(10, arcade.color.YELLOW, outer_alpha=255)

        # Position
        self.center_x = x
        self.center_y = y

        # Properties
        self.speed = 5.0
        self.damage = 1.0
        self.age = 0
        self.max_age = 5.0  # Seconds before bullet disappears

    def update(self, delta_time=1/60):
        """Update bullet position and age."""
        # Update position
        self.center_x += self.change_x
        self.center_y += self.change_y

        # Update age
        self.age += delta_time

        # Check if bullet should be removed
        if self.age > self.max_age:
            self.kill()

        # Check if bullet is off-screen
        if (self.center_x < -50 or self.center_x > SCREEN_WIDTH + 50 or
            self.center_y < -50 or self.center_y > SCREEN_HEIGHT + 50):
            self.kill()

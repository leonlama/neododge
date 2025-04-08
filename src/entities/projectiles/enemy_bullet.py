import arcade
from src.skins.skin_manager import skin_manager

class EnemyBullet(arcade.Sprite):
    """Bullet fired by shooter enemies."""

    def __init__(self, x, y, dx, dy):
        """Initialize the bullet.

        Args:
            x: Starting x position
            y: Starting y position
            dx: X velocity
            dy: Y velocity
        """
        super().__init__()

        # Set position
        self.center_x = x
        self.center_y = y

        # Set velocity
        self.change_x = dx
        self.change_y = dy

        # Set texture
        try:
            self.texture = skin_manager.get_texture("projectiles", "enemy_bullet")
            if not self.texture:
                # Create a fallback texture
                self.texture = arcade.make_circle_texture(8, arcade.color.RED)
        except:
            # Fallback if texture loading fails
            self.texture = arcade.make_circle_texture(8, arcade.color.RED)

        # Set scale
        try:
            self.scale = skin_manager.scales.get("bullet", 1.0)
        except:
            self.scale = 1.0

        # Set properties
        self.damage = 1

    def update(self):
        """Update bullet position."""
        self.center_x += self.change_x * (1/60)  # Assuming 60 FPS
        self.center_y += self.change_y * (1/60)

    def update_with_time(self, delta_time):
        """Update bullet position with delta time."""
        self.center_x += self.change_x * delta_time
        self.center_y += self.change_y * delta_time
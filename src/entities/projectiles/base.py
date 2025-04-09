import arcade
from src.core.scaling import get_scale

class Projectile(arcade.Sprite):
    """Base class for all projectiles in the game."""

    def __init__(self, x, y, dx, dy, damage=1, projectile_type="default"):
        super().__init__()

        # Position
        self.center_x = x
        self.center_y = y

        # Velocity
        self.change_x = dx
        self.change_y = dy

        # Properties
        self.damage = damage
        self.projectile_type = projectile_type

        # Load texture
        self._load_texture()

        # Set scale
        self.scale = get_scale('projectile')

    def _load_texture(self):
        """Load the projectile texture"""
        # Override in subclasses
        pass

    def update_with_time(self, delta_time):
        """Update projectile position with delta time."""
        self.center_x += self.change_x * delta_time
        self.center_y += self.change_y * delta_time

    def update(self):
        """Update projectile position assuming 60 FPS."""
        self.update_with_time(1/60)
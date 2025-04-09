import arcade
from src.entities.projectiles.base import Projectile
from src.skins.skin_manager import skin_manager
from src.core.scaling import get_scale

class EnemyBullet(Projectile):
    """Bullet fired by shooter enemies."""

    def __init__(self, x, y, dx, dy):
        """Initialize the bullet.

        Args:
            x: Starting x position
            y: Starting y position
            dx: X velocity
            dy: Y velocity
        """
        super().__init__(x, y, dx, dy, damage=1, projectile_type="enemy_bullet")

        # Override scale for bullets specifically
        self.scale = get_scale('bullet')

    def _load_texture(self):
        """Load the enemy bullet texture"""
        try:
            self.texture = skin_manager.get_texture("projectiles", "enemy_bullet")
            if not self.texture:
                # Create a fallback texture
                self.texture = arcade.make_circle_texture(8, arcade.color.RED)
        except:
            # Fallback if texture loading fails
            self.texture = arcade.make_circle_texture(8, arcade.color.RED)
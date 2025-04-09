import arcade
import math
from src.skins.skin_manager import skin_manager

class EnemyBullet(arcade.Sprite):
    """Bullet projectile class."""

    def __init__(self, x, y, direction_x, direction_y, speed=5.0, damage=1, is_player_bullet=True):
        super().__init__()

        self.center_x = x
        self.center_y = y
        self.speed = speed
        self.damage = damage
        self.is_player_bullet = is_player_bullet

        # Set velocity based on direction and speed
        self.change_x = direction_x * speed
        self.change_y = direction_y * speed

        # Set appearance
        try:
            if is_player_bullet:
                self.texture = skin_manager.get_texture("projectiles", "player_bullet")
            else:
                self.texture = skin_manager.get_texture("projectiles", "enemy_bullet")
        except Exception as e:
            print(f"Error setting bullet texture: {e}")

            # Fallback texture
            if is_player_bullet:
                self.texture = arcade.make_circle_texture(10, arcade.color.BLUE)
            else:
                self.texture = arcade.make_circle_texture(10, arcade.color.RED)

        # Set scale
        self.scale = 0.035  # Same as player scale

        # Set rotation to match direction
        self.angle = math.degrees(math.atan2(direction_y, direction_x))

    def update(self):
        """Update the bullet."""
        # Move the bullet
        self.center_x += self.change_x
        self.center_y += self.change_y

        # Check if bullet is off-screen
        window = arcade.get_window()
        if (self.center_x < 0 or self.center_x > window.width or
            self.center_y < 0 or self.center_y > window.height):
            self.remove_from_sprite_lists()
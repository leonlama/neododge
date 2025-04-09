import arcade
import math
import random
from src.entities.enemies.enemy import Enemy
from src.entities.projectiles.enemy_bullet import EnemyBullet
from src.audio.sound_manager import sound_manager
from src.core.scaling import get_scale

class ShooterEnemy(Enemy):
    """Enemy that moves slowly and shoots at the player."""

    def __init__(self, x, y, target=None):
        """Initialize the shooter enemy.

        Args:
            x: Initial x position
            y: Initial y position
            target: The target to shoot at (usually the player)
        """
        super().__init__(x, y, target, "shooter")

        # Set shooter-specific properties
        self.speed = random.uniform(60, 100)  # Slower than other types
        self.health = 3
        self.max_health = 3
        self.damage = 1

        # Shooting properties
        self.bullets = arcade.SpriteList()
        self.shoot_timer = 0
        self.fire_rate = random.uniform(1.5, 3.0)  # Time between shots
        self.bullet_speed = random.uniform(200, 300)

        # Movement pattern (moves in small patterns, not directly chasing)
        self.movement_timer = 0
        self.movement_duration = random.uniform(1.0, 2.0)
        self.set_random_direction()

    def update(self, delta_time=1/60):
        """Update shooter enemy behavior."""
        # Update movement
        self.movement_timer += delta_time
        if self.movement_timer >= self.movement_duration:
            self.movement_timer = 0
            self.movement_duration = random.uniform(1.0, 2.0)
            self.set_random_direction()

        # Move in current direction
        self.center_x += self.change_x * delta_time
        self.center_y += self.change_y * delta_time

        # Bounce off screen edges
        window = arcade.get_window()
        if self.left < 0:
            self.left = 0
            self.change_x *= -1
        elif self.right > window.width:
            self.right = window.width
            self.change_x *= -1

        if self.bottom < 0:
            self.bottom = 0
            self.change_y *= -1
        elif self.top > window.height:
            self.top = window.height
            self.change_y *= -1

        # Update shooting
        if self.target:
            self.shoot_timer += delta_time
            if self.shoot_timer >= self.fire_rate:
                self.shoot_timer = 0
                self.shoot_at_target()

        # Update bullets
        self.bullets.update()

        # Remove bullets that go off-screen
        for bullet in self.bullets:
            if (bullet.center_x < 0 or bullet.center_x > window.width or
                bullet.center_y < 0 or bullet.center_y > window.height):
                bullet.remove_from_sprite_lists()

    def set_random_direction(self):
        """Set a random movement direction."""
        angle = random.uniform(0, 2 * math.pi)
        self.change_x = self.speed * math.cos(angle)
        self.change_y = self.speed * math.sin(angle)

    def shoot_at_target(self):
        """Shoot a bullet at the target."""
        if not self.target:
            return

        # Calculate direction to target
        dx = self.target.center_x - self.center_x
        dy = self.target.center_y - self.center_y
        distance = max(1, math.hypot(dx, dy))

        # Create bullet
        bullet = EnemyBullet(
            self.center_x,
            self.center_y,
            dx / distance * self.bullet_speed,
            dy / distance * self.bullet_speed
        )

        # Add to bullet list
        self.bullets.append(bullet)

        # Play sound
        try:
            sound_manager.play_sound("enemy", "shoot")
        except Exception as e:
            print(f"Error playing enemy shoot sound: {e}")
import arcade
import math
import random
from scripts.enemies.base_enemy import BaseEnemy
from scripts.bullets.enemy_bullet import EnemyBullet
from src.core.resource_manager import resource_path
from src.core.constants import SCREEN_WIDTH, SCREEN_HEIGHT

class ShooterEnemy(BaseEnemy):
    """An enemy that shoots at the player."""

    def __init__(self, x, y, scale=1.0):
        super().__init__(x, y, scale)

        # Set texture
        try:
            self.texture = arcade.load_texture(resource_path("assets/images/enemies/shooter.png"))
        except:
            # Fallback texture
            self.texture = arcade.make_soft_square_texture(30, arcade.color.RED, outer_alpha=255)

        # Movement
        self.speed = 1.5
        self.behavior_type = "avoid"

        # Combat
        self.health = 1
        self.damage = 0.5
        self.can_shoot = True
        self.shoot_cooldown = 1.5
        self.bullet_speed = 5.0

    def _avoid_behavior(self):
        """Move away from the player if too close."""
        # Get player from the game view
        if not self.game_view or not self.game_view.player:
            return

        player = self.game_view.player

        # Calculate direction to player
        dx = player.center_x - self.center_x
        dy = player.center_y - self.center_y
        distance = math.sqrt(dx*dx + dy*dy)

        # If player is too close, move away
        if distance < 200:
            if distance > 0:
                self.change_x = -dx / distance * self.speed
                self.change_y = -dy / distance * self.speed
        # Otherwise, move randomly
        elif random.random() < 0.02:
            self.change_x = random.uniform(-1, 1) * self.speed
            self.change_y = random.uniform(-1, 1) * self.speed

        # Update position
        self.center_x += self.change_x
        self.center_y += self.change_y

        # Keep in bounds
        self.center_x = max(50, min(self.center_x, SCREEN_WIDTH - 50))
        self.center_y = max(50, min(self.center_y, SCREEN_HEIGHT - 50))

    def _shoot(self):
        """Shoot a bullet at the player."""
        # Get player from the game view
        if not self.game_view or not self.game_view.player:
            return

        player = self.game_view.player

        # Calculate direction to player
        dx = player.center_x - self.center_x
        dy = player.center_y - self.center_y
        distance = math.sqrt(dx*dx + dy*dy)

        if distance > 0:
            # Create bullet
            bullet = EnemyBullet(self.center_x, self.center_y)

            # Set bullet direction
            bullet.change_x = dx / distance * self.bullet_speed
            bullet.change_y = dy / distance * self.bullet_speed

            # Add bullet to list
            self.bullets.append(bullet)

            # Play sound
            try:
                bullet_sound = arcade.load_sound(resource_path("assets/audio/enemy_shoot.wav"))
                arcade.play_sound(bullet_sound, volume=0.1)
            except:
                pass

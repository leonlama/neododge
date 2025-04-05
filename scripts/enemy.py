import arcade
import math
import random
from scripts.bullet import Bullet

ENEMY_SPEED = 100
WANDER_SPEED = 80

class Enemy(arcade.Sprite):
    def __init__(self, start_x, start_y, target_sprite, behavior="chaser"):
        super().__init__()
        self.texture = arcade.make_soft_square_texture(32, arcade.color.RED, outer_alpha=255)
        self.center_x = start_x
        self.center_y = start_y
        self.target_sprite = target_sprite
        self.behavior = behavior
        self.bullets = arcade.SpriteList()

        # Wanderer direction
        self.direction = random.choice([(1, 0), (-1, 0), (0, 1), (0, -1)])

        # Shooter cooldown
        self.bullet_timer = 0

    def update(self, delta_time: float = 1 / 60):
        if self.behavior == "chaser":
            self._follow_player(delta_time)
        elif self.behavior == "wander":
            self._wander(delta_time)
        elif self.behavior == "shooter":
            self._shoot(delta_time)

        self.bullets.update()

    def _follow_player(self, dt):
        dx = self.target_sprite.center_x - self.center_x
        dy = self.target_sprite.center_y - self.center_y
        distance = math.hypot(dx, dy)

        if distance > 1:
            self.center_x += (dx / distance) * ENEMY_SPEED * dt
            self.center_y += (dy / distance) * ENEMY_SPEED * dt

    def _wander(self, dt):
        dx, dy = self.direction
        self.center_x += dx * WANDER_SPEED * dt
        self.center_y += dy * WANDER_SPEED * dt

        # Bounce off screen edges
        if self.left < 0 or self.right > 800:
            self.direction = (-self.direction[0], self.direction[1])
        if self.bottom < 0 or self.top > 600:
            self.direction = (self.direction[0], -self.direction[1])

    def _shoot(self, dt):
        self.bullet_timer += dt
        if self.bullet_timer >= 1.5:
            self.bullet_timer = 0
            bullet = Bullet(
                self.center_x,
                self.center_y,
                self.target_sprite.center_x,
                self.target_sprite.center_y,
                source=self
            )
            self.bullets.append(bullet)

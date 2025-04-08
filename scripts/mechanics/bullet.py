import arcade
import math

BULLET_SPEED = 250

class Bullet(arcade.Sprite):
    def __init__(self, start_x, start_y, target_x, target_y, source=None):
        super().__init__()
        self.texture = arcade.make_soft_circle_texture(10, arcade.color.YELLOW, outer_alpha=255)
        self.center_x = start_x
        self.center_y = start_y
        self.age = 0
        self.source = source

        dx = target_x - start_x
        dy = target_y - start_y
        dist = math.hypot(dx, dy)

        self.velocity = (dx / dist * BULLET_SPEED, dy / dist * BULLET_SPEED)

    def update(self, delta_time: float = 1 / 60):
        self.age += delta_time
        self.center_x += self.velocity[0] * delta_time
        self.center_y += self.velocity[1] * delta_time


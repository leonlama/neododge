import arcade
import math

ENEMY_SPEED = 100

class Enemy(arcade.Sprite):
    def __init__(self, start_x, start_y, target_sprite):
        super().__init__()
        self.texture = arcade.make_soft_square_texture(32, arcade.color.RED, outer_alpha=255)
        self.center_x = start_x
        self.center_y = start_y
        self.target_sprite = target_sprite

    def update(self, delta_time: float = 1 / 60):
        dx = self.target_sprite.center_x - self.center_x
        dy = self.target_sprite.center_y - self.center_y
        distance = math.hypot(dx, dy)

        if distance > 1:
            direction_x = dx / distance
            direction_y = dy / distance
            self.center_x += direction_x * ENEMY_SPEED * delta_time
            self.center_y += direction_y * ENEMY_SPEED * delta_time

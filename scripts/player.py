import arcade
import math

PLAYER_SPEED = 300

class Player(arcade.Sprite):
    def __init__(self, start_x, start_y):
        super().__init__()
        self.texture = arcade.make_soft_square_texture(32, arcade.color.CYAN, outer_alpha=255)
        self.center_x = start_x
        self.center_y = start_y
        self.target_x = start_x
        self.target_y = start_y

    def set_target(self, x, y):
        self.target_x = x
        self.target_y = y

    def update(self, delta_time: float = 1 / 60):
        dx = self.target_x - self.center_x
        dy = self.target_y - self.center_y
        distance = math.hypot(dx, dy)

        if distance > 2:
            direction_x = dx / distance
            direction_y = dy / distance
            self.center_x += direction_x * PLAYER_SPEED * delta_time
            self.center_y += direction_y * PLAYER_SPEED * delta_time

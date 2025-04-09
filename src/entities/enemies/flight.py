import arcade
from .enemy import Enemy

class Flight(Enemy):
    def __init__(self, x, y, direction="horizontal", speed=300, scale=1.0):
        super().__init__("flight", x, y, scale)
        self.direction = direction
        self.speed = speed
        self.texture = arcade.load_texture("assets/skins/default/enemies/shooter.png")  # placeholder

        if direction == "horizontal":
            self.change_x = speed
            self.change_y = 0
        else:
            self.change_x = 0
            self.change_y = speed

    def update(self, delta_time: float = 1/60):
        self.center_x += self.change_x * delta_time
        self.center_y += self.change_y * delta_time

        if (self.center_x < -50 or self.center_x > 850 or
            self.center_y < -50 or self.center_y > 650):
            self.kill()

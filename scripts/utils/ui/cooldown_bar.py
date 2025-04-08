import arcade
from scripts.utils.constants import DASH_COOLDOWN

class CooldownBar:
    def __init__(self, label: str, x: float, y: float, width: float, height: float):
        self.label = label
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.cooldown = DASH_COOLDOWN  # Default full cooldown (in seconds)
        self.timer = 0.0     # Time since last use

    def reset(self):
        self.timer = 0.0

    def update(self, delta_time: float):
        if self.timer < self.cooldown:
            self.timer += delta_time

    def set_cooldown(self, cooldown: float):
        self.cooldown = cooldown

    def draw(self):
        # Background (gray)
        arcade.draw_rectangle_filled(
            self.x + self.width / 2, self.y + self.height / 2,
            self.width, self.height,
            arcade.color.GRAY
        )

        # Fill amount (yellow)
        percent = min(self.timer / self.cooldown, 1.0)
        fill_width = self.width * percent

        arcade.draw_rectangle_filled(
            self.x + fill_width / 2, self.y + self.height / 2,
            fill_width, self.height,
            arcade.color.YELLOW
        )

        # Text label
        arcade.draw_text(
            self.label,
            self.x,
            self.y + self.height + 5,
            arcade.color.LIGHT_GRAY,
            font_size=10
        )

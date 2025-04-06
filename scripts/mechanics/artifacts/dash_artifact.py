import arcade
from .base import BaseArtifact

class DashArtifact(BaseArtifact):
    def __init__(self, x=None, y=None):
        super().__init__(x or 0, y or 0)
        self.texture = arcade.make_circle_texture(30, arcade.color.BLUE)
        self.name = "Dash"
        self.cooldown = 5.0
        self.cooldown_timer = 0.0

    def apply_effect(self, player):
        player.try_dash()

    def update(self, delta_time):
        if self.cooldown_timer > 0:
            self.cooldown_timer -= delta_time

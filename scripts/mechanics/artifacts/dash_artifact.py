import arcade
from .base import BaseArtifact

class DashArtifact(BaseArtifact):
    def __init__(self, x=None, y=None):
        super().__init__(x or 0, y or 0)
        self.texture = arcade.make_circle_texture(30, arcade.color.BLUE)
        self.name = "Dash"

    def apply_effect(self, player):
        player.try_dash()

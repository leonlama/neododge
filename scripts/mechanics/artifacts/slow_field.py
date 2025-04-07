import arcade
from .base import BaseArtifact
from scripts.skins.skin_manager import SkinManager

class SlowFieldArtifact(arcade.Sprite):
    def __init__(self, x, y):
        skin_manager = SkinManager()
        super().__init__(filename=skin_manager.get_path())
        self.center_x = x
        self.center_y = y
        self.name = "Slow Field"
        self.cooldown = 10.0
        self.cooldown_timer = self.cooldown

    def apply_effect(self, player, bullets):
        for bullet in bullets:
            bullet.change_x *= 0.5
            bullet.change_y *= 0.5

    def update(self, delta_time):
        if self.cooldown_timer > 0:
            self.cooldown_timer -= delta_time

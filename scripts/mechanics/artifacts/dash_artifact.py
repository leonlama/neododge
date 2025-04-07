from .base import BaseArtifact
from scripts.skins.skin_manager import skin_manager
from scripts.utils.constants import ARTIFACT_SCALE
from scripts.utils.resource_helper import resource_path

class DashArtifact(BaseArtifact):
    def __init__(self, x, y):
        super().__init__(resource_path(skin_manager.get_texture_path("artifacts", "dash")), scale=ARTIFACT_SCALE)
        self.center_x = x
        self.center_y = y
        self.name = "Dash"
        self.cooldown = 10.0  # seconds
        self.cooldown_timer = self.cooldown  # Start fully ready!

    def update(self, delta_time: float = 0):
        # Update cooldown timer
        self.cooldown_timer += delta_time

    def apply_effect(self, player, *_):
        if self.cooldown_timer >= self.cooldown:
            player.perform_dash()
            self.cooldown_timer = 0
            print("⚡ Dash used!")
        else:
            print("❌ Dash on cooldown.")

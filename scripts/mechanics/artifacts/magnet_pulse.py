from .base import BaseArtifact
from scripts.skins.skin_manager import skin_manager
from scripts.utils.constants import ARTIFACT_SCALE

class MagnetPulseArtifact(BaseArtifact):
    def __init__(self, x, y):
        super().__init__(skin_manager.get_texture_path("artifacts", "magnet_pulse"), scale=ARTIFACT_SCALE)
        self.center_x = x
        self.center_y = y
        self.name = "Magnet Pulse"
        self.cooldown = 10.0
        self.cooldown_timer = self.cooldown

    def apply_effect(self, player, orbs):
        for orb in orbs:
            orb.center_x = player.center_x
            orb.center_y = player.center_y

    def update(self, delta_time):
        if self.cooldown_timer > 0:
            self.cooldown_timer -= delta_time

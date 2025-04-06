from .base import BaseArtifact

class MagnetPulseArtifact(BaseArtifact):
    def __init__(self):
        super().__init__()
        self.name = "Magnet Pulse"
        self.cooldown = 10.0
        self.cooldown_timer = 0.0

    def apply_effect(self, player, orbs):
        for orb in orbs:
            orb.center_x = player.center_x
            orb.center_y = player.center_y

    def update(self, delta_time):
        if self.cooldown_timer > 0:
            self.cooldown_timer -= delta_time

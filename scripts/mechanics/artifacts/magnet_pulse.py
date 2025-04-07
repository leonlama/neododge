from .base import BaseArtifact

class MagnetPulseArtifact(BaseArtifact):
    def __init__(self, x, y):
        super().__init__()
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

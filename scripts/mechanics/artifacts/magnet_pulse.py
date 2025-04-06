from .base import BaseArtifact

class MagnetPulseArtifact(BaseArtifact):
    def __init__(self):
        super().__init__()
        self.name = "Magnet Pulse"

    def apply_effect(self, player, orbs):
        for orb in orbs:
            orb.center_x = player.center_x
            orb.center_y = player.center_y

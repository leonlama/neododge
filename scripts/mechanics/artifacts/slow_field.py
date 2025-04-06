from .base import BaseArtifact

class SlowFieldArtifact(BaseArtifact):
    def __init__(self):
        super().__init__()
        self.name = "Slow Field"

    def apply_effect(self, player, bullets):
        for bullet in bullets:
            bullet.change_x *= 0.5
            bullet.change_y *= 0.5

from .base import BaseArtifact

class CloneDashArtifact(BaseArtifact):
    def __init__(self):
        super().__init__()
        self.name = "Clone Dash"

    def apply_effect(self, player, enemies):
        clone = player.clone()
        enemies.append(clone)

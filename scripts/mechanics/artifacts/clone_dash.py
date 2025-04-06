from .base import BaseArtifact

class CloneDashArtifact(BaseArtifact):
    def __init__(self):
        super().__init__()
        self.name = "Clone Dash"
        self.cooldown = 10.0
        self.cooldown_timer = 0.0

    def apply_effect(self, player, enemies):
        clone = player.clone()
        enemies.append(clone)

    def update(self, delta_time):
        if self.cooldown_timer > 0:
            self.cooldown_timer -= delta_time

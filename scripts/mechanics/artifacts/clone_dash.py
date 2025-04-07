from .base import BaseArtifact

class CloneDashArtifact(BaseArtifact):
    def __init__(self, x, y):
        super().__init__()
        self.center_x = x
        self.center_y = y
        self.name = "Clone Dash"
        self.cooldown = 10.0
        self.cooldown_timer = self.cooldown

    def apply_effect(self, player, enemies):
        clone = player.clone()
        enemies.append(clone)

    def update(self, delta_time):
        if self.cooldown_timer > 0:
            self.cooldown_timer -= delta_time

from .base import BaseArtifact
from scripts.skins.skin_manager import skin_manager
from scripts.utils.constants import ARTIFACT_SCALE

class CloneDashArtifact(BaseArtifact):
    def __init__(self, x, y):
        super().__init__(skin_manager.get_texture_path("artifacts", "clone_dash"), scale=ARTIFACT_SCALE)
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

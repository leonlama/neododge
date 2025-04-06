from .base import BaseArtifact

class DashArtifact(BaseArtifact):
    def __init__(self, x=None, y=None):
        super().__init__()
        self.name = "Dash"
        self.center_x = x if x is not None else 0
        self.center_y = y if y is not None else 0

    def apply_effect(self, player):
        player.try_dash()

import arcade

from scripts.skins.skin_manager import SkinManager

class BaseArtifact(arcade.Sprite):
    def __init__(self, x: int = 0, y: int = 0):
        # skin_manager = SkinManager()
        # super().__init__(filename=skin_manager.get_texture_path("artifacts", "base"))
        super().__init__()
        self.center_x = x
        self.center_y = y
        self.name = "Unnamed Artifact"
        self.cooldown = 10.0
        self.cooldown_timer = self.cooldown

    def apply_effect(self, *args, **kwargs):
        raise NotImplementedError("Subclasses must implement apply_effect.")

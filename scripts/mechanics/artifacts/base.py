import arcade
from scripts.utils.constants import ARTIFACT_SCALE

class BaseArtifact(arcade.Sprite):
    def __init__(self, image_path):
        super().__init__(filename=image_path, scale=ARTIFACT_SCALE)
        self.name = "Unnamed"
        self.cooldown = 0
        self.cooldown_timer = 0

    def apply_effect(self, *args, **kwargs):
        raise NotImplementedError("Subclasses must implement apply_effect.")

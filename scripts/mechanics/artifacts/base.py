import arcade
from scripts.utils.constants import ARTIFACT_SCALE
from scripts.skins.skin_manager import skin_manager

class BaseArtifact(arcade.Sprite):
    def __init__(self, artifact_type, scale=None):
        super().__init__()
        self.artifact_type = artifact_type
        self.name = "Unnamed"
        self.cooldown = 0
        self.cooldown_timer = 0
        
        # Initialize with proper texture
        self.update_texture()
        
    def update_texture(self):
        """Update the texture based on current skin settings"""
        self.texture = skin_manager.get_texture("artifacts", self.artifact_type)
        self.scale = skin_manager.get_artifact_scale()
        
    def apply_effect(self, *args, **kwargs):
        raise NotImplementedError("Subclasses must implement apply_effect.")

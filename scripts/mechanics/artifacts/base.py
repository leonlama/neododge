import arcade
from scripts.utils.constants import ARTIFACT_SCALE
from scripts.skins.skin_manager import skin_manager
from scripts.utils.skin_logic import apply_skin_to_artifact

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
        self.texture = skin_manager.get_texture("artifacts", self.artifact_type, force_reload=True)
        self.scale = skin_manager.get_artifact_scale()
        
    def update(self, delta_time: float = 0):
        """Update method that should be called each frame"""
        # Update texture each frame to ensure current skin is used
        self.update_texture()
        
        # Update cooldown timer if needed
        if self.cooldown_timer < self.cooldown:
            self.cooldown_timer += delta_time
        
    def apply_effect(self, *args, **kwargs):
        raise NotImplementedError("Subclasses must implement apply_effect.")

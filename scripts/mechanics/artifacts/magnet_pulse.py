from .base import BaseArtifact
from scripts.skins.skin_manager import skin_manager
from scripts.utils.resource_helper import resource_path

class MagnetPulseArtifact(BaseArtifact):
    def __init__(self, x, y):
        super().__init__(resource_path(skin_manager.get_texture_path("artifacts", "magnet_pulse")), scale=skin_manager.get_artifact_scale())
        self.center_x = x
        self.center_y = y
        self.name = "Magnet Pulse"
        self.cooldown = 10.0
        self.cooldown_timer = self.cooldown
    
    def update_texture(self):
        """Update the texture based on current skin settings"""
        self.texture = skin_manager.get_texture("artifacts", "magnet_pulse")
        self.scale = skin_manager.get_artifact_scale()

    def apply_effect(self, player, orbs):
        for orb in orbs:
            orb.center_x = player.center_x
            orb.center_y = player.center_y

    def update(self, delta_time):
        if self.cooldown_timer > 0:
            self.cooldown_timer -= delta_time
        
        # Update texture each frame to ensure current skin is used
        self.update_texture()

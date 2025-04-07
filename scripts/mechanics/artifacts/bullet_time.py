from .base import BaseArtifact
from scripts.skins.skin_manager import skin_manager
from scripts.utils.resource_helper import resource_path

class BulletTimeArtifact(BaseArtifact):
    def __init__(self, x, y):
        super().__init__(resource_path(skin_manager.get_texture_path("artifacts", "bullet_time")), scale=skin_manager.get_artifact_scale())
        self.center_x = x
        self.center_y = y
        self.name = "Bullet Time"
        self.cooldown = 10.0
        self.cooldown_timer = self.cooldown
        
    def update_texture(self):
        """Update the texture based on current skin settings"""
        self.texture = skin_manager.get_texture("artifacts", "bullet_time")
        self.scale = skin_manager.get_artifact_scale()

    def apply_effect(self, enemies):
        for enemy in enemies:
            for bullet in enemy.bullets:
                bullet.change_x *= 0.5
                bullet.change_y *= 0.5

    def update(self, delta_time):
        if self.cooldown_timer > 0:
            self.cooldown_timer -= delta_time
        
        # Update texture each frame to ensure current skin is used
        self.update_texture()

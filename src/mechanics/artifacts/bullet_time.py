from .base import BaseArtifact
from scripts.skins.skin_manager import skin_manager
from scripts.utils.skin_logic import apply_skin_to_artifact

class BulletTimeArtifact(BaseArtifact):
    def __init__(self, x, y):
        super().__init__("bullet_time")
        self.center_x = x
        self.center_y = y
        self.name = "Bullet Time"
        self.cooldown = 10.0
        self.cooldown_timer = self.cooldown
        
    def update_texture(self):
        """Update the texture based on current skin settings"""
        self.texture = skin_manager.get_texture("artifacts", "bullet_time", force_reload=True)
        self.scale = skin_manager.get_artifact_scale()

    def apply_effect(self, player, enemies):
        if self.cooldown_timer >= self.cooldown:
            for enemy in enemies:
                for bullet in enemy.bullets:
                    bullet.change_x *= 0.5
                    bullet.change_y *= 0.5
            self.cooldown_timer = 0
            print("⏱️ Bullet Time used!")
        else:
            print("❌ Bullet Time on cooldown.")

    def update(self, delta_time):
        if self.cooldown_timer < self.cooldown:
            self.cooldown_timer += delta_time
        
        # Update texture each frame to ensure current skin is used
        self.update_texture()


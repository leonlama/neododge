from .base import BaseArtifact
from scripts.skins.skin_manager import skin_manager

class DashArtifact(BaseArtifact):
    def __init__(self, x, y):
        super().__init__("dash")
        self.center_x = x
        self.center_y = y
        self.name = "Dash"
        self.cooldown = 10.0  # seconds
        self.cooldown_timer = self.cooldown  # Start fully ready!
    
    def update_texture(self):
        """Update the texture based on current skin settings"""
        self.texture = skin_manager.get_texture("artifacts", "dash")
        self.scale = skin_manager.get_artifact_scale()

    def update(self, delta_time: float = 0):
        # Update cooldown timer
        if self.cooldown_timer < self.cooldown:
            self.cooldown_timer += delta_time
        
        # Update texture each frame to ensure current skin is used
        self.update_texture()

    def apply_effect(self, player, *_):
        if self.cooldown_timer >= self.cooldown:
            player.perform_dash()
            self.cooldown_timer = 0
            print("⚡ Dash used!")
        else:
            print("❌ Dash on cooldown.")

from .base import BaseArtifact
from scripts.skins.skin_manager import skin_manager
from scripts.utils.skin_logic import apply_skin_to_artifact

class CloneDashArtifact(BaseArtifact):
    def __init__(self, x, y):
        super().__init__("clone_dash")
        self.center_x = x
        self.center_y = y
        self.name = "Clone Dash"
        self.cooldown = 10.0
        self.cooldown_timer = self.cooldown
        
    def update_texture(self):
        """Update the texture based on current skin settings"""
        self.texture = skin_manager.get_texture("artifacts", "clone_dash", force_reload=True)
        self.scale = skin_manager.get_artifact_scale()

    def apply_effect(self, player, enemies):
        if self.cooldown_timer >= self.cooldown:
            clone = player.clone()
            enemies.append(clone)
            self.cooldown_timer = 0
            print("🧪 Clone Dash used!")
        else:
            print("❌ Clone Dash on cooldown.")

    def update(self, delta_time):
        if self.cooldown_timer < self.cooldown:
            self.cooldown_timer += delta_time
        
        # Update texture each frame to ensure current skin is used
        self.update_texture()

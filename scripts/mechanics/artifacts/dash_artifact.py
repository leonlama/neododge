from .base import BaseArtifact
from scripts.skins.skin_manager import skin_manager
from scripts.utils.skin_logic import apply_skin_to_artifact

class DashArtifact(BaseArtifact):
    def __init__(self, x, y):
        super().__init__("dash")
        self.center_x = x
        self.center_y = y
        self.name = "Dash"
        self.cooldown = 10.0  # seconds
        self.cooldown_timer = 10.0  # starts ready
    
    def update_texture(self):
        """Update the texture based on current skin settings"""
        self.texture = skin_manager.get_texture("artifacts", "dash", force_reload=True)
        self.scale = skin_manager.get_artifact_scale()

    def update(self, delta_time: float = 0):
        # Increase the cooldown timer
        self.cooldown_timer += delta_time
        
        # Update texture each frame to ensure current skin is used
        self.update_texture()

    def apply_effect(self, player, *_):
        """Apply the dash effect to the player"""
        # Check if cooldown allows
        if self.cooldown_timer >= self.cooldown:
            # Perform the dash
            player.perform_dash()

            # Reset artifact cooldown
            self.cooldown_timer = 0

            print("⚡ Dash artifact used!")
        else:
            print(f"❌ Dash artifact on cooldown. ({self.cooldown_timer:.1f}/{self.cooldown}s)")

from .base import BaseArtifact
from src.skins.skin_manager import skin_manager
from src.core.scaling import get_scale

class BulletTimeArtifact(BaseArtifact):
    def __init__(self, position_x, position_y):
        super().__init__(artifact_id="bullet_time", position_x=position_x, position_y=position_y, name="Bullet Time")
        self.cooldown_max = 10.0  # Override default cooldown
        self.cooldown_timer = 0.0  # Start ready to use
        
        # Load initial texture
        self._load_texture()
        
    def _load_texture(self):
        """Load the artifact texture"""
        self.texture = skin_manager.get_texture("artifacts", "bullet_time", force_reload=False)
        self.scale = get_scale('artifact')

    def apply_effect(self, player, game_state):
        """Apply bullet time effect to the game"""
        if self.is_ready():
            if game_state and hasattr(game_state, "enemies"):
                for enemy in game_state.enemies:
                    if hasattr(enemy, "bullets"):
                        for bullet in enemy.bullets:
                            bullet.change_x *= 0.5
                            bullet.change_y *= 0.5
            
            # Set cooldown
            self.cooldown_timer = self.cooldown_max
            print("⏱️ Bullet Time used!")
            return True
        else:
            print("❌ Bullet Time on cooldown.")
            return False

    def update(self, delta_time):
        """Update the artifact state"""
        # Call parent update to handle cooldown
        super().update(delta_time)

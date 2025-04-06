from .base import BaseArtifact

class BulletTimeArtifact(BaseArtifact):
    def __init__(self):
        super().__init__()
        self.name = "Bullet Time"

    def apply_effect(self, enemies):
        for enemy in enemies:
            for bullet in enemy.bullets:
                bullet.change_x *= 0.5
                bullet.change_y *= 0.5

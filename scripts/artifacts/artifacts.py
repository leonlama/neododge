
import arcade

class BaseArtifact(arcade.Sprite):
    def __init__(self, texture_color, radius=24, name="Unknown"):
        super().__init__()
        self.texture = arcade.make_soft_circle_texture(radius, texture_color, outer_alpha=255)
        self.center_x = 0
        self.center_y = 0
        self.name = name

class DashArtifact(BaseArtifact):
    def __init__(self, x=0, y=0):
        super().__init__(arcade.color.MAGENTA)
        self.center_x = x
        self.center_y = y
        self.name = "Dash"

class MagnetPulseArtifact(BaseArtifact):
    def __init__(self):
        super().__init__(arcade.color.SKY_BLUE, name="Magnet Pulse")

    def apply_effect(self, player, orbs):
        """Pulls nearby orbs toward the player."""
        for orb in orbs:
            dx = player.center_x - orb.center_x
            dy = player.center_y - orb.center_y
            orb.center_x += dx * 0.15  # Pull strength
            orb.center_y += dy * 0.15
        print("🔵 Magnet pulse active")

class SlowFieldArtifact(BaseArtifact):
    def __init__(self):
        super().__init__(arcade.color.LIGHT_PURPLE, name="Slow Field")

    def apply_effect(self, player, bullets):
        """Slows down bullets in a radius around the player."""
        for bullet in bullets:
            dist = ((bullet.center_x - player.center_x) ** 2 + (bullet.center_y - player.center_y) ** 2) ** 0.5
            if dist < 180:
                bullet.speed *= 0.3
        print("🌀 Slow field active")

class BulletTimeArtifact(BaseArtifact):
    def __init__(self):
        super().__init__(arcade.color.LIGHT_YELLOW, name="Bullet Time")

    def apply_effect(self, enemies):
        """Slows enemies and their bullets globally."""
        for enemy in enemies:
            enemy.speed *= 0.3
            for bullet in enemy.bullets:
                bullet.speed *= 0.3
        print("⏳ Bullet time active")

class CloneDashArtifact(BaseArtifact):
    def __init__(self):
        super().__init__(arcade.color.GRAY, name="Clone Dash")

    def apply_effect(self, player, clones):
        """Creates a stationary clone at the dash position to distract enemies."""
        clone = type(player)(player.center_x, player.center_y)
        clone.is_clone = True
        clones.append(clone)
        print("👤 Clone created")

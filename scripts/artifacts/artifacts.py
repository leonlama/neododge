
import arcade

class BaseArtifact(arcade.Sprite):
    def __init__(self, texture_color, radius=24):
        super().__init__()
        self.texture = arcade.make_soft_circle_texture(radius, texture_color, outer_alpha=255)
        self.center_x = 0
        self.center_y = 0

class DashArtifact(arcade.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.texture = arcade.make_soft_circle_texture(24, arcade.color.MAGENTA, outer_alpha=255)
        self.center_x = x
        self.center_y = y

class MagnetPulseArtifact(BaseArtifact):
    def __init__(self):
        super().__init__(arcade.color.SKY_BLUE)

class SlowFieldArtifact(BaseArtifact):
    def __init__(self):
        super().__init__(arcade.color.LIGHT_PURPLE)

class BulletTimeArtifact(BaseArtifact):
    def __init__(self):
        super().__init__(arcade.color.LIGHT_YELLOW)

class CloneDashArtifact(BaseArtifact):
    def __init__(self):
        super().__init__(arcade.color.GRAY)

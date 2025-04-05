import arcade

class DashArtifact(arcade.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.texture = arcade.make_soft_circle_texture(24, arcade.color.MAGENTA, outer_alpha=255)
        self.center_x = x
        self.center_y = y

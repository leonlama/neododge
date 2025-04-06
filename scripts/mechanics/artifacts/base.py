import arcade

class BaseArtifact(arcade.Sprite):
    def __init__(self, x: int = 0, y: int = 0, texture: arcade.Texture = None, scale: float = 0.5):
        if texture is None:
            texture = arcade.make_circle_texture(30, arcade.color.GRAY)
        super().__init__(texture=texture, scale=scale)
        self.center_x = x
        self.center_y = y
        self.name = "Unnamed Artifact"
        self.cooldown = 10.0
        self.active = False

    def apply_effect(self, *args, **kwargs):
        raise NotImplementedError("Subclasses must implement apply_effect.")

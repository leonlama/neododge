import arcade

class Orb(arcade.Sprite):
    def __init__(self, x, y, orb_type="gray"):
        super().__init__()
        self.orb_type = orb_type
        color = arcade.color.GRAY

        if orb_type == "red":
            color = arcade.color.RED
        elif orb_type == "gold":
            color = arcade.color.GOLD

        self.texture = arcade.make_soft_circle_texture(18, color, outer_alpha=255)
        self.center_x = x
        self.center_y = y
        self.age = 0

    def update(self, delta_time: float = 1 / 60):
        self.age += delta_time

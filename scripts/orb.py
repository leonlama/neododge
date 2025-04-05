import arcade

class Orb(arcade.Sprite):
    def __init__(self, x, y, orb_type="gray"):
        super().__init__()
        self.orb_type = orb_type
        self.age = 0

        color_map = {
            "gray": arcade.color.GRAY,
            "red": arcade.color.RED,
            "gold": arcade.color.GOLD,
            "speed_10": arcade.color.BLUE_BELL,
            "speed_20": arcade.color.BLUE_VIOLET,
            "speed_35": arcade.color.DARK_BLUE,
            "mult_1_5": arcade.color.ORANGE,
            "mult_2": arcade.color.YELLOW_ORANGE,
            "cooldown": arcade.color.PURPLE,
            "shield": arcade.color.LIGHT_GREEN,
        }

        color = color_map.get(orb_type, arcade.color.WHITE)
        self.texture = arcade.make_soft_circle_texture(18, color, outer_alpha=255)
        self.center_x = x
        self.center_y = y

    def update(self, delta_time: float = 1 / 60):
        self.age += delta_time

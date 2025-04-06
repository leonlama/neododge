import arcade
from arcade import AnimationKeyframe

class Coin(arcade.AnimatedTimeBasedSprite):
    def __init__(self, x, y):
        super().__init__()

        texture_list = arcade.load_spritesheet(
            "assets/items/coin2_20x20.png",  # Adjust path as needed
            sprite_width=20,
            sprite_height=20,
            columns=9,
            count=9
        )

        for i, texture in enumerate(texture_list):
            self.frames.append(AnimationKeyframe(i, 100, texture))  # 100 ms per frame

        self.texture = texture_list[0]  # initial frame
        self.center_x = x
        self.center_y = y
        self.scale = 1
        self.coin_value = 1 
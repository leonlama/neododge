import arcade
from arcade import AnimationKeyframe

class Coin(arcade.AnimatedTimeBasedSprite):
    """Animated coin that can be collected by the player."""

    def __init__(self, x, y):
        super().__init__()

        # Load the coin animation
        try:
            # Try to load the spritesheet
            texture_list = arcade.load_spritesheet(
                "assets/items/coin/gold_coin.png",
                sprite_width=20,
                sprite_height=20,
                columns=9,
                count=9
            )

            # Create animation frames
            for i, texture in enumerate(texture_list):
                self.frames.append(AnimationKeyframe(i, 100, texture))  # 100 ms per frame

            # Set initial texture
            self.texture = texture_list[0]

        except Exception as e:
            print(f"Error loading coin animation: {e}")
            # Fallback to a simple circle if animation fails
            self.texture = arcade.make_circle_texture(20, arcade.color.GOLD)

        # Set position
        self.center_x = x
        self.center_y = y

        # Set properties
        self.scale = 1.0
        self.coin_value = 1
import arcade
from arcade import AnimationKeyframe
from scripts.utils.resource_helper import resource_path
from scripts.skins.skin_manager import skin_manager

class Coin(arcade.AnimatedTimeBasedSprite):
    """
    Coin sprite that uses the skin manager for textures
    """
    def __init__(self, x, y):
        super().__init__()

        try:
            # Try to load the spritesheet
            spritesheet_path = resource_path("assets/items/coin2_20x20.png")

            if not os.path.exists(spritesheet_path):
                # Try alternative path
                alt_path = resource_path("assets/items/coin/coin_spritesheet.png")
                if os.path.exists(alt_path):
                    spritesheet_path = alt_path

            texture_list = arcade.load_spritesheet(
                spritesheet_path,
                sprite_width=20,
                sprite_height=20,
                columns=9,
                count=9
            )

            for i, texture in enumerate(texture_list):
                self.frames.append(AnimationKeyframe(i, 100, texture))  # 100 ms per frame

            self.texture = texture_list[0]  # initial frame

        except Exception as e:
            print(f"Error loading coin textures: {e}")
            # Create a fallback texture
            fallback = arcade.make_soft_circle_texture(20, arcade.color.GOLD)
            self.texture = fallback
            # Add a single frame for animation
            self.frames.append(AnimationKeyframe(0, 100, fallback))

        self.center_x = x
        self.center_y = y
        self.scale = 1
        self.coin_value = 1

def create_coin(x, y):
    """
    Factory function to create a coin

    Args:
        x: X coordinate
        y: Y coordinate

    Returns:
        Coin: A coin sprite
    """
    return Coin(x, y)
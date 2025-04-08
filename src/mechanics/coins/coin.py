import arcade

class Coin(arcade.Sprite):
    def __init__(self, x, y, value=1):
        super().__init__()
        self.center_x = x
        self.center_y = y
        self.value = value
        self.texture = arcade.load_texture("assets/items/coin/gold_coin.png")
        self.scale = 0.5
        self.age = 0

    def update(self, delta_time: float = 1/60):
        self.age += delta_time
import arcade
from scripts.player import Player

# --- Constants ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Neododge"

class NeododgeGame(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
        arcade.set_background_color(arcade.color.BLACK)
        self.player = None

    def setup(self):
        self.player = Player(self.width // 2, self.height // 2)

    def on_draw(self):
        self.clear()
        self.player.draw()

    def on_update(self, delta_time):
        self.player.update(delta_time)

    def on_mouse_press(self, x, y, button, modifiers):
        if button == arcade.MOUSE_BUTTON_RIGHT:
            self.player.set_target(x, y)

if __name__ == "__main__":
    game = NeododgeGame()
    game.setup()
    arcade.run()

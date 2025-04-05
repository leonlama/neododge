import arcade

# --- Constants ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Neododge"

class NeododgeGame(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
        arcade.set_background_color(arcade.color.BLACK)

    def setup(self):
        """Set up the game. Called once when the game starts."""
        pass

    def on_draw(self):
        """Render the screen."""
        self.clear()
        # Later: Draw player, enemies, etc.

    def on_update(self, delta_time):
        """All the logic to move and update game state."""
        pass

if __name__ == "__main__":
    game = NeododgeGame()
    game.setup()
    arcade.run()


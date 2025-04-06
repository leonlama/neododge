import arcade

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Neododge"

class StartView(arcade.View):
    def __init__(self):
        super().__init__()
        arcade.set_background_color(arcade.color.BLACK)

    def on_draw(self):
        self.clear()
        arcade.draw_text("NEODODGE", SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 60,
                         arcade.color.WHITE, font_size=48, anchor_x="center", font_name="Kenney Pixel")
        arcade.draw_text("Press any key or click to play", SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 - 40,
                         arcade.color.LIGHT_GRAY, font_size=20, anchor_x="center")

    def start_game(self):
        from main import NeododgeGame
        game_view = NeododgeGame()
        game_view.setup()
        self.window.show_view(game_view)

    def on_key_press(self, key, modifiers):
        self.start_game()

    def on_mouse_press(self, x, y, button, modifiers):
        self.start_game()

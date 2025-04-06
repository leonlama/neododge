import arcade

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

class GameOverView(arcade.View):
    def __init__(self, final_score: int):
        super().__init__()
        self.final_score = final_score

    def on_show(self):
        arcade.set_background_color(arcade.color.BLACK)

    def on_draw(self):
        self.clear()
        arcade.draw_text("GAME OVER", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 80,
                         arcade.color.RED, 48, anchor_x="center", font_name="Kenney Pixel")
        arcade.draw_text(f"Final Score: {self.final_score}", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 20,
                         arcade.color.WHITE, 28, anchor_x="center")
        arcade.draw_text("Press ENTER to Play Again", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 60,
                         arcade.color.GRAY, 18, anchor_x="center")

    def on_key_press(self, symbol, modifiers):
        if symbol == arcade.key.ENTER:
            from main import NeododgeGame
            game = NeododgeGame()
            game.setup()
            self.window.show_view(game)

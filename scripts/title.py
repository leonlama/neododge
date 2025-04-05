import arcade

SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720

class TitleView(arcade.View):
    def __init__(self):
        super().__init__()
        self.play_button = arcade.gui.UIFlatButton(
            text="▶ Play", center_x=SCREEN_WIDTH // 2, center_y=SCREEN_HEIGHT // 2, width=200
        )
        self.manager = arcade.gui.UIManager()
        self.manager.enable()
        self.manager.add(self.play_button)

    def on_show(self):
        arcade.set_background_color(arcade.color.BLACK)

    def on_draw(self):
        self.clear()

        # Title with a neon glow effect (cyan + shadow)
        arcade.draw_text("NEODODGE", 
                         SCREEN_WIDTH / 2 + 2, SCREEN_HEIGHT / 2 + 52,
                         arcade.color.GRAY, font_size=72, anchor_x="center", font_name="Kenney Future")
        arcade.draw_text("NEODODGE", 
                         SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 50,
                         arcade.color.CYAN, font_size=72, anchor_x="center", font_name="Kenney Future")

        # Thin line under title for retro vibe
        arcade.draw_line(SCREEN_WIDTH / 2 - 150, SCREEN_HEIGHT / 2 + 40, 
                         SCREEN_WIDTH / 2 + 150, SCREEN_HEIGHT / 2 + 40, 
                         arcade.color.LIGHT_GRAY, 1)

        # Subtext
        arcade.draw_text("Click to Play",
                         SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 - 40,
                         arcade.color.LIGHT_GRAY, font_size=20, anchor_x="center", font_name="Kenney Pixel")

        # Optional "arcade insert coin" style text
        arcade.draw_text("Dodge everything. Survive the neon waves.",
                         SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 - 100,
                         arcade.color.DARK_GRAY, font_size=14, anchor_x="center")

    def on_update(self, delta_time):
        pass

    def on_hide_view(self):
        self.manager.disable()

    def setup_callbacks(self, window, game_view):
        @self.play_button.event("on_click")
        def on_click_play(event):
            print("▶ Starting game...")
            window.show_view(game_view)

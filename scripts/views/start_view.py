import arcade
import pyglet
from scripts.utils.resource_helper import resource_path
from scripts.views.game_view import NeododgeGame

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Neododge"

class StartView(arcade.View):
    def __init__(self):
        super().__init__()
        self.music = None
        self.media_player = None

    def on_show(self):
        arcade.set_background_color(arcade.color.BLACK)

        # Load music
        music_path = resource_path("assets/audio/themev1.mp3")
        try:
            self.music = arcade.load_sound(music_path)
            self.media_player = arcade.play_sound(self.music, volume=0.4, looping=True)
        except Exception as e:
            print("Failed to load music:", e)

    def on_hide_view(self):
        # Stop music when view changes
        if self.media_player:
            self.media_player.pause()

    def on_draw(self):
        self.clear()
        arcade.draw_text("NEODODGE", self.window.width // 2, self.window.height // 2 + 50,
                         arcade.color.WHITE, font_size=36, anchor_x="center", font_name="Kenney Pixel")
        arcade.draw_text("Click to Start", self.window.width // 2, self.window.height // 2 - 50,
                         arcade.color.LIGHT_GRAY, font_size=20, anchor_x="center")

    def on_key_press(self, key, modifiers):
        self.start_game()

    def start_game(self):
        # Stop title music
        if self.media_player:
            self.media_player.pause()

        # Play click sound and voice line
        click_sound = arcade.load_sound(resource_path("assets/audio/start_click.wav"))
        arcade.play_sound(click_sound)

        # Create game view and show it
        game_view = NeododgeGame()
        game_view.setup()
        
        # Delay switching views using pyglet
        pyglet.clock.schedule_once(lambda dt: self.window.show_view(game_view), 1.2)

    def on_mouse_press(self, x, y, button, modifiers):
        self.start_game()

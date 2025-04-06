import arcade
import os
import pyglet

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
        music_path = os.path.join("assets", "audio", "themev1.mp3")
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
        arcade.draw_text("NEODODGE", SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 60,
                         arcade.color.WHITE, font_size=48, anchor_x="center", font_name="Kenney Pixel")
        arcade.draw_text("Press any key or click to play", SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 - 40,
                         arcade.color.LIGHT_GRAY, font_size=20, anchor_x="center")

    def start_game(self):
        from main import NeododgeGame
        game_view = NeododgeGame()
        game_view.setup()

        # Stop title music
        if self.media_player:
            self.media_player.pause()

        # Play click sound and voice line
        click_sound = arcade.load_sound("assets/audio/start_click.wav")
        #voice_line = arcade.load_sound("assets/audio/lets_go.wav")
        arcade.play_sound(click_sound)
        #arcade.play_sound(voice_line)

        # Delay switching views using pyglet
        pyglet.clock.schedule_once(lambda dt: self.window.show_view(game_view), 1.2)

    def on_key_press(self, key, modifiers):
        self.start_game()

    def on_mouse_press(self, x, y, button, modifiers):
        self.start_game()

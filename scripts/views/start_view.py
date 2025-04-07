import arcade
import pyglet
from scripts.utils.resource_helper import resource_path
from scripts.views.game_view import NeododgeGame
from scripts.skins.skin_manager import skin_manager

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
        arcade.draw_text("Press 'T' to toggle skin", self.window.width // 2, self.window.height // 2 - 80,
                         arcade.color.LIGHT_GRAY, font_size=16, anchor_x="center")
        arcade.draw_text(f"Current skin: {skin_manager.data['selected']}", self.window.width // 2, self.window.height // 2 - 110,
                         arcade.color.LIGHT_GRAY, font_size=14, anchor_x="center")

    def on_key_press(self, key, modifiers):
        if key == arcade.key.T:
            # Toggle skin
            current = skin_manager.data["selected"]
            new_skin = "default" if current == "mdma" else "mdma"
            skin_manager.select(new_skin)
            print(f"🎨 Switched to skin: {new_skin}")
        else:
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
        if self.media_player:
            arcade.stop_sound(self.media_player)  # ✅ Correct
        try:
            from scripts.views.game_view import NeododgeGame
            game_view = NeododgeGame()
            game_view.setup()  # Make sure setup() is called to initialize self.player
            self.window.show_view(game_view)
        except Exception as e:
            print("🚨 Failed to start game:", e)
            arcade.play_sound(arcade.load_sound(resource_path("assets/audio/damage.wav")))  # tiny feedback

import arcade
import pyglet
from src.core.resource_manager import resource_path
from src.skins.skin_manager import skin_manager
from src.core.constants import SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE

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
        arcade.draw_text("NEODODGE", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50,
                         arcade.color.WHITE, font_size=36, anchor_x="center", font_name="Kenney Pixel")
        arcade.draw_text("Click to Start", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50,
                         arcade.color.LIGHT_GRAY, font_size=20, anchor_x="center")
        arcade.draw_text("Press 'T' to toggle skin", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 80,
                         arcade.color.LIGHT_GRAY, font_size=16, anchor_x="center")
        arcade.draw_text(f"Current skin: {skin_manager.get_selected()}", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 110,
                         arcade.color.LIGHT_GRAY, font_size=14, anchor_x="center")

    def on_key_press(self, key, modifiers):
        if key == arcade.key.T:
            # Toggle skin
            current = skin_manager.get_selected()
            new_skin = "default" if current == "mdma" else "mdma"
            if skin_manager.select(new_skin):
                print(f"Skin changed to: {new_skin}")
        else:
            self.start_game()

    def start_game(self):
        # Stop title music
        if self.media_player:
            self.media_player.pause()

        # Play click sound
        try:
            click_sound = arcade.load_sound(resource_path("assets/audio/start_click.wav"))
            arcade.play_sound(click_sound)
        except Exception as e:
            print(f"Failed to load click sound: {e}")

        # Create game view and show it
        from src.views.game_view import NeododgeGame
        game_view = NeododgeGame()
        game_view.setup()

        # Delay switching views using pyglet
        pyglet.clock.schedule_once(lambda dt: self.window.show_view(game_view), 0.5)

    def on_mouse_press(self, x, y, button, modifiers):
        self.start_game()

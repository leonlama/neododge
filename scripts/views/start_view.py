import arcade
import pyglet
import math
from scripts.utils.resource_helper import resource_path
from scripts.views.game_view import NeododgeGame
from scripts.utils.skin_loader import SkinManager
from scripts.skins.skin_manager import skin_manager

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Neododge"

class StartView(arcade.View):
    def __init__(self):
        super().__init__()
        self.music = None
        self.media_player = None
        self.last_skin_update = 0  # For animation timing
        self.skin_change_indicator = 0.0  # Pulse animation

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
        arcade.draw_text("NEODODGE", int(self.window.width // 2), int(self.window.height // 2 + 50),
                         arcade.color.WHITE, font_size=36, anchor_x="center", font_name="Kenney Pixel")
        arcade.draw_text("Press SPACE to start", int(self.window.width // 2), int(self.window.height // 2 - 20),
                         arcade.color.WHITE, font_size=20, anchor_x="center")
        arcade.draw_text("Press 'T' to toggle skin", int(self.window.width // 2), int(self.window.height // 2 - 50),
                         arcade.color.WHITE, font_size=20, anchor_x="center")
        
        # Pulse effect for visual feedback
        pulse = abs(math.sin(self.skin_change_indicator * 3)) * 50 + 205
        self.skin_change_indicator = max(0, self.skin_change_indicator - 0.1)

        # Draw skin name with animation
        arcade.draw_text(
            f"Current skin: {skin_manager.get_selected()}",
            int(self.window.width // 2),
            int(self.window.height // 2 - 80),
            arcade.color.YELLOW,
            font_size=16,
            anchor_x="center",
            bold=True
        )

    def on_key_press(self, symbol, modifiers):
        if symbol == arcade.key.T:
            self.toggle_skin()
        elif symbol == arcade.key.SPACE:
            self.start_game()

    def toggle_skin(self):
        """Toggle between available skin sets"""
        # Determine the next skin
        current_skin = skin_manager.get_selected()
        next_skin = "mdma" if current_skin == "default" else "default"

        # Make sure the skin is unlocked
        if next_skin not in skin_manager.unlocked_skins:
            skin_manager.unlock_skin(next_skin)

        # Toggle to the next skin
        skin_manager.select(next_skin)
        
        # Update any visual elements in the start view
        self.update_visual_elements()
        
        # Visual feedback
        self.skin_change_indicator = 1.0
        arcade.play_sound(arcade.load_sound(
            resource_path("assets/audio/buff.wav")
        ))
        print(f"🎨 Switched to skin: {next_skin}")
        
        return skin_manager.get_selected()

    def update_visual_elements(self):
        """Update visual elements in the start view after skin change"""
        # Update any skin-dependent elements in the start view
        # For example, if you show sample artifacts or player icon
        pass

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

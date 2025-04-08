import arcade
import random
from src.core.constants import SCREEN_WIDTH, SCREEN_HEIGHT
from src.core.resource_manager import load_texture, load_sound
from src.views.game_view import NeododgeGame
from src.skins.skin_manager import skin_manager
import pyglet.media

class StartView(arcade.View):
    def __init__(self):
        super().__init__()
        self.background = arcade.make_soft_circle_texture(
            SCREEN_WIDTH * 2, 
            (20, 20, 20), 
            outer_alpha=255, 
            center_alpha=255
        )

        # Load start sound
        self.start_sound = load_sound("assets/audio/start_click.wav")
        
        # Initialize music variables
        self.background_music = None
        self.music_player = None

        # Setup particles for background
        self.particles = []
        for _ in range(50):
            self.particles.append({
                "x": random.randint(0, SCREEN_WIDTH),
                "y": random.randint(0, SCREEN_HEIGHT),
                "size": random.uniform(1, 3),
                "speed": random.uniform(20, 50),
                "color": (
                    random.randint(100, 255),
                    random.randint(100, 255),
                    random.randint(100, 255)
                )
            })

    def on_show(self):
        arcade.set_background_color(arcade.color.BLACK)
        # Play background music
        if not self.background_music:
            bgm_path = "assets/audio/themev1.mp3"
            bgm_source = pyglet.media.load(bgm_path)
            self.music_player = pyglet.media.Player()
            self.music_player.queue(bgm_source)
            self.music_player.volume = 0.25
            self.music_player.loop = True
            self.music_player.play()
            self.background_music = bgm_source

    def on_draw(self):
        self.clear()

        # Draw background particles
        for particle in self.particles:
            arcade.draw_circle_filled(
                particle["x"], 
                particle["y"], 
                particle["size"], 
                particle["color"]
            )

        # Draw title
        arcade.draw_text(
            "NEODODGE",
            SCREEN_WIDTH / 2,
            SCREEN_HEIGHT / 2 + 50,
            arcade.color.WHITE,
            font_size=50,
            anchor_x="center",
            font_name="Kenney Pixel"
        )

        # Draw instructions
        arcade.draw_text(
            "Click to Start",
            SCREEN_WIDTH / 2,
            SCREEN_HEIGHT / 2 - 30,
            arcade.color.LIGHT_GRAY,
            font_size=20,
            anchor_x="center",
            font_name="Kenney Pixel"
        )

        # Draw controls info
        arcade.draw_text(
            "Controls: Mouse to move, Space to dash",
            SCREEN_WIDTH / 2,
            SCREEN_HEIGHT / 2 - 70,
            arcade.color.LIGHT_GRAY,
            font_size=14,
            anchor_x="center",
            font_name="Kenney Pixel"
        )

        # Draw skin toggle info
        arcade.draw_text(
            "Press T to toggle skins",
            SCREEN_WIDTH / 2,
            SCREEN_HEIGHT / 2 - 100,
            arcade.color.LIGHT_GRAY,
            font_size=14,
            anchor_x="center",
            font_name="Kenney Pixel"
        )

        # Draw current skin info
        arcade.draw_text(
            f"Current skin: {skin_manager.current_skin}",
            SCREEN_WIDTH / 2,
            SCREEN_HEIGHT / 2 - 125,
            arcade.color.LIGHT_GRAY,
            font_size=12,
            anchor_x="center",
            font_name="Kenney Pixel"
        )

        # Draw version
        arcade.draw_text(
            "v1.2.0",
            SCREEN_WIDTH - 10,
            10,
            arcade.color.GRAY,
            font_size=12,
            anchor_x="right",
            font_name="Kenney Pixel"
        )

    def on_update(self, delta_time):
        # Update particles
        for particle in self.particles:
            particle["y"] -= particle["speed"] * delta_time

            # Reset particles that go off screen
            if particle["y"] < 0:
                particle["y"] = SCREEN_HEIGHT
                particle["x"] = random.randint(0, SCREEN_WIDTH)

    def on_key_press(self, key, modifiers):
        """Handle key press events"""
        if key == arcade.key.T:
            # Toggle skin
            self.toggle_skin()
        else:
            # Any other key starts the game
            self.start_game()

    def toggle_skin(self):
        """Toggle between available skins"""
        # Get available skins
        available_skins = list(skin_manager.skin_data.keys())
        current_skin = skin_manager.current_skin

        # Find next skin
        if current_skin in available_skins:
            current_index = available_skins.index(current_skin)
            next_index = (current_index + 1) % len(available_skins)
            next_skin = available_skins[next_index]

            # Apply new skin
            if skin_manager.set_skin(next_skin):
                print(f"🎨 Skin set to: {next_skin}")
            else:
                print(f"⚠️ Failed to switch skin")
        else:
            print(f"⚠️ Current skin '{current_skin}' not found in available skins")

    def on_mouse_press(self, x, y, button, modifiers):
        # Play sound
        if self.start_sound:
            arcade.play_sound(self.start_sound)

        # Start the game
        self.start_game()

    def start_game(self):
        # Stop the music when starting the game
        if self.music_player:
            arcade.stop_sound(self.music_player)
            
        game_view = NeododgeGame()
        game_view.setup()
        self.window.show_view(game_view)
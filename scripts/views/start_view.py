import arcade
from scripts.views.game_view import NeododgeGame

class StartView(arcade.View):
    """
    Main menu view for the game.

    Responsibilities:
    - Display the game title and instructions
    - Handle user input for starting the game
    - Allow toggling between available skins
    """

    def __init__(self):
        super().__init__()
        self.music = None
        self.media_player = None
        self.setup()

    def setup(self):
        """Set up the start view elements."""
        # Any setup code here
        pass

    def on_show(self):
        """Called when this view becomes active."""
        arcade.set_background_color(arcade.color.BLACK)
        
        # Load and play music
        self._load_music()

    def on_draw(self):
        """Render the screen."""
        arcade.start_render()

        # Draw title and instructions
        self._draw_title()
        self._draw_instructions()
        self._draw_skin_info()

    def _draw_title(self):
        """Draw the game title."""
        arcade.draw_text("NeoDodge", 
                         self.window.width/2, 
                         self.window.height/2 + 50,
                         arcade.color.WHITE, 
                         font_size=50, 
                         anchor_x="center")

    def _draw_instructions(self):
        """Draw game instructions."""
        arcade.draw_text("Press SPACE to start", 
                         self.window.width/2, 
                         self.window.height/2 - 20,
                         arcade.color.WHITE, 
                         font_size=20, 
                         anchor_x="center")

        arcade.draw_text("Press T to toggle skin", 
                         self.window.width/2, 
                         self.window.height/2 - 50,
                         arcade.color.WHITE, 
                         font_size=20, 
                         anchor_x="center")

    def _draw_skin_info(self):
        """Draw current skin information."""
        arcade.draw_text(f"Current skin: {self.window.skin_manager.data['selected']}", 
                         self.window.width/2, 
                         self.window.height/2 - 80,
                         arcade.color.YELLOW, 
                         font_size=16, 
                         anchor_x="center")

    def _load_music(self):
        """Load and play background music."""
        try:
            from scripts.utils.resource_helper import resource_path
            self.music = arcade.load_sound(resource_path("assets/audio/menu_music.mp3"))
            self.media_player = arcade.play_sound(self.music, looping=True)
        except Exception as e:
            print(f"Warning: Could not load or play music: {e}")

    def on_key_press(self, symbol, modifiers):
        """Handle key press events."""
        if symbol == arcade.key.T:
            self.toggle_skin()
        else:
            # Print debug information
            print(f"Key pressed: {symbol}")
            self._start_game()

    def on_mouse_press(self, x, y, button, modifiers):
        """Handle mouse press events."""
        print(f"Mouse pressed at ({x}, {y})")
        self._start_game()

    def _start_game(self):
        """Start a new game."""
        try:
            print("Starting game...")

            # Play click sound if available
            try:
                from scripts.utils.resource_helper import resource_path
                click_sound = arcade.load_sound(resource_path("assets/audio/start_click.wav"))
                arcade.play_sound(click_sound)
            except Exception as e:
                print(f"Warning: Could not play click sound: {e}")

            # Stop music
            if self.media_player:
                self.media_player.pause()

            # Create and setup game view
            from scripts.views.game_view import NeododgeGame
            game_view = NeododgeGame()
            game_view.setup()

            # Show the game view
            self.window.show_view(game_view)
            print("Game view shown")
        except Exception as e:
            print(f"❌ Error starting game: {e}")
            import traceback
            traceback.print_exc()

    def toggle_skin(self):
        """Toggle between available skin sets."""
        try:
            self.window.skin_manager.toggle_skin()
        except Exception as e:
            print(f"❌ Error toggling skin: {e}")
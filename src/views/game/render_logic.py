import arcade
from src.ui.improved_hud import draw_hud, draw_wave_message, draw_pickup_texts

def draw_game_elements(self):
        """Draw all game elements."""
        # Activate the game camera
        self.camera.use()

        # Draw game elements
        self.enemies.draw()
        self.orbs.draw()
        self.coins.draw()
        self.artifacts.draw()

        # Draw player
        self.player.draw()

        # Draw enemy bullets
        for enemy in self.enemies:
            if hasattr(enemy, 'bullets'):
                enemy.bullets.draw()

        # Draw dash artifact if it exists
        if self.dash_artifact:
            self.dash_artifact.draw()

        # Activate the GUI camera for HUD elements
        self.gui_camera.use()

def draw_improved_hud(self):
        """Draw the improved HUD."""
        from src.ui.improved_hud import draw_hud

        # Ensure heart textures exist
        if not hasattr(self, 'heart_textures') or not self.heart_textures.get('red') or not self.heart_textures.get('gray'):
            # Create fallback textures
            self.heart_textures = {
                "red": arcade.make_soft_circle_texture(30, arcade.color.RED),
                "gray": arcade.make_soft_circle_texture(30, arcade.color.GRAY)
            }

        # Get the current wave number
        wave_number = getattr(self.wave_manager, 'wave', 1)

        # Calculate the wave time left as a countdown
        wave_time_left = max(0, int(self.wave_manager.wave_duration - self.wave_manager.wave_timer))

        try:
            # Draw HUD
            draw_hud(
                self.player,
                self.score,
                wave_number,
                wave_time_left,
                self.heart_textures
            )
        except Exception as e:
            print(f"Error drawing HUD: {e}")
            # Fallback to simple HUD
            self.draw_simple_hud()

def render_game(game_view):
        """Render the entire game view."""
        # Start rendering
        arcade.start_render()
        
        # Draw background if it exists
        if hasattr(game_view, 'background') and game_view.background:
            game_view.background.draw()
        
        # Draw game elements
        game_view.draw_game_elements()
        
        # Draw HUD
        game_view.draw_improved_hud()
        
        # Draw pickup texts
        if hasattr(game_view, 'pickup_texts'):
            for text_obj in game_view.pickup_texts:
                text_obj.draw()
        
        # Draw wave message if active
        if hasattr(game_view, 'wave_message') and hasattr(game_view, 'wave_message_alpha') and game_view.wave_message_alpha > 0:
            draw_wave_message(game_view.wave_message, game_view.wave_message_alpha)
        
        # Draw message if active
        if hasattr(game_view, 'message') and hasattr(game_view, 'message_timer') and game_view.message_timer > 0:
            arcade.draw_text(
                game_view.message,
                game_view.window.width / 2,
                game_view.window.height / 2,
                arcade.color.WHITE,
                font_size=24,
                anchor_x="center",
                anchor_y="center",
                bold=True
            )
        
        # Draw debug info if enabled
        if hasattr(game_view, 'debug_mode') and game_view.debug_mode:
            game_view.draw_debug_info()
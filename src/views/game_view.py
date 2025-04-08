import arcade
from src.game_controller import GameController
from src.entities.player import Player
from src.core.constants import SCREEN_WIDTH, SCREEN_HEIGHT
from src.skins.skin_manager import skin_manager

class NeododgeGame(arcade.View):
    """Main game view."""

    def __init__(self):
        super().__init__()
        self.player = None
        self.enemies = arcade.SpriteList()
        self.orbs = arcade.SpriteList()
        self.coins = arcade.SpriteList()
        self.artifacts = arcade.SpriteList()
        self.game_controller = None
        self.score = 0
        self.pickup_texts = []

        # Mouse tracking
        self.mouse_x = 0
        self.mouse_y = 0
        self.right_mouse_down = False

        # Set up the camera
        self.camera = arcade.Camera(SCREEN_WIDTH, SCREEN_HEIGHT)

        # Set up the GUI camera
        self.gui_camera = arcade.Camera(SCREEN_WIDTH, SCREEN_HEIGHT)

    def setup(self):
        """Set up the game."""
        # Create player
        self.player = Player()
        self.player.center_x = self.window.width // 2
        self.player.center_y = self.window.height // 2
        self.player.window = self.window
        self.player.parent_view = self

        # Initialize game controller
        self.game_controller = GameController(
            self.player, 
            self.window.width, 
            self.window.height
        )
        self.game_controller.initialize(
            self.enemies, 
            self.orbs, 
            self.coins, 
            self.artifacts
        )

        # Reset score
        self.score = 0

    def on_show(self):
        """Called when this view becomes active"""
        arcade.set_background_color(arcade.color.BLACK)

    def on_draw(self):
        """Render the screen."""
        self.clear()

        # Activate the game camera
        self.camera.use()

        # Draw game elements
        self.player.draw()
        self.enemies.draw()
        self.orbs.draw()
        self.coins.draw()
        self.artifacts.draw()

        # Draw enemy bullets
        for enemy in self.enemies:
            if hasattr(enemy, 'bullets'):
                enemy.bullets.draw()

        # Activate the GUI camera for HUD elements
        self.gui_camera.use()

        # Draw HUD elements
        self.draw_hud()

        # Draw wave information
        wave_info = self.game_controller.get_wave_info()
        if wave_info["message_alpha"] > 0:
            arcade.draw_text(
                wave_info["message"],
                self.window.width // 2,
                self.window.height - 100,
                arcade.color.WHITE,
                24,
                anchor_x="center",
                anchor_y="center",
                alpha=wave_info["message_alpha"]
            )

        # Draw wave timer
        arcade.draw_text(
            f"Time: {wave_info['time_remaining']:.1f}",
            self.window.width - 100,
            self.window.height - 30,
            arcade.color.WHITE,
            18
        )

        # Draw wave number
        arcade.draw_text(
            f"Wave: {wave_info['wave_number']}",
            20,
            self.window.height - 30,
            arcade.color.WHITE,
            18
        )

    def on_update(self, delta_time):
        """Update game logic."""
        # Update player
        self.player.update(delta_time)

        # If right mouse is held down, continuously update target
        if self.right_mouse_down and self.player:
            self.player.set_target(self.mouse_x, self.mouse_y)

        # Update enemies
        self.enemies.update()
        for enemy in self.enemies:
            if hasattr(enemy, 'bullets'):
                enemy.bullets.update(delta_time)

        # Update other game elements
        self.orbs.update()
        self.coins.update()
        self.artifacts.update()

        # Update game controller
        self.game_controller.update(delta_time)

        # Check if it's time to show the shop
        if self.game_controller.should_show_shop():
            self.show_shop()

        # Check for collisions
        self.check_collisions()

        # Update score
        self.score += delta_time * 10

    def check_collisions(self):
        """Check for collisions between game elements."""
        # Player-enemy collisions
        for enemy in self.enemies:
            if arcade.check_for_collision(self.player, enemy):
                self.player.take_damage(1)

        # Player-orb collisions
        for orb in self.orbs:
            if arcade.check_for_collision(self.player, orb):
                orb.apply_effect(self.player)
                self.orbs.remove(orb)

        # Player-coin collisions
        for coin in self.coins:
            if arcade.check_for_collision(self.player, coin):
                self.player.collect_coin()
                self.coins.remove(coin)

        # Player-artifact collisions
        for artifact in self.artifacts:
            if arcade.check_for_collision(self.player, artifact):
                self.player.collect_artifact(artifact)
                self.artifacts.remove(artifact)

    def show_shop(self):
        """Show the shop view."""
        from src.views.shop_view import ShopView
        shop_view = ShopView(self.player, self)
        self.window.show_view(shop_view)

    def draw_hud(self):
        """Draw the heads-up display."""
        # Draw player health
        if hasattr(self.player, 'draw_hearts'):
            self.player.draw_hearts()
        else:
            # Fallback if draw_hearts is not available
            health_text = f"Health: {self.player.health}/{self.player.max_health}"
            arcade.draw_text(health_text, 20, arcade.get_window().height - 30, 
                             arcade.color.WHITE, 18)

        # Draw score
        score_text = f"Score: {int(self.score)}"
        arcade.draw_text(score_text, 20, arcade.get_window().height - 60, 
                         arcade.color.WHITE, 18)

        # Draw wave info
        if hasattr(self, 'game_controller'):
            wave_info = self.game_controller.get_wave_info()
            wave_text = f"Wave: {wave_info['wave_number']}"
            arcade.draw_text(wave_text, 20, arcade.get_window().height - 90, 
                             arcade.color.WHITE, 18)

            # Draw wave message if visible
            if wave_info['message_alpha'] > 0:
                arcade.draw_text(
                    wave_info['message'],
                    arcade.get_window().width / 2,
                    arcade.get_window().height / 2,
                    arcade.color.WHITE,
                    24,
                    anchor_x="center",
                    anchor_y="center",
                    alpha=wave_info['message_alpha']
                )

        # Draw player orb status
        if hasattr(self.player, 'draw_orb_status'):
            self.player.draw_orb_status()

        # Draw player artifacts
        if hasattr(self.player, 'draw_artifacts'):
            self.player.draw_artifacts()

        # Draw coin count
        arcade.draw_text(
            f"Coins: {self.player.coins}",
            20,
            arcade.get_window().height - 120,
            arcade.color.GOLD,
            18
        )

    def apply_skin_toggle(self):
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
                print(f"Skin changed to: {next_skin}")

                # Update player texture
                if self.player:
                    self.player.texture = skin_manager.get_texture("player")

                    # Update heart textures
                    self.player.heart_textures = {
                        "red": skin_manager.get_texture("heart_red", "assets/ui/heart_red.png"),
                        "gray": skin_manager.get_texture("heart_gray", "assets/ui/heart_gray.png"),
                        "gold": skin_manager.get_texture("heart_gold", "assets/ui/heart_gold.png")
                    }
            else:
                print(f"⚠️ Failed to switch skin")
        else:
            print(f"⚠️ Current skin '{current_skin}' not found in available skins")

    def on_key_press(self, key, modifiers):
        """Handle key press events"""
        if key == arcade.key.ESCAPE:
            # Pause the game or return to menu
            pass
        elif key == arcade.key.SPACE:
            # Player dash
            if self.player:
                self.player.try_dash()
        elif key == arcade.key.T:
            # Toggle skin
            self.apply_skin_toggle()

    def on_mouse_press(self, x, y, button, modifiers):
        """Handle mouse press events"""
        if button == arcade.MOUSE_BUTTON_RIGHT:
            # Set player target with right click
            if self.player:
                self.player.set_target(x, y)
                self.right_mouse_down = True
                self.mouse_x = x
                self.mouse_y = y

    def on_mouse_release(self, x, y, button, modifiers):
        """Handle mouse release events"""
        if button == arcade.MOUSE_BUTTON_RIGHT:
            self.right_mouse_down = False

    def on_mouse_motion(self, x, y, dx, dy):
        """Handle mouse motion events"""
        self.mouse_x = x
        self.mouse_y = y
import arcade
import random
from src.controllers.game_controller import GameController
from src.entities.player.player import Player
from src.core.constants import (
    SCREEN_WIDTH, 
    SCREEN_HEIGHT, 
    PLAYER_SCALE, 
    ARTIFACT_SCALE,
    WAVE_TEXT_DURATION,
    WAVE_DURATION
)
from src.skins.skin_manager import skin_manager
from src.audio.sound_manager import sound_manager

from src.mechanics.artifacts.dash_artifact import DashArtifact
from src.mechanics.coins.coin import Coin
from src.mechanics.orbs.orb_pool import get_random_orb
from src.views.shop_view import ShopView

from src.mechanics.wave_management.wave_manager import WaveManager
from src.controllers.game_controller import GameController
from src.ui.improved_hud import (
    draw_wave_info,
    draw_score,
    draw_player_health,
    draw_active_effects,
    draw_coin_count,
    draw_wave_message,
    draw_pickup_texts
)

from src.ui.pickup_text import PickupText
from src.views.game.update import update_game
from src.views.game.collision_logic import check_collisions, check_orb_collisions
from src.views.game.bullet_logic import update_enemy_bullets
from src.views.game.mouse_movement import handle_mouse_targeting

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
        self.buff_display_text = []
        self.wave_time_remaining = 10  # seconds for example

        # Mouse tracking
        self.mouse_x = 0
        self.mouse_y = 0
        self.right_mouse_down = False

        # Set up the camera
        self.camera = arcade.Camera(SCREEN_WIDTH, SCREEN_HEIGHT)

        # Set up the GUI camera
        self.gui_camera = arcade.Camera(SCREEN_WIDTH, SCREEN_HEIGHT)
        
        # Import functions from modules
        from src.views.game.spawn_logic import clear_enemies
        from src.views.game.coin_logic import spawn_coin, maybe_spawn_more_coins
        from src.views.game.orb_logic import spawn_orbs
        from src.views.game.spawn_logic import spawn_artifact
        from src.views.game.audio_logic import setup_sounds

        # Bind methods directly without lambdas
        self.clear_enemies = clear_enemies.__get__(self)
        self.spawn_coin = spawn_coin.__get__(self)
        self.maybe_spawn_more_coins = maybe_spawn_more_coins.__get__(self)
        self.spawn_orbs = spawn_orbs.__get__(self)
        self.spawn_artifact = spawn_artifact.__get__(self)
        self.setup_sounds = setup_sounds.__get__(self)

    def on_wave_start(self, wave_config):
        """
        Called when a new wave starts.

        Args:
            wave_config (dict): The configuration for the new wave
        """
        wave_number = wave_config["wave_number"]
        wave_type = wave_config["type"]

        # Show appropriate message based on wave type
        if wave_type == "normal":
            self.show_message(f"Wave {wave_number}")
        elif wave_type == "swarm":
            self.show_message(f"Swarm Wave {wave_number}!")
        elif wave_type == "elite":
            self.show_message(f"Elite Wave {wave_number}!")
        elif wave_type == "boss":
            self.show_message(f"BOSS WAVE {wave_number}!")

        print(f"🌊 Starting {wave_type} wave {wave_number}")

    def on_wave_end(self, wave_number):
        """
        Called when a wave ends.

        Args:
            wave_number (int): The completed wave number
        """
        #self.show_message(f"Wave {wave_number} Complete!")
        self.score += wave_number * 100  # Bonus points for completing a wave
        print(f"🌊 Wave {wave_number} completed! Score: {self.score}")
        
    def start_next_wave(self, delta_time=0):
        """Start the next wave."""
        self.wave_manager.start_wave()

    def reset_damage_sound_cooldown(self, dt):
        """Reset the damage sound cooldown."""
        if hasattr(self.player, 'damage_sound_cooldown'):
            self.player.damage_sound_cooldown = False

    def on_show(self):
        """Called when this view becomes active"""
        arcade.set_background_color(arcade.color.BLACK)

    def on_draw(self):
        """Render the screen."""
        try:
            # Start rendering
            arcade.start_render()
            
            # Draw background
            if hasattr(self, 'background') and self.background:
                self.background.draw()
    
            # Use game camera for game elements
            self.camera.use()
    
            # Draw all sprites
            if hasattr(self, 'player') and self.player:
                self.player.draw()
    
            if hasattr(self, 'enemies'):
                self.enemies.draw()
    
            if hasattr(self, 'orbs'):
                self.orbs.draw()
    
            if hasattr(self, 'coins'):
                self.coins.draw()
    
            if hasattr(self, 'artifacts'):
                self.artifacts.draw()
    
            # Draw enemy bullets
            for enemy in self.enemies:
                if hasattr(enemy, 'bullets'):
                    enemy.bullets.draw()
    
            # Use GUI camera for UI elements
            self.gui_camera.use()
    
            # 💚 Top-left hearts
            from src.ui.improved_hud import draw_player_health
            if hasattr(self, 'player') and self.player:
                draw_player_health(self.player, self.heart_textures)
    
            # 💯 Score
            from src.ui.improved_hud import draw_score
            draw_score(self.score)
    
            # 💥 Top-right active effects
            from src.ui.improved_hud import draw_active_effects
            if hasattr(self, 'player') and self.player and hasattr(self.player, 'status_effects'):
                draw_active_effects(self.player.status_effects)
    
            # 💸 Coins bottom-right
            from src.ui.improved_hud import draw_coin_count
            if hasattr(self, 'player') and self.player:
                draw_coin_count(getattr(self.player, 'coins', 0))
    
            # 🌊 Top-center wave info
            from src.ui.improved_hud import draw_wave_info
            if hasattr(self, 'wave_manager'):
                draw_wave_info(
                    self.wave_manager.current_wave,
                    wave_timer=self.wave_time_remaining if hasattr(self, 'wave_time_remaining') else None,
                    enemies_left=len(self.enemies) if hasattr(self, 'enemies') else None
                )
    
            # Draw any pickup texts
            if hasattr(self, 'pickup_texts'):
                for text_obj in self.pickup_texts:
                    text_obj.draw()
    
            # Draw wave message if active
            if hasattr(self, 'wave_message') and self.wave_message and hasattr(self, 'wave_message_alpha') and self.wave_message_alpha > 0:
                from src.ui.improved_hud import draw_wave_message
                draw_wave_message(self.wave_message, self.wave_message_alpha)
    
            # Draw message if active
            if hasattr(self, 'message') and hasattr(self, 'message_timer') and self.message_timer > 0:
                arcade.draw_text(
                    self.message,
                    self.window.width / 2,
                    self.window.height / 2,
                    arcade.color.WHITE,
                    font_size=24,
                    anchor_x="center",
                    anchor_y="center",
                    bold=True
                )
    
            # Draw debug info if enabled
            if hasattr(self, 'debug_mode') and self.debug_mode:
                self.draw_debug_info()
    
        except Exception as e:
            print("❌ Error in on_draw:", e)
            import traceback
            traceback.print_exc()
    def on_update(self, delta_time: float):
        update_game(delta_time, self)
        
        # Update all enemies in the sprite list
        if hasattr(self, 'enemies') and self.enemies:
            for enemy in self.enemies:
                # Set target if not already set
                if not hasattr(enemy, 'target') or enemy.target is None:
                    if hasattr(self, 'player') and self.player:
                        enemy.target = self.player
                        print(f"[ENEMY] {enemy.__class__.__name__} target set to player")
                
                # Debug logging for enemy updates
                if hasattr(enemy, 'update'):
                    enemy.update(delta_time)
                    if hasattr(enemy, 'target'):
                        #print(f"[ENEMY] {enemy.__class__.__name__} update called. Target: {enemy.target}")
                        pass
        
        check_collisions(self)
        check_orb_collisions(self)
        update_enemy_bullets(self, delta_time)
        
        # Update wave timer if it exists
        if hasattr(self, 'wave_time_remaining') and self.wave_time_remaining > 0:
            self.wave_time_remaining -= delta_time
            
        # Update remaining time if it exists
        if hasattr(self, 'remaining_time') and self.remaining_time > 0:
            self.remaining_time -= delta_time
    
        
    def check_collisions(self):
        """Check for collisions between game objects."""
        # Player-Enemy collisions
        if self.player and not getattr(self.player, 'invincible', False):
            enemy_hit_list = arcade.check_for_collision_with_list(self.player, self.enemies)
            for enemy in enemy_hit_list:
                # Handle player taking damage
                if hasattr(self.player, 'take_damage'):
                    damage = getattr(enemy, 'damage', 1)
                    self.player.take_damage(damage)
                    
                    # Play damage sound
                    self.play_damage_sound()

                # Remove enemy if it's a one-hit enemy
                if hasattr(enemy, 'is_one_hit') and enemy.is_one_hit:
                    enemy.remove_from_sprite_lists()

        # Player-Coin collisions
        coin_hit_list = arcade.check_for_collision_with_list(self.player, self.coins)
        for coin in coin_hit_list:
            # Remove the coin
            coin.remove_from_sprite_lists()

            # Handle coin collection
            if hasattr(self.player, 'collect_coin'):
                self.player.collect_coin()
            else:
                # Fallback if player doesn't have collect_coin method
                if hasattr(self.player, 'coins'):
                    self.player.coins += 1
                else:
                    self.player.coins = 1

                # Add to score
                self.score += 10

            # Play coin sound
            self.play_coin_sound()

            # Add pickup text
            if hasattr(self, 'add_pickup_text'):
                self.add_pickup_text("Coin collected!", self.player.center_x, self.player.center_y)

        # Player-Orb collisions
        for orb in list(self.orbs):  # Use a copy of the list to safely modify during iteration
            distance = ((self.player.center_x - orb.center_x) ** 2 + 
                        (self.player.center_y - orb.center_y) ** 2) ** 0.5
            
            # Check if player is close enough to collect the orb
            # Use a generous collision radius to make collection easier
            collision_radius = getattr(self.player, 'collision_radius', 30) + getattr(orb, 'collision_radius', 15)

            if distance <= collision_radius:
                print(f"Collision detected with {orb.orb_type} orb!")

                # Get orb type and message
                orb_type = getattr(orb, 'orb_type', "unknown")
                message = getattr(orb, 'message', "Orb collected!")

                # Apply the orb effect
                try:
                    self.apply_orb_effect(orb)
                    print(f"Applied orb effect: {orb_type}")

                    # Remove the orb
                    orb.remove_from_sprite_lists()

                    # Play appropriate sound
                    if orb_type in ["speed", "shield", "invincibility"]:
                        self.play_buff_sound()
                    else:
                        self.play_debuff_sound()

                    # Add pickup text
                    if hasattr(self, 'add_pickup_text'):
                        self.add_pickup_text(message, self.player.center_x, self.player.center_y)
                    elif hasattr(self, 'pickup_texts'):
                        self.pickup_texts.append([message, self.player.center_x, self.player.center_y, 1.0])
                except Exception as e:
                    print(f"Error applying orb effect: {e}")

        # Check bullet collisions
        for enemy in self.enemies:
            if hasattr(enemy, 'bullets'):
                # Enemy bullets hit player
                if self.player and not getattr(self.player, 'invincible', False):
                    bullet_hit_list = arcade.check_for_collision_with_list(self.player, enemy.bullets)
                    for bullet in bullet_hit_list:
                        # Remove the bullet
                        bullet.remove_from_sprite_lists()

                        # Damage player
                        damage = getattr(bullet, 'damage', 1)
                        self.player.take_damage(damage)
                        
                        # Play damage sound
                        self.play_damage_sound()
        
    def show_shop(self):
        """Show the shop view."""
        shop_view = ShopView(self.player, self)
        self.window.show_view(shop_view)
        
    def show_message(self, message, duration=2.0):
        """
        Show a message on screen.

        Args:
            message (str): The message to display
            duration (float): How long to display the message in seconds
        """
        self.message = message
        self.message_timer = duration
        print(f"📢 Showing message: {message}")
        
    def get_screen_dimensions(self):
        """Get the dimensions of the game screen."""
        # Use the window dimensions if width/height attributes don't exist
        window = arcade.get_window()
        return window.width, window.height

    def add_pickup_text(self, text, x, y):
        """Add a pickup text that floats upward and fades out."""
        if not hasattr(self, 'pickup_texts'):
            self.pickup_texts = []

        # Add the text with position and lifetime
        self.pickup_texts.append(PickupText(text, x, y))  # 1.0 second lifetime

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
                    self.player.texture = skin_manager.get_texture("player", None)

                    # Update heart textures
                    self.player.heart_textures = {
                        "red": skin_manager.get_texture("ui", "heart_red"),
                        "gray": skin_manager.get_texture("ui", "heart_gray"),
                        "gold": skin_manager.get_texture("ui", "heart_gold")
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
        """Handle mouse press events."""
        # Store mouse position
        self.mouse_x = x
        self.mouse_y = y

        if button == arcade.MOUSE_BUTTON_RIGHT:
            # Convert screen coordinates to world coordinates if using camera
            if hasattr(self, 'camera'):
                # Different versions of Arcade have different methods for coordinate conversion
                # Try the appropriate method based on your Arcade version
                try:
                    # For newer Arcade versions
                    world_pos = self.camera.mouse_coordinates_to_world(x, y)
                    x, y = world_pos
                except AttributeError:
                    # For older Arcade versions or custom Camera implementations
                    # Calculate the conversion manually
                    x = x / self.camera.scale + self.camera.position[0]
                    y = y / self.camera.scale + self.camera.position[1]
                    #print(f"Converted mouse position to world coordinates: ({x}, {y})")

            # Set player target
            if self.player:
                handle_mouse_targeting(self, x, y, held=False)
            self.right_mouse_down = True
            #print(f"🖱️ Right mouse button pressed")
        elif button == arcade.MOUSE_BUTTON_LEFT:
            self.left_mouse_down = True
            
            # Set target position for player
            if self.player:
                handle_mouse_targeting(self, x, y, held=False)
            
            #print("🖱️ Left mouse button pressed")

    def on_mouse_release(self, x, y, button, modifiers):
        """Handle mouse release events."""
        # Update mouse position
        self.mouse_x = x
        self.mouse_y = y

        # Update mouse button state
        if button == arcade.MOUSE_BUTTON_LEFT:
            self.left_mouse_down = False
            #print("🖱️ Left mouse button released")
        elif button == arcade.MOUSE_BUTTON_RIGHT:
            self.right_mouse_down = False
            #print("🖱️ Right mouse button released")

    def on_mouse_motion(self, x, y, dx, dy):
        """Handle mouse motion events."""
        # Update mouse position
        self.mouse_x = x
        self.mouse_y = y

        # If either mouse button is held down, update player target
        if (self.left_mouse_down or self.right_mouse_down) and self.player:
            handle_mouse_targeting(self, x, y, held=True)

    def show_wave_message(self, text):
        self.wave_message = text
        self.wave_message_alpha = 255
        self.message_timer = 0  # reset
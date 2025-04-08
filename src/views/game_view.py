import arcade
import random
from src.controllers.game_controller import GameController
from src.entities.player import Player
from src.core.constants import SCREEN_WIDTH, SCREEN_HEIGHT
from src.skins.skin_manager import skin_manager

from src.mechanics.artifacts.dash import DashArtifact
from src.mechanics.coins.coin import Coin
from src.mechanics.orbs.buff_orbs import BuffOrb
from src.mechanics.orbs.debuff_orbs import DebuffOrb
from src.views.shop_view import ShopView

from src.mechanics.wave_management.wave_manager import WaveManager
from src.controllers.game_controller import GameController

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
        self.player = Player(self.window.width // 2, self.window.height // 2)
        self.player.window = self.window
        self.player.parent_view = self

        # Initialize sprite lists
        self.enemies = arcade.SpriteList()
        self.orbs = arcade.SpriteList()
        self.coins = arcade.SpriteList()
        self.artifacts = arcade.SpriteList()

        # Initialize wave manager
        self.wave_manager = WaveManager(self.player)
        self.wave_manager.wave = 1
        self.wave_manager.spawn_enemies(self.enemies, self.window.width, self.window.height)

        # Initialize dash artifact (but don't spawn it yet)
        self.dash_artifact = None

        # Set up coin spawning (start with a delay)
        self.coins_to_spawn = 5
        self.coin_spawn_timer = 3.0  # First coin spawns after 3 seconds

        # Set up orb spawning
        self.orb_spawn_timer = random.uniform(4, 8)

        # Set up artifact spawning
        self.artifact_spawn_timer = random.uniform(20, 30)

        # Initialize other game state variables
        self.score = 0
        self.level_timer = 0.0
        self.wave_duration = 20.0
        self.in_wave = True
        self.wave_pause = False
        self.wave_message = ""
        self.wave_message_alpha = 0

        # Initialize pickup texts
        self.pickup_texts = []

        # Initialize game controller
        self.game_controller = GameController(self, self.window.width, self.window.height)

        # Load sound effects
        try:
            self.coin_sound = arcade.load_sound("assets/audio/coin.flac")
            self.damage_sound = arcade.load_sound("assets/audio/damage.wav")
            self.buff_sound = arcade.load_sound("assets/audio/buff.wav")
            self.debuff_sound = arcade.load_sound("assets/audio/debuff.wav")
        except Exception as e:
            print(f"Error loading sounds: {e}")
            self.coin_sound = None
            self.damage_sound = None
            self.buff_sound = None
            self.debuff_sound = None

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
                anchor_y="center"
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

        # Draw pickup texts
        if hasattr(self, 'pickup_texts'):
            for text, x, y, _ in self.pickup_texts:
                arcade.draw_text(text, x, y, arcade.color.WHITE, 14, anchor_x="center")

    def add_pickup_text(self, text, x, y):
        """Add floating text for item pickups."""
        if not hasattr(self, 'pickup_texts'):
            self.pickup_texts = []

        # Add text with position and lifetime
        self.pickup_texts.append([text, x, y, 1.0])  # 1.0 second lifetime

    def on_update(self, delta_time):
        """Update game state."""
        # Update player
        self.player.update(delta_time)

        # If right mouse is held down, continuously update target
        if self.right_mouse_down and self.player:
            self.player.set_target(self.mouse_x, self.mouse_y)

        # Update game controller
        if hasattr(self, 'game_controller'):
            self.game_controller.update(delta_time)

        # Check if we should show the shop
        if self.game_controller.should_show_shop():
            # Show shop view
            from src.views.shop_view import ShopView
            shop_view = ShopView()
            shop_view.player = self.player
            shop_view.previous_view = self
            self.window.show_view(shop_view)

            # Reset shop flag to prevent showing it again immediately
            self.game_controller.reset_shop_flag()
            return

        # Update enemies
        for enemy in self.enemies:
            enemy.update(delta_time)

            # Update enemy bullets without passing delta_time
            if hasattr(enemy, 'bullets'):
                enemy.bullets.update()  # Remove delta_time parameter

                # If bullets need delta_time, update each bullet individually
                for bullet in enemy.bullets:
                    if hasattr(bullet, 'update_with_time'):
                        bullet.update_with_time(delta_time)

        # Update orbs
        self.orbs.update()

        # Update coins
        self.coins.update()

        # Update coin animations
        for coin in self.coins:
            if hasattr(coin, 'update_animation'):
                coin.update_animation(delta_time)

        # Handle coin spawning
        if hasattr(self, 'coins_to_spawn') and self.coins_to_spawn > 0:
            if hasattr(self, 'coin_spawn_timer'):
                self.coin_spawn_timer -= delta_time
                if self.coin_spawn_timer <= 0:
                    # Spawn a coin at a random position
                    x = random.randint(50, arcade.get_window().width - 50)
                    y = random.randint(50, arcade.get_window().height - 50)

                    # Create the coin
                    coin = Coin(x, y)
                    self.coins.append(coin)

                    # Update spawn counter and timer
                    self.coins_to_spawn -= 1
                    self.coin_spawn_timer = random.uniform(3, 7)  # Random time until next coin
                    print(f"🪙 Spawned a coin! Remaining: {self.coins_to_spawn}")

        # Handle orb spawning
        if hasattr(self, 'orb_spawn_timer'):
            self.orb_spawn_timer -= delta_time
            if self.orb_spawn_timer <= 0:
                # Spawn an orb at a random position
                x = random.randint(50, arcade.get_window().width - 50)
                y = random.randint(50, arcade.get_window().height - 50)

                # Create a random orb
                orb_type = random.choice(["buff", "debuff"])
                if orb_type == "buff":
                    orb = BuffOrb(x, y)
                else:
                    orb = DebuffOrb(x, y)

                self.orbs.append(orb)

                # Reset timer
                self.orb_spawn_timer = random.uniform(4, 8)
                print(f"🔮 Spawned a {orb_type} orb!")

        # Handle artifact spawning
        if hasattr(self, 'artifact_spawn_timer'):
            self.artifact_spawn_timer -= delta_time
            if self.artifact_spawn_timer <= 0 and not hasattr(self, 'dash_artifact'):
                # Spawn an artifact at a random position
                x = random.randint(50, arcade.get_window().width - 50)
                y = random.randint(50, arcade.get_window().height - 50)

                # Create the artifact
                self.dash_artifact = DashArtifact(x, y)
                self.artifacts.append(self.dash_artifact)

                # Reset timer
                self.artifact_spawn_timer = random.uniform(20, 30)
                print("✨ Spawned a dash artifact!")

        # Update artifacts
        self.artifacts.update()

        # Update pickup texts
        if hasattr(self, 'pickup_texts'):
            for i in range(len(self.pickup_texts) - 1, -1, -1):
                text, x, y, lifetime = self.pickup_texts[i]
                lifetime -= delta_time
                if lifetime <= 0:
                    self.pickup_texts.pop(i)
                else:
                    # Move text upward
                    self.pickup_texts[i] = [text, x, y + 1, lifetime]

        # Check for collisions
        self.check_collisions()

        # Update score
        self.score += delta_time * 10

    def check_collisions(self):
        """Check for collisions between game objects."""
        # Player-Enemy collisions
        enemy_hit_list = arcade.check_for_collision_with_list(self.player, self.enemies)
        for enemy in enemy_hit_list:
            # Handle player taking damage
            if hasattr(self.player, 'take_damage'):
                self.player.take_damage()
                
                # Play damage sound
                if hasattr(self, 'damage_sound') and self.damage_sound:
                    arcade.play_sound(self.damage_sound)

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
                if hasattr(self, 'coin_sound') and self.coin_sound:
                    arcade.play_sound(self.coin_sound)

                # Add pickup text
                if hasattr(self, 'add_pickup_text'):
                    self.add_pickup_text("Coin collected!", self.player.center_x, self.player.center_y)

        # Player-Orb collisions
        orb_hit_list = arcade.check_for_collision_with_list(self.player, self.orbs)
        for orb in orb_hit_list:
            # Store the message before removing the orb
            message = getattr(orb, 'message', "Orb collected!")

            # Determine if it's a buff or debuff orb
            is_buff = isinstance(orb, BuffOrb) if 'BuffOrb' in globals() else 'buff' in str(orb.__class__).lower()

            # Remove the orb
            orb.remove_from_sprite_lists()

            try:
                # Try to apply the effect
                if hasattr(orb, 'apply_effect'):
                    orb.apply_effect(self.player)

                # Play appropriate sound
                if is_buff and hasattr(self, 'buff_sound') and self.buff_sound:
                    arcade.play_sound(self.buff_sound)
                elif not is_buff and hasattr(self, 'debuff_sound') and self.debuff_sound:
                    arcade.play_sound(self.debuff_sound)

                # Add pickup text
                if hasattr(self, 'add_pickup_text'):
                    self.add_pickup_text(message, self.player.center_x, self.player.center_y)
                elif hasattr(self, 'pickup_texts'):
                    self.pickup_texts.append([message, self.player.center_x, self.player.center_y, 1.0])
            except Exception as e:
                print(f"Error applying orb effect: {e}")

        # Player-Artifact collisions
        if hasattr(self, 'dash_artifact') and self.dash_artifact:
            if arcade.check_for_collision(self.player, self.dash_artifact):
                # Store the message before removing the artifact
                message = getattr(self.dash_artifact, 'name', "Artifact collected!")

                try:
                    # Apply the effect
                    self.dash_artifact.apply_effect(self.player)

                    # Remove the artifact
                    self.dash_artifact.remove_from_sprite_lists()
                    self.dash_artifact = None

                    # Play buff sound (artifacts are generally positive)
                    if hasattr(self, 'buff_sound') and self.buff_sound:
                        arcade.play_sound(self.buff_sound)

                    # Add pickup text
                    if hasattr(self, 'add_pickup_text'):
                        self.add_pickup_text(f"{message} unlocked!", self.player.center_x, self.player.center_y)
                    elif hasattr(self, 'pickup_texts'):
                        self.pickup_texts.append([f"{message} unlocked!", self.player.center_x, self.player.center_y, 1.0])
                except Exception as e:
                    print(f"Error applying artifact effect: {e}")

        # Enemy bullet collisions with player
        for enemy in self.enemies:
            if hasattr(enemy, 'bullets'):
                bullet_hit_list = arcade.check_for_collision_with_list(self.player, enemy.bullets)
                for bullet in bullet_hit_list:
                    # Remove the bullet
                    bullet.remove_from_sprite_lists()

                    # Handle player taking damage
                    if hasattr(self.player, 'take_damage'):
                        self.player.take_damage(1)
                        
                        # Play damage sound
                        if hasattr(self, 'damage_sound') and self.damage_sound:
                            arcade.play_sound(self.damage_sound)

    def show_shop(self):
        """Show the shop view."""
        shop_view = ShopView(self.player, self)
        self.window.show_view(shop_view)

    def draw_hud(self):
        """Draw the heads-up display."""
        # Draw player health
        if hasattr(self.player, 'draw_hearts'):
            self.player.draw_hearts()

        # Draw score
        arcade.draw_text(f"Score: {int(self.score)}", 30, arcade.get_window().height - 60, 
                         arcade.color.WHITE, 16)

        # Draw coin count
        if hasattr(self.player, 'coins'):
            arcade.draw_text(f"Coins: {self.player.coins}", arcade.get_window().width - 100, 30, 
                             arcade.color.GOLD, 18)

        # Draw wave info
        if hasattr(self, 'wave_manager'):
            # Draw wave number
            wave_number = self.wave_manager.wave if hasattr(self.wave_manager, 'wave') else 1
            color = arcade.color.GOLD if wave_number % 5 == 0 else arcade.color.LIGHT_GREEN
            arcade.draw_text(
                f"Wave {wave_number}",
                arcade.get_window().width // 2,
                arcade.get_window().height - 35,
                color,
                font_size=18,
                anchor_x="center"
            )

            # Draw wave timer if in a wave
            if hasattr(self, 'in_wave') and self.in_wave and hasattr(self, 'level_timer') and hasattr(self, 'wave_duration'):
                time_left = max(0, int(self.wave_duration - self.level_timer))
                arcade.draw_text(f"⏱ {time_left}s left", arcade.get_window().width // 2, 
                                 arcade.get_window().height - 70, arcade.color.LIGHT_GRAY, 16, 
                                 anchor_x="center")

        # Draw wave message only if not already drawn by wave manager
        if hasattr(self, 'wave_message') and hasattr(self, 'wave_message_alpha') and self.wave_message_alpha > 0:
            # Check if wave manager has already drawn this message
            wave_manager_drew_message = False
            if hasattr(self, 'wave_manager') and hasattr(self.wave_manager, 'last_message_drawn'):
                wave_manager_drew_message = (self.wave_manager.last_message_drawn == self.wave_message)

            # Only draw if not already drawn
            if not wave_manager_drew_message:
                color = arcade.color.LIGHT_GREEN
                arcade.draw_text(
                    self.wave_message,
                    arcade.get_window().width / 2,
                    arcade.get_window().height / 2,
                    color,
                    font_size=24,
                    anchor_x="center"
                )

    def add_pickup_text(self, text, x, y):
        """Add a pickup text that floats upward and fades out."""
        if not hasattr(self, 'pickup_texts'):
            self.pickup_texts = []

        # Add the text with position and lifetime
        self.pickup_texts.append([text, x, y, 1.0])  # 1.0 second lifetime

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
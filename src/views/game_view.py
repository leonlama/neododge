import arcade
import random
import math
from src.core.constants import SCREEN_WIDTH, SCREEN_HEIGHT
from src.skins.skin_manager import skin_manager
from src.entities.player import Player
from src.ui.hud import (
    draw_player_health, draw_score, draw_wave_info, 
    draw_active_effects, draw_coin_count, draw_wave_message
)
from src.mechanics.wave_management.wave_manager import WaveManager
# Placeholder for Enemy class
class Enemy:
    def __init__(self, x, y, player, behavior="basic"):
        self.center_x = x
        self.center_y = y
        self.player = player
        self.behavior = behavior
        print(f"Created placeholder enemy at ({x}, {y}) with {behavior} behavior")
from src.mechanics.coins.coin import Coin
from src.mechanics.orbs.buff_orbs import BuffOrb
from src.mechanics.orbs.debuff_orbs import DebuffOrb
from src.mechanics.orbs.orb_pool import get_random_orb

class NeododgeGame(arcade.View):
    def __init__(self):
        super().__init__()

        # Game state
        self.score = 0
        self.game_over = False
        self.paused = False

        # Wave management
        self.wave = 1
        self.wave_timer = 0
        self.wave_duration = 30
        self.wave_message = None
        self.wave_message_timer = 0
        self.in_wave = False
        self.wave_pause_timer = 0
        self.wave_message_alpha = 0

        # Lists to track game objects
        self.enemies = arcade.SpriteList()
        self.orbs = arcade.SpriteList()
        self.coins_list = arcade.SpriteList()
        self.coins = arcade.SpriteList()  # For compatibility with spawn_wave_entities
        self.dash_artifact = None

        # Active effects for the HUD
        self.active_effects = []

        # Mouse tracking
        self.mouse_x = 0
        self.mouse_y = 0
        self.right_mouse_down = False

        # Set up the camera
        self.camera = arcade.Camera(SCREEN_WIDTH, SCREEN_HEIGHT)

        # Set up the GUI camera
        self.gui_camera = arcade.Camera(SCREEN_WIDTH, SCREEN_HEIGHT)

        # Player will be initialized in setup()
        self.player = None
        
        # Initialize the wave manager (will be properly set up in setup())
        self.wave_manager = None

    def setup(self):
        """Set up the game"""
        # Reset game state
        self.score = 0
        self.game_over = False
        self.paused = False
        self.wave = 1
        self.wave_timer = 0
        self.wave_duration = 30
        self.wave_message = "Wave 1"
        self.wave_message_timer = 3.0
        self.in_wave = False
        self.wave_pause_timer = 3.0

        # Create player
        self.player = Player()
        self.player.center_x = SCREEN_WIDTH / 2
        self.player.center_y = SCREEN_HEIGHT / 2

        # Initialize the wave manager with the player
        self.wave_manager = WaveManager(self.player)

        # Clear game objects
        self.enemies = arcade.SpriteList()
        self.orbs = arcade.SpriteList()
        self.coins_list = arcade.SpriteList()
        self.coins = arcade.SpriteList()
        self.active_effects = []

        # Display welcome message
        self.wave_message = "Get Ready!"
        self.wave_message_timer = 3.0
        self.wave_message_alpha = 255

    def on_show(self):
        """Called when this view becomes active"""
        arcade.set_background_color(arcade.color.BLACK)

    def on_draw(self):
        """Render the screen"""
        # Clear the screen
        self.clear()

        # Activate the game camera
        self.camera.use()

        # Draw the player
        if self.player:
            self.player.draw()

        # Draw all game objects
        self.enemies.draw()
        self.orbs.draw()
        self.coins_list.draw()
        self.coins.draw()  # Draw coins from both lists

        # Activate the GUI camera for HUD elements
        self.gui_camera.use()

        # Draw the HUD components
        if self.player:
            draw_player_health(self.player)
            draw_coin_count(self.player.coins)

        draw_score(self.score)
        draw_wave_info(self.wave, self.wave_timer, self.wave_duration)
        draw_active_effects(self.active_effects)

        # Draw wave message if active
        if self.wave_message and (self.wave_message_timer > 0 or self.wave_message_alpha > 0):
            # Use the wave_message_alpha value directly if available
            alpha = self.wave_message_alpha if self.wave_message_alpha > 0 else min(255, int(self.wave_message_timer * 255))
            draw_wave_message(self.wave_message, alpha)

    def on_update(self, delta_time):
        """Update the game state"""
        if self.game_over or self.paused:
            return

        # Update player
        if self.player:
            self.player.update(delta_time)

        # If right mouse is held down, continuously update target
        if self.right_mouse_down and self.player:
            self.player.set_target(self.mouse_x, self.mouse_y)

        # Update enemies
        self.enemies.update()

        # Update wave manager analytics
        if self.wave_manager:
            self.wave_manager.update_analytics(delta_time)

        if self.in_wave:
            self.wave_timer += delta_time
            if self.wave_timer >= self.wave_duration:
                self.in_wave = False
                self.wave_pause_timer = 3.0
                self.wave_message = f"Successfully survived Wave {self.wave}!"
                self.wave_message_alpha = 255
                print(self.wave_message)

                # Analyze wave performance
                wave_stats = self.wave_manager.end_wave_analysis()
                print(f"Wave stats: {wave_stats}")
        else:
            self.wave_pause_timer -= delta_time
            self.wave_message_alpha = self.fade_wave_message_alpha(self.wave_pause_timer)
            if self.wave_pause_timer <= 0:
                self.start_new_wave()

                # Check if it's time to go to the shop
                if self.wave % 5 == 0:
                    from src.views.shop_view import ShopView
                    shop_view = ShopView(self.player, self)
                    self.window.show_view(shop_view)

        # Update wave message timer
        if self.wave_message_timer > 0:
            self.wave_message_timer -= delta_time

        # Update score
        self.score += delta_time * self.get_score_multiplier()

        # Update active effects and remove expired ones
        self.update_active_effects(delta_time)

    def fade_wave_message_alpha(self, remaining_time):
        """Calculate alpha value for wave message based on remaining time"""
        if remaining_time <= 0:
            return 0
        elif remaining_time >= 2.0:
            return 255
        else:
            return int(255 * (remaining_time / 2.0))

    def start_new_wave(self):
        self.wave += 1

        # Generate wave configuration
        wave_config = self.wave_manager.generate_wave(self.wave)

        # Spawn enemies based on wave configuration
        self.spawn_wave_entities(wave_config)

        # Set wave parameters
        self.wave_duration = 20 + (self.wave - 1) * 5
        self.wave_timer = 0
        self.in_wave = True

        # Display wave message
        self.wave_message = wave_config["message"]
        self.wave_message_alpha = 255

        print(f"🚀 Starting Wave {self.wave} ({wave_config['type']})")

    def spawn_wave_entities(self, wave_config):
        """Spawn all entities for a wave based on the configuration"""
        # Clear existing entities
        self.enemies = arcade.SpriteList()

        # Spawn enemies
        for i, enemy_type in enumerate(wave_config["enemy_types"]):
            # Random position for now
            x = random.randint(50, SCREEN_WIDTH - 50)
            y = random.randint(50, SCREEN_HEIGHT - 50)

            # Create enemy with parameters from wave config
            if enemy_type == "basic":
                enemy = Enemy(x, y, self.player)
            elif enemy_type == "chaser":
                enemy = Enemy(x, y, self.player, behavior="chase")
            elif enemy_type == "shooter":
                enemy = Enemy(x, y, self.player, behavior="shoot")
            elif enemy_type == "boss":
                enemy = Enemy(x, y, self.player, behavior="boss")
                enemy.scale = 2.0

            # Apply enemy parameters if available
            if "enemy_params" in wave_config:
                enemy.speed *= wave_config["enemy_params"].get("speed", 1.0)
                enemy.health *= wave_config["enemy_params"].get("health", 1.0)

            self.enemies.append(enemy)

        # Spawn orbs
        self.orbs = arcade.SpriteList()
        for _ in range(wave_config.get("orb_count", 0)):
            x = random.randint(50, SCREEN_WIDTH - 50)
            y = random.randint(50, SCREEN_HEIGHT - 50)

            # Determine orb type based on distribution
            orb_types = wave_config.get("orb_types", {"buff": 0.8, "debuff": 0.2})
            orb_type = "buff" if random.random() < orb_types.get("buff", 0.8) else "debuff"

            if orb_type == "buff":
                orb = BuffOrb(x, y)
            else:
                orb = DebuffOrb(x, y)

            self.orbs.append(orb)

        # Spawn artifact if needed
        if wave_config.get("spawn_artifact", False):
            artifact = self.wave_manager.maybe_spawn_artifact(
                self.player.artifacts if hasattr(self.player, "artifacts") else [],
                self
            )
            if artifact:
                self.dash_artifact = artifact

        # Spawn coins
        self.coins.clear()
        coin_count = wave_config.get("coin_count", random.randint(1, 5))
        for _ in range(coin_count):
            x = random.randint(50, SCREEN_WIDTH - 50)
            y = random.randint(50, SCREEN_HEIGHT - 50)
            coin = Coin(x, y)
            self.coins.append(coin)

        # Display wave message if available
        if "message" in wave_config:
            self.wave_message = wave_config["message"]
            self.wave_message_alpha = 255

    def get_score_multiplier(self):
        """Calculate the current score multiplier from active effects"""
        multiplier = 1.0

        # Add multipliers from active effects
        for effect in self.active_effects:
            if effect.get("type") == "multiplier":
                multiplier *= effect.get("value", 1.0)

        return multiplier

    def update_active_effects(self, delta_time):
        """Update active effects and remove expired ones"""
        for effect in self.active_effects[:]:  # Create a copy to safely modify during iteration
            effect["duration"] -= delta_time
            if effect["duration"] <= 0:
                self.active_effects.remove(effect)

    def add_effect(self, effect_type, value, duration, color=arcade.color.WHITE, icon=""):
        """Add an effect to the active effects list"""
        self.active_effects.append({
            "type": effect_type,
            "value": value,
            "duration": duration,
            "color": color,
            "icon": icon
        })

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
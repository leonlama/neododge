import arcade
import random
import math
import time
from src.skins.skin_manager import skin_manager
from src.entities.player import Player
# Import individual functions instead of draw_hud
from src.ui.hud import (
    draw_player_health, draw_score, draw_wave_info, 
    draw_active_effects, draw_coin_count, draw_wave_message
)

class NeododgeGame(arcade.View):
    def __init__(self):
        super().__init__()

        # Set up the game window
        self.width = 800
        self.height = 600

        # Game state
        self.score = 0
        self.game_over = False
        self.paused = False
        self.coins = 0

        # Wave management
        self.current_wave = 1
        self.wave_timer = 0
        self.wave_duration = 30
        self.wave_message = None
        self.wave_message_timer = 0

        # Player setup
        self.player = Player()
        self.player.center_x = self.width / 2
        self.player.center_y = self.height / 2

        # Lists to track game objects
        self.enemies = []
        self.orbs = []
        self.coins_list = []

        # Active effects for the HUD
        self.active_effects = []

        # Mouse tracking
        self.mouse_x = 0
        self.mouse_y = 0

        # Set up the camera
        self.camera = arcade.Camera(self.width, self.height)

        # Set up the GUI camera
        self.gui_camera = arcade.Camera(self.width, self.height)

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
        self.player.draw()

        # Draw all game objects
        for enemy in self.enemies:
            enemy.draw()

        for orb in self.orbs:
            orb.draw()

        for coin in self.coins_list:
            coin.draw()

        # Activate the GUI camera for HUD elements
        self.gui_camera.use()

        # Draw the HUD components individually
        draw_player_health(self.player)
        draw_score(self.score)
        draw_wave_info(self.current_wave, self.wave_timer, self.wave_duration)
        draw_active_effects(self.active_effects)
        draw_coin_count(self.coins)

        # Draw wave message if active
        if self.wave_message and self.wave_message_timer > 0:
            # Calculate alpha based on remaining time (fade out)
            alpha = min(255, int(self.wave_message_timer * 255))
            draw_wave_message(self.wave_message, alpha)

    def on_update(self, delta_time):
        """Update the game state"""
        if self.game_over or self.paused:
            return

        # Update player
        self.player.update(delta_time)

        # Update enemies
        for enemy in self.enemies:
            enemy.update(delta_time)

        # Update wave timer
        self.wave_timer += delta_time
        if self.wave_timer >= self.wave_duration:
            self.start_new_wave()

        # Update wave message timer
        if self.wave_message_timer > 0:
            self.wave_message_timer -= delta_time

        # Update score
        self.score += delta_time * self.get_score_multiplier()

        # Update active effects and remove expired ones
        self.update_active_effects(delta_time)

    def start_new_wave(self):
        """Start a new wave"""
        self.current_wave += 1
        self.wave_timer = 0

        # Display wave message
        self.wave_message = f"Wave {self.current_wave}"
        self.wave_message_timer = 3.0  # Show for 3 seconds

        # Spawn enemies for the new wave
        self.spawn_wave_enemies()

    def spawn_wave_enemies(self):
        """Spawn enemies for the current wave"""
        # Simple example - spawn more enemies for higher waves
        num_enemies = min(5, 1 + self.current_wave // 2)

        for _ in range(num_enemies):
            # This is just a placeholder - you'd have actual enemy spawning logic
            print(f"Would spawn enemy (wave {self.current_wave})")

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

        # WASD movement
        elif key == arcade.key.W:
            self.player.change_y = self.player.speed
            self.player.target_x = None  # Clear target when using keyboard
            self.player.target_y = None
        elif key == arcade.key.S:
            self.player.change_y = -self.player.speed
            self.player.target_x = None
            self.player.target_y = None
        elif key == arcade.key.A:
            self.player.change_x = -self.player.speed
            self.player.target_x = None
            self.player.target_y = None
        elif key == arcade.key.D:
            self.player.change_x = self.player.speed
            self.player.target_x = None
            self.player.target_y = None

    def on_key_release(self, key, modifiers):
        """Handle key release events"""
        # WASD movement
        if key == arcade.key.W and self.player.change_y > 0:
            self.player.change_y = 0
        elif key == arcade.key.S and self.player.change_y < 0:
            self.player.change_y = 0
        elif key == arcade.key.A and self.player.change_x < 0:
            self.player.change_x = 0
        elif key == arcade.key.D and self.player.change_x > 0:
            self.player.change_x = 0

    def on_mouse_press(self, x, y, button, modifiers):
        """Handle mouse press events"""
        #
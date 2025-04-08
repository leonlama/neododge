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

class NeododgeGame(arcade.View):
    def __init__(self):
        super().__init__()

        # Game state
        self.score = 0
        self.game_over = False
        self.paused = False

        # Wave management
        self.current_wave = 1
        self.wave_timer = 0
        self.wave_duration = 30
        self.wave_message = None
        self.wave_message_timer = 0

        # Lists to track game objects
        self.enemies = arcade.SpriteList()
        self.orbs = arcade.SpriteList()
        self.coins_list = arcade.SpriteList()

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

    def setup(self):
        """Set up the game"""
        # Reset game state
        self.score = 0
        self.game_over = False
        self.paused = False
        self.current_wave = 1
        self.wave_timer = 0
        self.wave_duration = 30
        self.wave_message = "Wave 1"
        self.wave_message_timer = 3.0

        # Create player
        self.player = Player()
        self.player.center_x = SCREEN_WIDTH / 2
        self.player.center_y = SCREEN_HEIGHT / 2

        # Clear game objects
        self.enemies = arcade.SpriteList()
        self.orbs = arcade.SpriteList()
        self.coins_list = arcade.SpriteList()
        self.active_effects = []

        # Display welcome message
        self.wave_message = "Get Ready!"
        self.wave_message_timer = 3.0

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

        # Activate the GUI camera for HUD elements
        self.gui_camera.use()

        # Draw the HUD components
        if self.player:
            draw_player_health(self.player)
            draw_coin_count(self.player.coins)

        draw_score(self.score)
        draw_wave_info(self.current_wave, self.wave_timer, self.wave_duration)
        draw_active_effects(self.active_effects)

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
        if self.player:
            self.player.update(delta_time)

        # If right mouse is held down, continuously update target
        if self.right_mouse_down and self.player:
            self.player.set_target(self.mouse_x, self.mouse_y)

        # Update enemies
        self.enemies.update()

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
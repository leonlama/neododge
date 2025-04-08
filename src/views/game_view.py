import arcade
import random
import math
from arcade.gui import UIManager

from src.core.constants import (
    SCREEN_WIDTH, SCREEN_HEIGHT, PLAYER_SPEED, 
    PLAYER_DASH_DISTANCE, PLAYER_DASH_COOLDOWN
)
from src.entities.player import Player
from src.skins.skin_manager import skin_manager
from src.ui.hud import (
    draw_score, draw_pickup_texts, draw_wave_timer, 
    draw_wave_number, draw_coin_count, draw_player_health,
    draw_active_orbs, draw_wave_message
)

class WaveManager:
    """Manages game waves and difficulty progression"""

    def __init__(self, game_view):
        self.game_view = game_view
        self.wave = 1
        self.level_timer = 0
        self.wave_duration = 30  # seconds per wave
        self.wave_message = "Wave 1"
        self.wave_message_animation = {"phase": "fade_in", "alpha": 0, "letter_positions": [], "letter_alphas": []}

    def update(self, delta_time):
        """Update wave state"""
        self.level_timer += delta_time

        # Check if wave is complete
        if self.level_timer >= self.wave_duration:
            self.next_wave()

    def next_wave(self):
        """Advance to the next wave"""
        self.wave += 1
        self.level_timer = 0
        self.wave_message = f"Wave {self.wave}"
        self.wave_message_animation = {"phase": "fade_in", "alpha": 255, "letter_positions": [], "letter_alphas": []}

        # Increase difficulty
        self.wave_duration = min(60, 30 + self.wave * 2)  # Longer waves as game progresses

class EnemySpawner:
    """Manages enemy spawning based on wave difficulty"""

    def __init__(self, game_view):
        self.game_view = game_view
        self.spawn_timer = 0
        self.spawn_interval = 2.0  # seconds between spawns

    def update(self, delta_time):
        """Update enemy spawning"""
        self.spawn_timer += delta_time

        # Spawn enemies at regular intervals
        if self.spawn_timer >= self.spawn_interval:
            self.spawn_timer = 0
            self.spawn_enemy()

    def spawn_enemy(self):
        """Spawn a new enemy"""
        # Debug message for now
        print(f"Would spawn enemy (wave {self.game_view.wave_manager.wave})")

class OrbSpawner:
    """Manages orb spawning"""

    def __init__(self, game_view):
        self.game_view = game_view
        self.spawn_timer = 0
        self.spawn_interval = 5.0  # seconds between spawns

    def update(self, delta_time):
        """Update orb spawning"""
        self.spawn_timer += delta_time

        # Spawn orbs at regular intervals
        if self.spawn_timer >= self.spawn_interval:
            self.spawn_timer = 0
            self.spawn_orb()

    def spawn_orb(self):
        """Spawn a new orb"""
        # Debug message for now
        orb_types = ["speed", "shield", "cooldown", "multiplier"]
        orb_type = random.choice(orb_types)
        x = random.randint(50, SCREEN_WIDTH - 50)
        y = random.randint(50, SCREEN_HEIGHT - 50)
        print(f"Would spawn buff orb: {orb_type} at ({x}, {y})")

class NeododgeGame(arcade.View):
    """Main game view for Neododge"""

    def __init__(self):
        super().__init__()

        # Set up the game window
        self.window.set_mouse_visible(True)

        # Initialize game state
        self.score = 0
        self.pickup_texts = []
        self.enemies = arcade.SpriteList()
        self.bullets = arcade.SpriteList()
        self.orbs = arcade.SpriteList()
        self.artifacts = arcade.SpriteList()

        # Create player
        self.player = Player()
        self.player.center_x = SCREEN_WIDTH // 2
        self.player.center_y = SCREEN_HEIGHT // 2

        # Create managers
        self.wave_manager = WaveManager(self)
        self.enemy_spawner = EnemySpawner(self)
        self.orb_spawner = OrbSpawner(self)

        # Set up UI
        self.ui_manager = UIManager()
        self.ui_manager.enable()

        # Set up background
        self.background_color = arcade.color.BLACK

        # Debug mode
        self.debug_mode = False

    def on_show_view(self):
        """Called when switching to this view"""
        arcade.set_background_color(self.background_color)

    def on_update(self, delta_time):
        """Update game state"""
        # Update player
        self.player.update(delta_time)

        # Update managers
        self.wave_manager.update(delta_time)
        self.enemy_spawner.update(delta_time)
        self.orb_spawner.update(delta_time)

        # Update game objects
        self.enemies.update()
        self.bullets.update()
        self.orbs.update()

        # Check for collisions
        self._check_collisions()

        # Update pickup texts
        self._update_pickup_texts(delta_time)

        # Update score
        self.score += delta_time * 10 * self.player.multiplier

    def on_draw(self):
        """Render the game"""
        arcade.start_render()

        # Draw game objects
        self.orbs.draw()
        self.enemies.draw()
        self.bullets.draw()
        self.player.draw()

        # Draw HUD
        self.draw_hud()

        # Draw debug info
        if self.debug_mode:
            self._draw_debug_info()

    def draw_hud(self):
        """Draw the heads-up display"""
        # Draw score
        draw_score(self.score)

        # Draw wave info
        draw_wave_timer(self.wave_manager.level_timer, self.wave_manager.wave_duration)
        draw_wave_number(self.wave_manager.wave)

        # Draw player info
        draw_player_health(self.player)
        draw_active_orbs(self.player)
        draw_coin_count(self.player.coins)

        # Draw pickup texts
        draw_pickup_texts(self.pickup_texts)

        # Draw wave message if active
        draw_wave_message(self.wave_manager.wave_message, self.wave_manager.wave_message_animation)

    def on_key_press(self, key, modifiers):
        """Handle key press events"""
        if key == arcade.key.ESCAPE:
            # Pause game
            pass
        elif key == arcade.key.F3:
            # Toggle debug mode
            self.debug_mode = not self.debug_mode
        elif key == arcade.key.W or key == arcade.key.UP:
            self.player.change_y = PLAYER_SPEED
        elif key == arcade.key.S or key == arcade.key.DOWN:
            self.player.change_y = -PLAYER_SPEED
        elif key == arcade.key.A or key == arcade.key.LEFT:
            self.player.change_x = -PLAYER_SPEED
        elif key == arcade.key.D or key == arcade.key.RIGHT:
            self.player.change_x = PLAYER_SPEED
        elif key == arcade.key.SPACE:
            # Dash
            if self.player.dash_cooldown <= 0:
                self._perform_dash()
        elif key == arcade.key.T:
            # Toggle skin
            self.apply_skin_toggle()
        elif key == arcade.key.Q:
            # Use artifact 1
            if len(self.player.artifacts) > 0:
                self.player.artifacts[0].apply_effect(self.player)
        elif key == arcade.key.E:
            # Use artifact 2
            if len(self.player.artifacts) > 1:
                self.player.artifacts[1].apply_effect(self.player)

    def on_key_release(self, key, modifiers):
        """Handle key release events"""
        if key == arcade.key.W or key == arcade.key.UP:
            self.player.change_y = 0
        elif key == arcade.key.S or key == arcade.key.DOWN:
            self.player.change_y = 0
        elif key == arcade.key.A or key == arcade.key.LEFT:
            self.player.change_x = 0
        elif key == arcade.key.D or key == arcade.key.RIGHT:
            self.player.change_x = 0

    def on_mouse_motion(self, x, y, dx, dy):
        """Handle mouse motion events"""
        # Update player target for dash
        self.player.target_x = x
        self.player.target_y = y

    def on_mouse_press(self, x, y, button, modifiers):
        """Handle mouse press events"""
        if button == arcade.MOUSE_BUTTON_LEFT:
            # Dash
            if self.player.dash_cooldown <= 0:
                self._perform_dash()

    def apply_skin_toggle(self):
        """Toggle between available skins"""
        # Get available skins and toggle to next one
        available_skins = list(skin_manager.skin_data.keys())
        current_skin = skin_manager.current_skin

        # Find next skin in rotation
        current_index = available_skins.index(current_skin)
        next_index = (current_index + 1) % len(available_skins)
        next_skin = available_skins[next_index]

        # Apply the new skin
        if skin_manager.set_skin(next_skin):
            print(f"🎨 Switched to {next_skin} skin")

            # Update player texture
            self.player.texture = skin_manager.get_texture("player")
            self.player.scale = skin_manager.get_player_scale()

            # Update heart textures
            self.player.heart_textures = {
                "red": skin_manager.get_texture("heart", "assets/ui/heart_red.png"),
                "gray": skin_manager.get_texture("heart_gray", "assets/ui/heart_gray.png"),
                "gold": skin_manager.get_texture("heart_gold", "assets/ui/heart_gold.png")
            }
        else:
            print("⚠️ Skin not found or not unlocked")

    def _perform_dash(self):
        """Perform player dash"""
        self.player.perform_dash()

    def _check_collisions(self):
        """Check for collisions between game objects"""
        # TODO: Implement collision detection
        pass

    def _update_pickup_texts(self, delta_time):
        """Update floating pickup text animations"""
        for i, (text, x, y, timer) in enumerate(self.pickup_texts):
            self.pickup_texts[i] = (text, x, y + 1, timer - delta_time)

        # Remove expired pickup texts
        self.pickup_texts = [pt for pt in self.pickup_texts if pt[3] > 0]

    def _draw_debug_info(self):
        """Draw debug information"""
        debug_info = [
            f"FPS: {arcade.get_fps(60):.1f}",
            f"Player Pos: ({self.player.center_x:.1f}, {self.player.center_y:.1f})",
            f"Wave: {self.wave_manager.wave}",
            f"Enemies: {len(self.enemies)}",
            f"Orbs: {len(self.orbs)}",
            f"Bullets: {len(self.bullets)}",
        ]

        for i, text in enumerate(debug_info):
            arcade.draw_text(
                text,
                10,
                SCREEN_HEIGHT - 120 - i * 20,
                arcade.color.WHITE,
                12
            )
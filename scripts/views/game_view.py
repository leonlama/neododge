# scripts/views/game_view.py
import arcade
import random
import math
from scripts.characters.player import Player
from scripts.characters.enemy import Enemy
from scripts.mechanics.wave_manager import WaveManager
from scripts.utils.constants import SCREEN_WIDTH, SCREEN_HEIGHT
from scripts.utils.hud import (
    draw_pickup_texts,
    draw_wave_message,
    draw_wave_timer,
    draw_score,
    draw_wave_number,
    draw_coin_count,
)

class NeododgeGame(arcade.View):
    """
    Main game view for NeoDodge.

    Responsibilities:
    - Handle game logic and rendering
    - Manage player, enemies, orbs, and other game elements
    - Handle user input for gameplay
    """

    def __init__(self):
        super().__init__()
        # Game objects
        self.player = None
        self.enemies = arcade.SpriteList()
        self.orbs = arcade.SpriteList()
        self.coins = arcade.SpriteList()
        self.artifacts = arcade.SpriteList()
        self.current_artifact = None
        self.bullets = arcade.SpriteList()

        # Game state
        self.score = 0
        self.wave_manager = None
        self.level_timer = 0
        self.wave_duration = 30  # seconds
        self.wave_message = ""
        self.wave_message_alpha = 0
        self.pickup_texts = []

        # Game over state
        self.game_over = False
        self.game_over_timer = 0

    def setup(self):
        """Set up the game elements."""
        try:
            print("Setting up game...")

            # Set up player
            self.player = Player()
            self.player.center_x = self.window.width / 2
            self.player.center_y = self.window.height / 2

            # Set up wave manager
            self.wave_manager = WaveManager(self.player)

            # Start first wave
            self._start_wave()

            # Play game start sound
            try:
                start_sound = arcade.load_sound("assets/audio/game_start.wav")
                arcade.play_sound(start_sound)
            except Exception as e:
                print(f"Warning: Could not play game start sound: {e}")

            print("Game setup complete")
        except Exception as e:
            print(f"❌ Error setting up game: {e}")
            import traceback
            traceback.print_exc()

    def on_show(self):
        """Called when this view becomes active."""
        arcade.set_background_color(arcade.color.BLACK)

    def on_draw(self):
        """Render the screen."""
        arcade.start_render()

        # Draw game elements
        self.coins.draw()
        self.orbs.draw()
        self.artifacts.draw()

        # Draw enemies and their bullets
        for enemy in self.enemies:
            enemy.bullets.draw()
        self.enemies.draw()

        # Draw player
        if self.player:
            self.player.draw()
            if hasattr(self.player, 'draw_orb_status'):
                self.player.draw_orb_status(self.window.width, self.window.height)
            if hasattr(self.player, 'draw_artifacts'):
                self.player.draw_artifacts()

        # Draw HUD
        self._draw_hud()

        # Draw wave message
        if self.wave_message and self.wave_message_alpha > 0:
            draw_wave_message(self.wave_message, self.wave_message_alpha)

        # Draw game over screen
        if self.game_over:
            self._draw_game_over()

    def on_update(self, delta_time):
        """Update game logic."""
        if self.game_over:
            self.game_over_timer += delta_time
            if self.game_over_timer > 3:
                # Return to start screen
                from scripts.views.start_view import StartView
                start_view = StartView()
                self.window.show_view(start_view)
            return

        # Update level timer
        self.level_timer += delta_time

        # Check if wave is complete
        if self.level_timer >= self.wave_duration:
            self._next_wave()

        # Update player
        if self.player:
            self.player.update()

        # Update enemies and their bullets
        for enemy in self.enemies:
            enemy.update(delta_time)

        # Update orbs
        self.orbs.update()

        # Update coins
        self.coins.update()

        # Update artifacts
        self.artifacts.update()

        # Update pickup texts
        self._update_pickup_texts(delta_time)

        # Update wave message alpha
        if self.wave_message_alpha > 0:
            self.wave_message_alpha -= delta_time * 255 / 2  # Fade over 2 seconds

        # Check collisions
        self._check_collisions()

    def on_mouse_motion(self, x, y, dx, dy):
        """Handle mouse motion."""
        if self.player and not self.game_over:
            self.player.center_x = x
            self.player.center_y = y

    def on_key_press(self, symbol, modifiers):
        """Handle key press events."""
        if symbol == arcade.key.T:
            self.apply_skin_toggle()
        elif symbol == arcade.key.ESCAPE:
            # Return to start screen
            from scripts.views.start_view import StartView
            start_view = StartView()
            self.window.show_view(start_view)

    def apply_skin_toggle(self):
        """Toggle between available skin sets and update all game elements."""
        try:
            # Toggle the skin
            self.window.skin_manager.toggle_skin()

            # Update all visual elements
            self._update_visual_elements()
        except Exception as e:
            print(f"❌ Error toggling skin: {e}")

    def _update_visual_elements(self):
        """Update all visual elements after a skin change."""
        # Update player
        if self.player and hasattr(self.player, 'update_texture'):
            self.player.update_texture()

        # Update enemies
        for enemy in self.enemies:
            if hasattr(enemy, 'update_texture'):
                enemy.update_texture()

        # Update orbs
        for orb in self.orbs:
            if hasattr(orb, 'update_texture'):
                orb.update_texture()

        # Update coins
        for coin in self.coins:
            if hasattr(coin, 'update_texture'):
                coin.update_texture()

        # Update artifacts
        for artifact in self.artifacts:
            if hasattr(artifact, 'update_texture'):
                artifact.update_texture()

    def _draw_hud(self):
        """Draw the HUD."""
        # Draw score
        draw_score(self.score)

        # Draw wave number
        draw_wave_number(self.wave_manager.wave)

        # Draw wave timer
        draw_wave_timer(self.level_timer, self.wave_duration)

        # Draw coin count
        if hasattr(self.player, 'coins'):
            draw_coin_count(self.player.coins)

        # Draw pickup texts
        draw_pickup_texts(self.pickup_texts)

    def _draw_game_over(self):
        """Draw the game over screen."""
        # Semi-transparent overlay
        arcade.draw_rectangle_filled(
            self.window.width / 2,
            self.window.height / 2,
            self.window.width,
            self.window.height,
            (0, 0, 0, 200)
        )

        # Game over text
        arcade.draw_text(
            "GAME OVER",
            self.window.width / 2,
            self.window.height / 2 + 50,
            arcade.color.WHITE,
            font_size=50,
            anchor_x="center"
        )

        # Final score
        arcade.draw_text(
            f"Final Score: {int(self.score)}",
            self.window.width / 2,
            self.window.height / 2 - 20,
            arcade.color.WHITE,
            font_size=30,
            anchor_x="center"
        )

    def _start_wave(self):
        """Start a new wave."""
        # Reset level timer
        self.level_timer = 0

        # Spawn enemies
        extras = self.wave_manager.spawn_enemies(
            self.enemies,
            self.window.width,
            self.window.height
        )

        # Add coins to the game
        self.coins.extend(extras.get("coins", []))

        # Spawn orbs
        orb_count = extras.get("orbs", 0)
        self.wave_manager.spawn_orbs(
            self.orbs,
            orb_count,
            self.window.width,
            self.window.height
        )

        # Maybe spawn artifact
        if extras.get("artifact", False):
            artifact = self.wave_manager.maybe_spawn_artifact(
                [a.name for a in self.player.artifacts],
                self.current_artifact,
                self.window.width,
                self.window.height
            )
            if artifact:
                self.artifacts.append(artifact)
                self.current_artifact = artifact

        # Set wave message
        self.wave_message = f"Wave {self.wave_manager.wave}"
        self.wave_message_alpha = 255

    def _next_wave(self):
        """Advance to the next wave."""
        self.wave_manager.next_wave()
        self._start_wave()

    def _check_collisions(self):
        """Check for collisions between game objects."""
        # Player-enemy collision
        enemy_hit = arcade.check_for_collision_with_list(self.player, self.enemies)
        if enemy_hit:
            # Player takes damage
            if hasattr(self.player, 'take_damage'):
                alive = self.player.take_damage()
                if not alive:
                    self.game_over = True

            # Remove the enemy
            for enemy in enemy_hit:
                enemy.remove_from_sprite_lists()

        # Player-orb collision
        orb_hit = arcade.check_for_collision_with_list(self.player, self.orbs)
        for orb in orb_hit:
            # Apply orb effect
            if hasattr(orb, 'apply_effect'):
                orb.apply_effect(self.player)

                # Add pickup text
                self.pickup_texts.append([
                    orb.name,
                    orb.center_x,
                    orb.center_y,
                    1.0  # Duration
                ])

            # Remove the orb
            orb.remove_from_sprite_lists()

        # Player-coin collision
        coin_hit = arcade.check_for_collision_with_list(self.player, self.coins)
        for coin in coin_hit:
            # Add coin to player
            if hasattr(self.player, 'add_coin'):
                self.player.add_coin()
                self.score += 10

            # Remove the coin
            coin.remove_from_sprite_lists()

        # Player-artifact collision
        artifact_hit = arcade.check_for_collision_with_list(self.player, self.artifacts)
        for artifact in artifact_hit:
            # Add artifact to player
            if hasattr(self.player, 'artifacts'):
                self.player.artifacts.append(artifact)

                # Add pickup text
                self.pickup_texts.append([
                    f"Artifact: {artifact.name}",
                    artifact.center_x,
                    artifact.center_y,
                    1.5  # Duration
                ])

            # Remove the artifact
            artifact.remove_from_sprite_lists()
            self.current_artifact = None

        # Check for bullet collisions
        for enemy in self.enemies:
            for bullet in enemy.bullets:
                if arcade.check_for_collision(bullet, self.player):
                    # Player takes damage
                    if hasattr(self.player, 'take_damage'):
                        alive = self.player.take_damage()
                        if not alive:
                            self.game_over = True

                    # Remove the bullet
                    bullet.remove_from_sprite_lists()

    def _update_pickup_texts(self, delta_time):
        """Update pickup text animations."""
        for i in range(len(self.pickup_texts) - 1, -1, -1):
            self.pickup_texts[i][3] -= delta_time
            if self.pickup_texts[i][3] <= 0:
                self.pickup_texts.pop(i)
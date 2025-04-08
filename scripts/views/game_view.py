import arcade
import random
import math
from src.entities.player import Player
from scripts.mechanics.artifacts.dash_artifact import DashArtifact
from scripts.mechanics.orbs.buff_orbs import BuffOrb
from scripts.mechanics.orbs.debuff_orbs import DebuffOrb
from scripts.mechanics.coins.coin_factory import create_coin, Coin
from scripts.managers.wave_manager import WaveManager
from src.core.constants import SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE, ARTIFACT_SCALE
from scripts.utils.shaders import load_vision_shader, create_vision_geometry
from scripts.utils.spawner import spawn_random_orb, spawn_dash_artifact
from scripts.utils.pickup_text import update_pickup_texts
from scripts.utils.hud import (
    draw_pickup_texts,
    draw_wave_message,
    draw_wave_timer,
    draw_score,
    draw_wave_number,
    draw_coin_count,
)
from scripts.utils.wave_text import fade_wave_message_alpha
from src.core.resource_manager import resource_path
from scripts.utils.orb_utils import get_texture_name_from_orb_type
from scripts.skins.skin_manager import skin_manager
from scripts.mechanics.game_state import game_state
from scripts.enemies.base_enemy import BaseEnemy
from scripts.enemies.chaser_enemy import ChaserEnemy
from scripts.enemies.enemy_manager import EnemyManager
from scripts.utils.ui.cooldown_bar import CooldownBar
from src.core.constants import DASH_COOLDOWN

class NeododgeGame(arcade.View):
    def __init__(self):
        super().__init__()
        self.player = None
        self.enemies = arcade.SpriteList()
        self.orbs = arcade.SpriteList()
        self.coins = arcade.SpriteList()
        self.dash_artifact = None
        self.pickup_texts = []
        self.wave_duration = 20.0
        self.level_timer = 0.0
        self.orb_spawn_timer = random.uniform(4, 8)
        self.artifact_spawn_timer = random.uniform(20, 30)
        self.score = 0
        self.wave_manager = None
        self.enemy_manager = None
        self.in_wave = True
        self.wave_pause_timer = 0.0
        self.wave_message_alpha = 255
        self.wave_message = ""
        self.wave_pause = False
        self.clones = []
        self.vision_shader = None
        self.vision_geometry = None
        self.coins_to_spawn = 0
        self.coin_spawn_timer = 0.0
        self.coin_sound = arcade.load_sound(resource_path("assets/audio/coin.flac"))
        self.right_mouse_down = False
        self.mouse_x = 0
        self.mouse_y = 0
        self.dash_bar = None  # Start with no bar

    def on_show(self):
        arcade.set_background_color(arcade.color.BLACK)
        self.vision_shader = load_vision_shader(self.window)
        self.vision_geometry = create_vision_geometry(self.window)

    def setup(self):
        """Set up the game and initialize variables."""
        # Create player with position
        self.player = Player(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        self.player.window = self.window
        self.player.parent_view = self

        # Initialize managers
        self.enemy_manager = EnemyManager(self)
        self.wave_manager = WaveManager(self)

        # Start first wave
        self.enemy_manager.spawn_enemies(self.enemies, self.wave_manager.wave, self.window.width, self.window.height)

        # Set up other game elements
        self.dash_artifact = spawn_dash_artifact(SCREEN_WIDTH, SCREEN_HEIGHT)
        self.orbs = arcade.SpriteList()

    def on_draw(self):
        self.clear()

        # --- World Layer ---
        self.player.draw()
        self.orbs.draw()
        self.coins.draw()
        self.enemies.draw()
        for enemy in self.enemies:
            enemy.bullets.draw()
        if self.dash_artifact:
            self.dash_artifact.draw()

        # Draw vision blur if active
        if self.player.vision_blur:
            self.vision_shader["resolution"] = self.window.get_size()
            self.vision_shader["center"] = (self.player.center_x, self.player.center_y)
            self.vision_shader["radius"] = 130.0
            self.vision_geometry.render(self.vision_shader)

        # --- HUD Layer ---
        self.player.draw_hearts()
        self.player.draw_orb_status()
        self.player.draw_artifacts()  # Ensure this line is active
        arcade.draw_text(f"Score: {int(self.score)}", 30, SCREEN_HEIGHT - 60, arcade.color.WHITE, 16)
        draw_pickup_texts(self.pickup_texts)
        draw_coin_count(game_state.coins)

        # Wave timer and message
        if not self.wave_pause:
            draw_wave_timer(self.level_timer, self.wave_duration)
        if not self.in_wave and self.wave_message:
            draw_wave_message(self.wave_message, self.wave_message_alpha)

        # Draw wave number
        draw_wave_number(self.wave_manager.wave)

        # Draw Dash Cooldown Bar
        if self.dash_bar:
            self.dash_bar.draw()

    def on_update(self, delta_time):
        """Update the game state."""
        # Update wave manager
        self.wave_manager.update(delta_time)

        # Update timers
        self._update_timers(delta_time)

        # Update entities
        self._update_entities(delta_time)

        # Handle collisions - pass delta_time
        self._handle_collisions(delta_time)

        # Check game state
        self._check_game_state()

        # Update cooldown bar from player's dash timer
        if self.dash_bar and self.player and self.player.has_dash_artifact:
            # First, make sure the cooldown value matches the player's cooldown
            effective_cooldown = self.player.cooldown * self.player.cooldown_factor
            if self.dash_bar.cooldown != effective_cooldown:
                self.dash_bar.cooldown = effective_cooldown

            # Now set the timer directly - this is what makes the bar fill up
            self.dash_bar.timer = self.player.dash_timer
            
    def _update_timers(self, delta_time):
        """Update game timers."""
        # Wave timer
        if self.in_wave:
            self.level_timer += delta_time
            if self.level_timer >= self.wave_duration:
                self.in_wave = False
                self.wave_pause_timer = 3.0
                self.wave_message = f"Successfully survived Wave {self.wave_manager.wave}!"
                self.wave_message_alpha = 255
                print(self.wave_message)
        else:
            self.wave_pause_timer -= delta_time
            self.wave_message_alpha = fade_wave_message_alpha(self.wave_pause_timer)
            if self.wave_pause_timer <= 0:
                self._start_next_wave()
        
        # Spawn timers
        self.orb_spawn_timer -= delta_time
        self.artifact_spawn_timer -= delta_time
        
        # Coin spawn timer
        if self.coins_to_spawn > 0:
            self.coin_spawn_timer -= delta_time
            
        # Update pickup texts
        self.pickup_texts = update_pickup_texts(self.pickup_texts, delta_time)
    
    def _update_entities(self, delta_time):
        """Update all game entities."""
        # Update player
        if self.player:
            self.player.update(delta_time)
            
            # Update mouse position for targeting
            if self.right_mouse_down:
                self.player.set_target(self.mouse_x, self.mouse_y)
        
        # Update enemies and their bullets
        for enemy in self.enemies:
            enemy.update(delta_time)
            enemy.bullets.update()
            
        # Check for wave completion by enemy count
        if self.wave_manager.in_wave and len(self.enemies) == 0:
            self.wave_manager.complete_wave()
            
            # Start next wave after pause
            if not self.wave_manager.wave % 3 == 0:  # Every 3rd wave shows shop
                self.wave_manager.start_next_wave(self.enemy_manager, self.enemies)
        
        # Update orbs, coins, and other entities
        self.orbs.update()
        self.coins.update()
        
        # Update artifacts
        for artifact in self.player.artifacts:
            if hasattr(artifact, 'update'):
                artifact.update(delta_time)
        
        # Update score
        self.score += delta_time * 10
        
        # Handle random spawns
        self._handle_spawns(delta_time)
        
        # Update pickup text animations
        if hasattr(self, 'pickup_texts'):
            for i, (text, x, y, timer) in enumerate(self.pickup_texts):
                self.pickup_texts[i] = (text, x, y, timer - delta_time)
            self.pickup_texts = [item for item in self.pickup_texts if item[3] > 0]
            
    def _handle_spawns(self, delta_time):
        """Handle random spawning of game objects."""
        # Spawn orbs
        if self.orb_spawn_timer <= 0:
            self.orbs.append(spawn_random_orb(SCREEN_WIDTH, SCREEN_HEIGHT))
            self.orb_spawn_timer = random.uniform(4, 8)
            
        # Spawn artifacts
        if self.artifact_spawn_timer <= 0 and not self.dash_artifact:
            self.dash_artifact = spawn_dash_artifact(SCREEN_WIDTH, SCREEN_HEIGHT)
            self.artifact_spawn_timer = random.uniform(20, 30)
            
        # Spawn coins
        if self.coins_to_spawn > 0 and self.coin_spawn_timer <= 0:
            x = random.randint(50, SCREEN_WIDTH - 50)
            y = random.randint(50, SCREEN_HEIGHT - 50)
            self.coins.append(Coin(x, y))
            self.coins_to_spawn -= 1
            self.coin_spawn_timer = random.uniform(3, 7)
            print(f"🪙 Spawned a coin! Remaining: {self.coins_to_spawn}")
    
    def _handle_collisions(self, delta_time):
        """Handle all collision detection in the game."""
        # Dash artifact collision
        if self.dash_artifact and arcade.check_for_collision(self.player, self.dash_artifact):
            self.player.has_dash_artifact = True  # Enable dash for player
            self.player.can_dash = True  # Make dash available immediately

            # Create cooldown bar with better dimensions
            if not self.dash_bar:

                # Use a more appropriate size and position
                self.dash_bar = CooldownBar("Dash", 30, 50, 80, 6)  # Match player.draw_artifacts dimensions
                self.dash_bar.set_cooldown(DASH_COOLDOWN)  # Use the constant
                # Initialize with player's current dash timer instead of resetting
                self.dash_bar.timer = self.player.dash_timer

            # Remove the artifact from the game
            self.dash_artifact = None

            # Add pickup text
            self.pickup_texts.append(["Dash Unlocked!", self.player.center_x, self.player.center_y + 30, 2.0])
        
        # Enemy and bullet collisions
        for enemy in self.enemies:
            for bullet in enemy.bullets:
                bullet.update(delta_time)
                dist = arcade.get_distance_between_sprites(self.player, bullet)
                if 10 < dist < 35:
                    self.score += 1
                    print("🌀 Close dodge! +1 score")
                if bullet.age > 0.2 and not self.player.invincible and arcade.check_for_collision(bullet, self.player):
                    self.player.take_damage(0.5)
                    enemy.bullets.remove(bullet)
            if not self.player.invincible and arcade.check_for_collision(enemy, self.player):
                self.player.take_damage(1.0)
        
        # Orb collisions
        for orb in self.orbs:
            orb.update(delta_time)
            if orb.age > 0.5 and arcade.check_for_collision(orb, self.player):
                orb.apply_effect(self.player)
                self.pickup_texts.append([orb.message, self.player.center_x, self.player.center_y, 1.0])

                # Play orb sound
                if isinstance(orb, BuffOrb):
                    arcade.play_sound(arcade.load_sound(resource_path("assets/audio/buff.wav")))
                elif isinstance(orb, DebuffOrb):
                    arcade.play_sound(arcade.load_sound(resource_path("assets/audio/debuff.wav")), volume=0.1)

                self.orbs.remove(orb)
        
        # Coin collisions
        for coin in self.coins:
            coin.update_animation(delta_time)
            if arcade.check_for_collision(self.player, coin):
                game_state.coins += coin.coin_value
                arcade.play_sound(self.coin_sound)
                self.coins.remove(coin)

    def _check_game_state(self):
        """Check for game state transitions."""
        # Currently just a placeholder for future game state checks
        pass
    
    def _start_next_wave(self):
        """Start the next wave of enemies."""
        # Start the next wave with the enemies sprite list
        self.wave_manager.start_next_wave(self.enemy_manager, self.enemies)
        
        # Set up the coin plan
        self.coins_to_spawn = random.randint(1, 5)
        self.coin_spawn_timer = random.uniform(3, 7)
        print(f"🪙 Will spawn {self.coins_to_spawn} coins over time")
        
        # Handle orbs and artifacts
        info = self.wave_manager.spawn_orbs(self.orbs, 3, SCREEN_WIDTH, SCREEN_HEIGHT)
        
        if info and "artifact" in info and info["artifact"]:
            artifact = self.wave_manager.maybe_spawn_artifact(
                self.player.artifacts,
                self.dash_artifact,
                SCREEN_WIDTH,
                SCREEN_HEIGHT
            )
            if artifact:
                self.dash_artifact = artifact
        
        self.wave_duration = 20 + (self.wave_manager.wave - 1) * 5
        self.level_timer = 0
        self.in_wave = True
        print(f"🚀 Starting Wave {self.wave_manager.wave}")
        
        # Check if it's time to go to the shop
        if self.wave_manager.wave % 5 == 0:
            from scripts.views.shop_view import ShopView
            shop_view = ShopView(self.player, self)
            self.window.show_view(shop_view)
            
    def apply_skin_toggle(self):
        """Toggle between available skin sets"""
        try:
            # Use the skin_manager's toggle_skin method
            skin_manager.toggle_skin()
            
            # Update visual elements that depend on the skin
            self.update_visual_elements()
            
            # Play feedback sound
            arcade.play_sound(arcade.load_sound(resource_path("assets/audio/buff.wav")))
        except Exception as e:
            print(f"❌ Error toggling skin: {e}")

    def update_visual_elements(self):
        """Update all visual elements after a skin change"""
        # Update player appearance
        self.player.update_appearance()

        # Update orbs
        for orb in self.orbs:
            orb.update_appearance()

        # Update artifacts
        for artifact in self.player.artifacts:
            artifact.update_appearance()

    def on_mouse_press(self, x, y, button, modifiers):
        """Handle mouse button press."""
        if button == arcade.MOUSE_BUTTON_RIGHT:
            # Set player target for movement (not dash)
            self.player.set_target(x, y)
            self.right_mouse_down = True
            self.mouse_x = x
            self.mouse_y = y

    def on_mouse_release(self, x, y, button, modifiers):
        """Handle mouse button release."""
        if button == arcade.MOUSE_BUTTON_RIGHT:
            self.right_mouse_down = False

    def on_mouse_motion(self, x, y, dx, dy):
        """Track mouse movement."""
        self.mouse_x = x
        self.mouse_y = y

    def on_key_press(self, symbol, modifiers):
        """Handle key press."""
        if symbol == arcade.key.SPACE:
            # Dash toward mouse position
            self.player.try_dash(self.mouse_x, self.mouse_y)
        elif symbol == arcade.key.S:
            self.player.set_target(self.player.center_x, self.player.center_y)
        elif symbol == arcade.key.T:
            self.apply_skin_toggle()
            
        key_map = {
            arcade.key.Q: 0,
            arcade.key.W: 1,
            arcade.key.E: 2,
            arcade.key.R: 3,
        }
        if symbol in key_map:
            idx = key_map[symbol]
            if idx < len(self.player.artifacts):
                artifact = self.player.artifacts[idx]
                name = artifact.__class__.__name__
                if name == "MagnetPulseArtifact":
                    artifact.apply_effect(self.player, self.orbs)
                elif name == "SlowFieldArtifact":
                    for enemy in self.enemies:
                        for bullet in enemy.bullets:
                            artifact.apply_effect(self.player, [bullet])
                elif name == "BulletTimeArtifact":
                    artifact.apply_effect(self.enemies)
                elif name == "CloneDashArtifact":
                    artifact.apply_effect(self.player, self.enemies)
                elif name == "DashArtifact":
                    self.player.try_dash()

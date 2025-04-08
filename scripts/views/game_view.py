import arcade
import random
import math
from scripts.characters.player import Player
from scripts.mechanics.artifacts.dash_artifact import DashArtifact
from scripts.mechanics.orbs.buff_orbs import BuffOrb
from scripts.mechanics.orbs.debuff_orbs import DebuffOrb
from scripts.mechanics.coins.coin_factory import create_coin, Coin
from scripts.mechanics.wave_manager import WaveManager
from scripts.utils.constants import SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE, ARTIFACT_SCALE
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
from scripts.utils.resource_helper import resource_path
from scripts.utils.orb_utils import get_texture_name_from_orb_type
from scripts.skins.skin_manager import skin_manager
from scripts.mechanics.game_state import game_state

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

    def on_show(self):
        arcade.set_background_color(arcade.color.BLACK)
        self.vision_shader = load_vision_shader(self.window)
        self.vision_geometry = create_vision_geometry(self.window)

    def setup(self):
        self.player = Player(self.window.width // 2, self.window.height // 2)
        self.player.window = self.window
        self.player.parent_view = self
        self.wave_manager = WaveManager(self.player)
        self.wave_manager.wave = 1  # Start at wave 4 for debugging the shop
        self.wave_manager.spawn_enemies(self.enemies, self.window.width, self.window.height)
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
        self.player.draw_artifacts()
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

    def on_update(self, delta_time):
        self.player.update(delta_time)
        self.orbs.update()
        self.coins.update()
        self.enemies.update()
        self.score += delta_time * 10
        self.orb_spawn_timer -= delta_time
        self.artifact_spawn_timer -= delta_time
        self.pickup_texts = update_pickup_texts(self.pickup_texts, delta_time)

        for artifact in self.player.artifacts:
            if hasattr(artifact, 'update'):
                artifact.update(delta_time)

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
                self.wave_manager.next_wave()
                info = self.wave_manager.spawn_enemies(self.enemies, SCREEN_WIDTH, SCREEN_HEIGHT)
                self.wave_manager.spawn_orbs(self.orbs, info["orbs"], SCREEN_WIDTH, SCREEN_HEIGHT)

                # Set up the coin plan
                self.coins_to_spawn = random.randint(1, 5)
                self.coin_spawn_timer = random.uniform(3, 7)
                print(f"🪙 Will spawn {self.coins_to_spawn} coins over time")

                if info["artifact"]:
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

        if self.orb_spawn_timer <= 0:
            self.orbs.append(spawn_random_orb(SCREEN_WIDTH, SCREEN_HEIGHT))
            self.orb_spawn_timer = random.uniform(4, 8)
        if self.artifact_spawn_timer <= 0 and not self.dash_artifact:
            self.dash_artifact = spawn_dash_artifact(SCREEN_WIDTH, SCREEN_HEIGHT)
            self.artifact_spawn_timer = random.uniform(20, 30)
        if self.dash_artifact and arcade.check_for_collision(self.player, self.dash_artifact):
            # Only add if not already collected
            if not any(isinstance(a, DashArtifact) for a in self.player.artifacts):
                self.player.add_artifact("dash", 15)  # Add dash artifact with 5 second cooldown
                print("✨ Dash unlocked!")
            else:
                print("⚠️ Dash already unlocked.")
            self.player.can_dash = True
            self.dash_artifact = None

        # Staggered coin spawning
        if self.coins_to_spawn > 0:
            self.coin_spawn_timer -= delta_time
            if self.coin_spawn_timer <= 0:
                x = random.randint(50, SCREEN_WIDTH - 50)
                y = random.randint(50, SCREEN_HEIGHT - 50)
                self.coins.append(Coin(x, y))
                self.coins_to_spawn -= 1
                self.coin_spawn_timer = random.uniform(3, 7)
                print(f"🪙 Spawned a coin! Remaining: {self.coins_to_spawn}")

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

        for coin in self.coins:
            coin.update_animation(delta_time)
            if arcade.check_for_collision(self.player, coin):
                game_state.coins += coin.coin_value
                arcade.play_sound(self.coin_sound)
                self.coins.remove(coin)

        # Handle mouse movement
        if self.right_mouse_down:
            self.player.move_towards_mouse(self, delta_time)
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
        if button == arcade.MOUSE_BUTTON_RIGHT:
            self.right_mouse_down = True
        self.player.set_target(x, y)

    def on_mouse_release(self, x, y, button, modifiers):
        if button == arcade.MOUSE_BUTTON_RIGHT:
            self.right_mouse_down = False

    def on_mouse_motion(self, x, y, dx, dy):
        """
        Track mouse movement

        Args:
            x: Mouse X position
            y: Mouse Y position
            dx: Change in X
            dy: Change in Y
        """
        self.mouse_x = x
        self.mouse_y = y

    def on_key_press(self, symbol, modifiers):
        """Handle key press events"""
        if symbol == arcade.key.SPACE:
            # Try to dash
            self.player.try_dash()
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
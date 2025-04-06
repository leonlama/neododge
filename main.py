import arcade
import random
from scripts.characters.player import Player
from scripts.characters.enemy import Enemy
from scripts.mechanics.artifacts.artifacts import (
    DashArtifact, MagnetPulseArtifact, SlowFieldArtifact,
    BulletTimeArtifact, CloneDashArtifact
)
from scripts.mechanics.orbs.buff_orbs import BuffOrb
from scripts.mechanics.orbs.debuff_orbs import DebuffOrb
from scripts.views.start_view import StartView
from scripts.mechanics.wave_manager import WaveManager

from scripts.utils.constants import SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE
from scripts.utils.shaders import load_vision_shader, create_vision_geometry
from scripts.utils.spawner import spawn_random_orb, spawn_dash_artifact
from scripts.utils.pickup_text import draw_pickup_texts, update_pickup_texts
from scripts.utils.wave_text import draw_wave_message, fade_wave_message_alpha


class NeododgeGame(arcade.View):
    def __init__(self):
        super().__init__()
        self.player = None
        self.enemies = arcade.SpriteList()
        self.orbs = arcade.SpriteList()
        self.dash_artifact = None
        self.pickup_texts = []
        self.wave_manager = None
        self.wave_duration = 20.0
        self.level_timer = 0.0
        self.orb_spawn_timer = random.uniform(4, 8)
        self.artifact_spawn_timer = random.uniform(20, 30)
        self.score = 0
        self.in_wave = True
        self.wave_pause_timer = 0.0
        self.wave_pause = False
        self.wave_message_alpha = 255
        self.wave_message = ""
        self.vision_shader = None
        self.vision_geometry = None

    def on_show(self):
        arcade.set_background_color(arcade.color.BLACK)
        self.vision_shader = load_vision_shader(self.window)
        self.vision_geometry = create_vision_geometry(self.window)

    def setup(self):
        self.player = Player(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        self.player.window = self.window
        self.player.parent_view = self
        self.wave_manager = WaveManager(self.player)
        self.wave_manager.spawn_enemies(self.enemies, SCREEN_WIDTH, SCREEN_HEIGHT)
        self.dash_artifact = spawn_dash_artifact()

    def on_draw(self):
        self.clear()
        self.player.draw()
        self.orbs.draw()
        self.enemies.draw()
        for enemy in self.enemies:
            enemy.bullets.draw()
        if self.dash_artifact:
            self.dash_artifact.draw()

        if self.player.vision_blur:
            self.vision_shader["resolution"] = self.window.get_size()
            self.vision_shader["center"] = (self.player.center_x, self.player.center_y)
            self.vision_shader["radius"] = 130.0
            self.vision_geometry.render(self.vision_shader)

        self.player.draw_hearts()
        self.player.draw_orb_status()
        self.player.draw_artifacts()
        arcade.draw_text(f"Score: {int(self.score)}", 30, SCREEN_HEIGHT - 60, arcade.color.WHITE, 16)

        draw_pickup_texts(self.pickup_texts)

        if not self.wave_pause:
            time_left = max(0, int(self.wave_duration - self.level_timer))
            arcade.draw_text(f"⏱ {time_left}s left", SCREEN_WIDTH // 2, SCREEN_HEIGHT - 60,
                             arcade.color.LIGHT_GRAY, 16, anchor_x="center")

        if not self.in_wave and self.wave_message:
            draw_wave_message(self.wave_message, self.wave_message_alpha)

    def on_update(self, delta_time):
        self.player.update(delta_time)
        self.orbs.update()
        self.enemies.update()
        self.score += delta_time * 10
        self.orb_spawn_timer -= delta_time
        self.artifact_spawn_timer -= delta_time
        self.pickup_texts = update_pickup_texts(self.pickup_texts, delta_time)

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

        if self.orb_spawn_timer <= 0:
            self.orbs.append(spawn_random_orb())
            self.orb_spawn_timer = random.uniform(4, 8)

        if self.artifact_spawn_timer <= 0 and not self.dash_artifact:
            self.dash_artifact = spawn_dash_artifact()
            self.artifact_spawn_timer = random.uniform(20, 30)

        if self.dash_artifact and arcade.check_for_collision(self.player, self.dash_artifact):
            self.player.can_dash = True
            self.player.artifacts.append(DashArtifact())
            self.dash_artifact = None
            print("✨ Dash unlocked!")

        for enemy in self.enemies:
            enemy.update(delta_time)
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
                self.orbs.remove(orb)

    def on_mouse_press(self, x, y, button, modifiers):
        if button == arcade.MOUSE_BUTTON_RIGHT:
            self.player.set_target(x, y)

    def on_key_press(self, symbol, modifiers):
        if symbol == arcade.key.SPACE:
            self.player.try_dash()
        elif symbol == arcade.key.S:
            self.player.set_target(self.player.center_x, self.player.center_y)

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


if __name__ == "__main__":
    window = arcade.Window(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    start_view = StartView()
    window.show_view(start_view)
    arcade.run()

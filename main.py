import arcade
import random
import math

import arcade.gl
import array

from scripts.characters.player import Player
from scripts.characters.enemy import Enemy
from scripts.mechanics.artifacts.artifacts import DashArtifact
from scripts.mechanics.orbs.buff_orbs import BuffOrb
from scripts.mechanics.orbs.debuff_orbs import DebuffOrb
from scripts.views.start_view import StartView
from scripts.views.game_over_view import GameOverView
from scripts.mechanics.wave_manager import WaveManager
from scripts.mechanics.artifacts.artifacts import (
    MagnetPulseArtifact,
    SlowFieldArtifact,
    BulletTimeArtifact,
    CloneDashArtifact
)
from scripts.views.test_views.test_orbs_view import OrbTestView

# --- Constants ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Neododge"

class NeododgeGame(arcade.View):
    def __init__(self):
        super().__init__()
        self.player = None
        self.enemies = None
        self.dash_artifact = None
        self.orbs = arcade.SpriteList()
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
        self.vision_mask = arcade.make_soft_circle_texture(
            300,
            arcade.color.BLACK,
            outer_alpha=255,
            center_alpha=0
        )
        self.vision_shader = None
        self.vision_geometry = None

    def on_show(self):
        arcade.set_background_color(arcade.color.BLACK)

        # Shader setup
        self.vision_shader = self.window.ctx.load_program(
            vertex_shader="""
            #version 330
            in vec2 in_vert;
            in vec2 in_tex;
            out vec2 uv;
            void main() {
                gl_Position = vec4(in_vert, 0.0, 1.0);
                uv = in_tex;
            }
            """,
            fragment_shader="""
            #version 330
            uniform vec2 resolution;
            uniform vec2 center;
            uniform float radius;
            in vec2 uv;
            out vec4 fragColor;

            void main() {
                vec2 fragCoord = uv * resolution;
                float dist = distance(fragCoord, center);
                float alpha = smoothstep(radius, radius - 25.0, dist);
                fragColor = vec4(0, 0, 0, alpha);
            }
            """
        )

        # Fullscreen triangle pair (2 triangles)
        quad = array.array(
            'f', [
                -1.0, -1.0, 0.0, 0.0,
                 1.0, -1.0, 1.0, 0.0,
                -1.0,  1.0, 0.0, 1.0,

                 1.0, -1.0, 1.0, 0.0,
                 1.0,  1.0, 1.0, 1.0,
                -1.0,  1.0, 0.0, 1.0
            ]
        )
        vbo = self.window.ctx.buffer(data=quad)
        self.vision_geometry = self.window.ctx.geometry(
            [arcade.gl.BufferDescription(vbo, "2f 2f", ["in_vert", "in_tex"])]
        )

    def setup(self):
        self.player = Player(self.window.width // 2, self.window.height // 2)
        self.player.window = self.window  # 💡 Makes GameOverView possible
        self.player.parent_view = self    # 💡 So player can access score
        self.enemies = arcade.SpriteList()
        x, y = random.randint(50, SCREEN_WIDTH - 50), random.randint(50, SCREEN_HEIGHT - 50)
        self.dash_artifact = DashArtifact(x, y)
        self.orbs = arcade.SpriteList()
        self.wave_manager = WaveManager(self.player)
        self.wave_manager.spawn_enemies(self.enemies, self.window.width, self.window.height)

    def on_draw(self):
        self.clear()

        # --- World Layer ---
        # Everything that should be affected by blur
        self.player.draw()
        self.orbs.draw()
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

        for text, x, y, _ in self.pickup_texts:
            arcade.draw_text(text, x, y + 20, arcade.color.WHITE, 14, anchor_x="center")

        # Draw wave timer
        if not self.wave_pause:
            time_left = max(0, int(self.wave_duration - self.level_timer))
            arcade.draw_text(f"⏱ {time_left}s left", SCREEN_WIDTH // 2, SCREEN_HEIGHT - 60,
                             arcade.color.LIGHT_GRAY, 16, anchor_x="center")

        # Draw wave message if not in wave
        if not self.in_wave and self.wave_message:
            fade_color = (*arcade.color.LIGHT_GREEN[:3], self.wave_message_alpha)  # Add alpha to RGB

            arcade.draw_text(
                self.wave_message,
                SCREEN_WIDTH / 2,
                SCREEN_HEIGHT / 2,
                fade_color,
                font_size=24,
                anchor_x="center",
                font_name="Kenney Pixel"
            )

    def draw_vision_blur(self):
        # Create a shape list
        shape_list = arcade.ShapeElementList()

        # Full black screen
        full_black = arcade.create_rectangle_filled(
            SCREEN_WIDTH // 2,
            SCREEN_HEIGHT // 2,
            SCREEN_WIDTH,
            SCREEN_HEIGHT,
            arcade.color.BLACK
        )
        shape_list.append(full_black)

        # Transparent circular hole (by setting blend mode properly)
        vision_radius = 150
        transparent_circle = arcade.create_ellipse_filled(
            self.player.center_x,
            self.player.center_y,
            vision_radius * 2,
            vision_radius * 2,
            (0, 0, 0, 0)
        )
        shape_list.append(transparent_circle)

        # Enable stencil-style blending
        shape_list.draw()

    def on_update(self, delta_time):
        self.player.update(delta_time)
        self.orbs.update()
        
        if self.in_wave:
            self.level_timer += delta_time

            if self.level_timer >= self.wave_duration:
                self.in_wave = False
                self.wave_pause_timer = 3.0  # 3 second pause
                self.wave_message_alpha = 255
                self.wave_message = f"Successfully survived Wave {self.wave_manager.wave}!"
                print(self.wave_message)
        else:
            self.wave_pause_timer -= delta_time
            self.wave_message_alpha = max(0, int(255 * (self.wave_pause_timer / 3.0)))  # fade out

            if self.wave_pause_timer <= 0:
                self.wave_manager.next_wave()
                wave_info = self.wave_manager.spawn_enemies(self.enemies, self.window.width, self.window.height)

                # Orbs
                self.wave_manager.spawn_orbs(self.orbs, wave_info["orbs"], self.window.width, self.window.height)

                # Artifact
                if wave_info["artifact"]:
                    artifact = self.wave_manager.maybe_spawn_artifact(
                        self.player.artifacts,
                        self.dash_artifact,
                        self.window.width,
                        self.window.height
                    )
                    if artifact:
                        self.dash_artifact = artifact

                self.wave_duration = 20 + (self.wave_manager.wave - 1) * 5
                self.level_timer = 0
                self.in_wave = True
                print(f"🚀 Starting Wave {self.wave_manager.wave}")

        self.orb_spawn_timer -= delta_time
        self.artifact_spawn_timer -= delta_time
        self.score += delta_time * 10  # 10 points per second survived

        if self.orb_spawn_timer <= 0:
            x, y = random.randint(50, SCREEN_WIDTH - 50), random.randint(50, SCREEN_HEIGHT - 50)
            orb = random.choice([
                BuffOrb(x, y),
                DebuffOrb(x, y)
            ])
            self.orbs.append(orb)
            self.orb_spawn_timer = random.uniform(4, 8)

        if self.artifact_spawn_timer <= 0 and not self.dash_artifact:
            x, y = random.randint(50, SCREEN_WIDTH - 50), random.randint(50, SCREEN_HEIGHT - 50)
            self.dash_artifact = DashArtifact(x, y)
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

                # 🔥 Close dodge detection (within 35 px, but not hit)
                dist = arcade.get_distance_between_sprites(self.player, bullet)
                if 10 < dist < 35:
                    self.score += 1
                    print("🌀 Close dodge! +1 score")

                # Bullet hit check
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

        # Update pickup text durations
        for t in self.pickup_texts:
            t[3] -= delta_time
        self.pickup_texts = [t for t in self.pickup_texts if t[3] > 0]

    def on_mouse_press(self, x, y, button, modifiers):
        if button == arcade.MOUSE_BUTTON_RIGHT:
            self.player.set_target(x, y)

    def on_key_press(self, symbol, modifiers):
        if symbol == arcade.key.SPACE:
            self.player.try_dash()
        elif symbol == arcade.key.S:
            self.player.set_target(self.player.center_x, self.player.center_y)

        # 🎯 Artifact Activation
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

                # 💡 Dispatch effect by type
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

# Game Loop with wave manager

if __name__ == "__main__":
    window = arcade.Window(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    start_view = StartView()
    window.show_view(start_view)
    arcade.run()

# TESTING ORBS

"""if __name__ == "__main__":
    window = arcade.Window(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    test_view = OrbTestView()
    test_view.setup()
    window.show_view(test_view)
    arcade.run()"""

# TESTING ARTIFACTS

"""if __name__ == "__main__":
    window = arcade.Window(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    test_view = TestArtifactsView()
    window.show_view(test_view)
    arcade.run()"""

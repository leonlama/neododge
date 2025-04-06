import arcade
import math
from scripts.characters.player import Player
from scripts.mechanics.orbs.buff_orbs import BuffOrb
from scripts.mechanics.orbs.debuff_orbs import DebuffOrb

import arcade
import arcade.gl
import array

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Orb Test View"

class OrbTestView(arcade.View):
    def __init__(self):
        super().__init__()
        self.player = None
        self.orbs = arcade.SpriteList()
        self.enemies = arcade.SpriteList()  # Assuming enemies are part of the test view
        self.dash_artifact = None  # Assuming a dash artifact might be used
        self.score = 0  # Assuming a score is tracked
        self.vision_mask = arcade.make_soft_circle_texture(300, arcade.color.BLACK, outer_alpha=255, center_alpha=0)
        self.fbo = None
        self.vision_shader = None

    def on_show(self):
        arcade.set_background_color(arcade.color.DARK_SLATE_GRAY)
        
        self.fbo = self.window.ctx.framebuffer(
            color_attachments=[self.window.ctx.texture((self.window.width, self.window.height))]
        )

        # Shader that cuts a circle around the player
        self.vision_shader = self.window.ctx.program(
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
                    vec2 screen_pos = uv * resolution;
                    float dist = distance(screen_pos, center);
                    if (dist < radius) {
                        discard;
                    }
                    fragColor = vec4(0, 0, 0, 0.9);  // semi-transparent black outside vision
                }
            """
        )

        # Define 2 triangles (full screen quad)
        quad = array.array(
            'f', [
                -1.0, -1.0, 0.0, 0.0,  # bottom left
                 1.0, -1.0, 1.0, 0.0,  # bottom right
                -1.0,  1.0, 0.0, 1.0,  # top left

                 1.0, -1.0, 1.0, 0.0,  # bottom right
                 1.0,  1.0, 1.0, 1.0,  # top right
                -1.0,  1.0, 0.0, 1.0   # top left
            ]
        )

        vbo = self.window.ctx.buffer(data=quad)

        # Tell OpenGL how to interpret the vertex data
        self.vision_geometry = self.window.ctx.geometry(
            [arcade.gl.BufferDescription(vbo, "2f 2f", ["in_vert", "in_tex"])]
        )

    def setup(self):
        start_x = SCREEN_WIDTH // 2
        start_y = 100
        self.player = Player(start_x, start_y)
        self.player.window = self.window
        self.player.parent_view = self
        self.player.pickup_messages = []
        self.player.can_dash = True  # Allow dashing in this view

        # Spawn buff orbs
        buff_types = [
            "gray", "red", "gold",
            "speed_10", "speed_20", "speed_35",
            "mult_1_5", "mult_2",
            "cooldown", "shield"
        ]
        for i, orb_type in enumerate(buff_types):
            orb = BuffOrb(100 + i * 60, 400, orb_type)
            self.orbs.append(orb)

        # Spawn debuff orbs
        debuff_types = [
            "slow", "mult_down_0_5", "mult_down_0_25",
            "cooldown_up", "vision_blur", "big_hitbox" #"inverse_move",
        ]
        for i, orb_type in enumerate(debuff_types):
            orb = DebuffOrb(100 + i * 60, 300, orb_type)
            self.orbs.append(orb)

    def on_draw(self):
        self.clear()

        # --- World Layer ---
        self.player.draw()
        self.orbs.draw()
        self.enemies.draw()
        for enemy in self.enemies:
            enemy.bullets.draw()
        if self.dash_artifact:
            self.dash_artifact.draw()

        # 👁️ Apply vision blur AFTER drawing world, BEFORE HUD
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

        for text, x, y, _ in self.player.pickup_texts:
            arcade.draw_text(text, x, y + 20, arcade.color.WHITE, 14, anchor_x="center")
            
    def draw_vision_blur(self):
        # Render current frame to FBO
        self.fbo.use()
        self.clear()
        self.player.draw()
        self.orbs.draw()

        # Go back to screen
        self.window.ctx.screen.use()

        # Bind texture and shader
        self.fbo.color_attachments[0].use()
        self.vision_shader["tex"] = 0
        self.vision_shader["resolution"] = (self.window.width, self.window.height)
        self.vision_shader["center"] = (self.player.center_x, self.player.center_y)
        self.vision_shader["radius"] = 150.0

        self.vision_geometry.render(self.vision_shader)

    def on_update(self, delta_time):
        self.player.update(delta_time)
        self.orbs.update()

        for orb in self.orbs:
            orb.update(delta_time)
            if arcade.check_for_collision(self.player, orb):
                orb.apply_effect(self.player)
                self.player.pickup_texts.append([orb.message, self.player.center_x, self.player.center_y, 1.0])
                self.orbs.remove(orb)

        for t in self.player.pickup_texts:
            t[3] -= delta_time
        self.player.pickup_texts = [t for t in self.player.pickup_texts if t[3] > 0]

    def on_mouse_press(self, x, y, button, modifiers):
        if button == arcade.MOUSE_BUTTON_RIGHT:
            self.player.set_target(x, y)

    def on_key_press(self, symbol, modifiers):
        if symbol == arcade.key.RIGHT:
            self.player.center_x += 10
        elif symbol == arcade.key.LEFT:
            self.player.center_x -= 10
        elif symbol == arcade.key.UP:
            self.player.center_y += 10
        elif symbol == arcade.key.DOWN:
            self.player.center_y -= 10
        elif symbol == arcade.key.SPACE:
            self.player.try_dash()

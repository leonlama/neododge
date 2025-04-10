import arcade
import math

from scripts.views.game_over_view import GameOverView
from scripts.utils.resource_helper import resource_path

damage_sound = arcade.load_sound(resource_path("assets/audio/damage.wav"))

PLAYER_SPEED = 300
DASH_DISTANCE = 150

class Player(arcade.Sprite):
    def __init__(self, start_x, start_y):
        super().__init__()
        self.texture = arcade.make_soft_square_texture(32, arcade.color.CYAN, outer_alpha=255)
        self.center_x = start_x
        self.center_y = start_y
        self.target_x = start_x
        self.target_y = start_y
        self.can_dash = False
        self.dash_timer = 0
        self.invincible = False
        self.invincibility_timer = 0
        self.blink_state = True
        self.max_slots = 3
        self.current_hearts = 3.0
        self.gold_hearts = 0
        self.speed_bonus = 1.0
        self.multiplier = 1.0
        self.shield = False
        self.mult_timer = 0
        self.cooldown_factor = 1.0
        self.cooldown = 1.0
        self.artifacts = []
        self.active_orbs = []
        self.vision_blur = False
        self.vision_timer = 0.0
        self.inverse_move = False
        self.window = None
        self.parent_view = None
        self.artifact_cooldowns = {}
        self.pickup_texts = []
        self.coins = 0

    def set_target(self, x, y):
        if self.inverse_move:
            dx = x - self.center_x
            dy = y - self.center_y
            self.target_x = self.center_x - dx
            self.target_y = self.center_y - dy
        else:
            self.target_x = x
            self.target_y = y

    def update(self, delta_time: float = 1 / 60):
        self.dash_timer += delta_time * self.cooldown_factor

        if self.mult_timer > 0:
            self.mult_timer -= delta_time
            if self.mult_timer <= 0:
                self.multiplier = 1.0

        for orb in self.active_orbs:
            orb[1] -= delta_time
        self.active_orbs = [orb for orb in self.active_orbs if orb[1] > 0]

        if self.vision_blur:
            self.vision_timer -= delta_time
            if self.vision_timer <= 0:
                self.vision_blur = False

        for artifact in self.artifacts:
            if hasattr(artifact, "cooldown_timer") and artifact.cooldown_timer < artifact.cooldown:
                artifact.cooldown_timer += delta_time

        if self.target_x and self.target_y:
            dx = self.target_x - self.center_x
            dy = self.target_y - self.center_y
            dist = math.hypot(dx, dy)
            if dist < 5:
                self.change_x = 0
                self.change_y = 0
                self.target_x = None
                self.target_y = None
            else:
                direction_x = dx / dist
                direction_y = dy / dist
                speed = PLAYER_SPEED * self.speed_bonus * delta_time
                self.change_x = direction_x * speed
                self.change_y = direction_y * speed
                self.center_x += self.change_x
                self.center_y += self.change_y

        if self.invincible:
            self.invincibility_timer += delta_time
            if int(self.invincibility_timer * 10) % 2 == 0:
                self.blink_state = False
            else:
                self.blink_state = True
            if self.invincibility_timer >= 1.0:
                self.invincible = False
                self.invincibility_timer = 0
                self.blink_state = True

        if hasattr(self, "big_hitbox_timer") and self.big_hitbox_timer > 0:
            self.big_hitbox_timer -= delta_time
            if self.big_hitbox_timer <= 0:
                self.width, self.height = self.original_size
                self.set_hit_box(self.texture.hit_box_points)

    def try_dash(self):
        for artifact in self.artifacts:
            if artifact.name == "Dash":
                if artifact.cooldown_timer >= artifact.cooldown:
                    self.perform_dash()
                    artifact.cooldown_timer = 0
                else:
                    print("❌ Dash on cooldown.")

    def perform_dash(self):
        dx = self.target_x - self.center_x
        dy = self.target_y - self.center_y
        distance = math.hypot(dx, dy)
        if distance > 0:
            direction_x = dx / distance
            direction_y = dy / distance
            self.center_x += direction_x * DASH_DISTANCE
            self.center_y += direction_y * DASH_DISTANCE
            self.dash_timer = 0

    def take_damage(self, amount: float):
        if self.invincible:
            return
        if self.shield:
            self.shield = False
            return

        arcade.play_sound(damage_sound)
        self.invincible = True
        self.invincibility_timer = 0
        while amount > 0:
            if self.gold_hearts > 0:
                self.gold_hearts -= 1
                amount -= 1
            elif self.current_hearts > 0:
                self.current_hearts -= 0.5
                amount -= 0.5
            else:
                break
        if self.current_hearts + self.gold_hearts <= 0:
            if self.window and self.parent_view:
                self.window.show_view(GameOverView(self.parent_view.score))

    def draw(self):
        if not self.invincible or self.blink_state:
            super().draw()

    def draw_hearts(self, x_start=30, y=570):
        for i in range(self.max_slots):
            x = x_start + i * 40
            if i < int(self.current_hearts):
                arcade.draw_text("❤", x, y, arcade.color.RED, 30)
            elif i < self.current_hearts:
                arcade.draw_text("♥", x, y, arcade.color.LIGHT_RED_OCHRE, 30)
            else:
                arcade.draw_text("♡", x, y, arcade.color.GRAY, 30)
        for i in range(self.gold_hearts):
            x = x_start + (self.max_slots + i) * 40
            arcade.draw_text("💛", x, y, arcade.color.GOLD, 30)

    def draw_orb_status(self, screen_width=800, screen_height=600):
        x = screen_width - 220
        y = screen_height - 30
        line_height = 20
        i = 0
        if self.shield:
            arcade.draw_text("🛡️ Shield Active", x, y - i * line_height, arcade.color.LIGHT_GREEN, 14)
            i += 1
        if self.speed_bonus > 1.0:
            percent = int((self.speed_bonus - 1) * 100)
            arcade.draw_text(f"⚡ Speed +{percent}%", x, y - i * line_height, arcade.color.LIGHT_BLUE, 14)
            i += 1
        if self.cooldown_factor < 1.0:
            arcade.draw_text(f"⏱️ Cooldown x{self.cooldown_factor}", x, y - i * line_height, arcade.color.ORCHID, 14)
            i += 1
        for orb in self.active_orbs:
            label, time_left = orb
            arcade.draw_text(f"{label} ({int(time_left)}s)", x, y - i * line_height, arcade.color.LIGHT_YELLOW, 14)
            i += 1

    def draw_artifacts(self):
        start_x = 30
        y = 50
        font = "Kenney Pixel"
        font_size = 13
        bar_width = 50
        bar_height = 6
        bar_offset = -10

        for idx, artifact in enumerate(self.artifacts):
            x = start_x + 70 * idx
            text = artifact.name

            # ✅ Determine if artifact is ready or on cooldown
            ready = hasattr(artifact, "cooldown_timer") and artifact.cooldown_timer >= artifact.cooldown
            text_color = arcade.color.YELLOW if ready else arcade.color.DARK_GRAY

            # 📝 Draw artifact name
            arcade.draw_text(
                text,
                x,
                y,
                text_color,
                font_size=font_size,
                font_name=font,
                anchor_x="left"
            )

            # ⏳ Draw cooldown bar
            if hasattr(artifact, "cooldown") and hasattr(artifact, "cooldown_timer"):
                # Ratio goes from 0 (just used) to 1 (ready)
                cooldown_ratio = min(artifact.cooldown_timer / artifact.cooldown, 1.0)
                fill_width = bar_width * cooldown_ratio

                # Background bar
                arcade.draw_rectangle_filled(
                    x + bar_width / 2,
                    y + bar_offset,
                    bar_width,
                    bar_height,
                    arcade.color.DARK_GRAY
                )

                # Yellow fill indicating time until ready
                arcade.draw_rectangle_filled(
                    x + fill_width / 2,
                    y + bar_offset,
                    fill_width,
                    bar_height,
                    arcade.color.YELLOW
                )
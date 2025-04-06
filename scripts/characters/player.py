import arcade
import math

from scripts.views.game_over_view import GameOverView

PLAYER_SPEED = 300
DASH_DISTANCE = 150
DASH_COOLDOWN = 3  # seconds

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
        self.blink_state = True  # for visual flicker
        self.max_slots = 3
        self.current_hearts = 3.0
        self.gold_hearts = 0
        self.speed_bonus = 1.0
        self.multiplier = 1.0
        self.shield = False
        self.mult_timer = 0
        self.cooldown_factor = 1.0  # 1.0 = normal, 0.5 = 2x faster
        self.cooldown = 1.0  # Base value, can be reduced by orbs
        self.artifacts = []  # Active ability names (max 1–3?)
        self.active_orbs = []  # list of [name:str, time:float]
        self.vision_blur = False
        self.vision_timer = 0.0
        self.inverse_move = False
        self.window = None
        self.parent_view = None
        self.artifact_cooldowns = {}  # Dict[str, float]
        self.pickup_texts = []  # Tracks floating messages like "💛 Golden heart gained!"

    def set_target(self, x, y):
        if self.inverse_move:
            # Invert the direction: move away from the target click
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
                print("🔚 Multiplier expired.")

        # Tick down all active orb durations
        for orb in self.active_orbs:
            orb[1] -= delta_time
        self.active_orbs = [orb for orb in self.active_orbs if orb[1] > 0]

        if self.vision_blur:
            self.vision_timer -= delta_time
            if self.vision_timer <= 0:
                self.vision_blur = False

        # Cool down artifacts
        for key in list(self.artifact_cooldowns.keys()):
            self.artifact_cooldowns[key] -= delta_time
            if self.artifact_cooldowns[key] <= 0:
                del self.artifact_cooldowns[key]

        dx = self.target_x - self.center_x
        dy = self.target_y - self.center_y
        distance = math.hypot(dx, dy)

        # Stop moving if close enough (snap into place)
        if distance < 2:
            self.center_x = self.target_x
            self.center_y = self.target_y
            return

        direction_x = dx / distance
        direction_y = dy / distance
        self.center_x += direction_x * PLAYER_SPEED * self.speed_bonus * delta_time
        self.center_y += direction_y * PLAYER_SPEED * self.speed_bonus * delta_time

        if self.invincible:
            self.invincibility_timer += delta_time
            # Toggle blink every 0.1s
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
                print("🧼 Big Hitbox expired")

    def try_dash(self):
        if self.can_dash and self.dash_timer >= DASH_COOLDOWN * self.cooldown_factor:
            dx = self.target_x - self.center_x
            dy = self.target_y - self.target_y
            distance = math.hypot(dx, dy)

            if distance > 0:
                direction_x = dx / distance
                direction_y = dy / distance
                self.center_x += direction_x * DASH_DISTANCE
                self.center_y += direction_y * DASH_DISTANCE
                self.dash_timer = 0
                print("💨 Dashed!")

    def take_damage(self, amount: float):
        if self.invincible:
            print("🚫 Player is invincible! No damage taken.")
            return

        if self.shield:
            self.shield = False
            print("🛡️ Shield blocked the damage!")
            return

        print(f"💔 Damage taken: {amount}")
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

        total_health = self.current_hearts + self.gold_hearts
        print(f"💔 Damage taken! Remaining Hearts: {total_health}")
        if total_health <= 0:
            print("💀 Game Over!")
            if self.window and self.parent_view:
                self.window.show_view(GameOverView(self.parent_view.score))
            else:
                print("❌ Could not show game over screen – missing view or window reference.")

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

        # Shield icon
        if self.shield:
            arcade.draw_text("🛡️ Shield Active", x, y - i * line_height, arcade.color.LIGHT_GREEN, 14)
            i += 1

        # Speed bonus
        if self.speed_bonus > 1.0:
            percent = int((self.speed_bonus - 1) * 100)
            arcade.draw_text(f"⚡ Speed +{percent}%", x, y - i * line_height, arcade.color.LIGHT_BLUE, 14)
            i += 1

        # Cooldown reduction
        if self.cooldown_factor < 1.0:
            arcade.draw_text(f"⏱️ Cooldown x{self.cooldown_factor}", x, y - i * line_height, arcade.color.ORCHID, 14)
            i += 1

        # Timed orb effects (e.g., multipliers)
        for orb in self.active_orbs:
            label, time_left = orb
            arcade.draw_text(f"{label} ({int(time_left)}s)", x, y - i * line_height, arcade.color.LIGHT_YELLOW, 14)
            i += 1

    def draw_artifacts(self):
        """Draw artifact names or icons at bottom-left of the screen."""
        for i, art in enumerate(self.artifacts):
            arcade.draw_text(art.name, 20, 20 + i * 20, arcade.color.GOLD, 14)

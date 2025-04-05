import arcade
import math

PLAYER_SPEED = 300
DASH_DISTANCE = 150
DASH_COOLDOWN = 1.5  # seconds

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

    def set_target(self, x, y):
        self.target_x = x
        self.target_y = y

    def update(self, delta_time: float = 1 / 60):
        self.dash_timer += delta_time

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
        self.center_x += direction_x * PLAYER_SPEED * delta_time
        self.center_y += direction_y * PLAYER_SPEED * delta_time

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

    def try_dash(self):
        if self.can_dash and self.dash_timer >= DASH_COOLDOWN:
            dx = self.target_x - self.center_x
            dy = self.target_y - self.center_y
            distance = math.hypot(dx, dy)

            if distance > 0:
                direction_x = dx / distance
                direction_y = dy / distance
                self.center_x += direction_x * DASH_DISTANCE
                self.center_y += direction_y * DASH_DISTANCE
                self.dash_timer = 0
                print("💨 Dashed!")

    def draw(self):
        if not self.invincible or (self.invincible and self.blink_state):
            super().draw()

import arcade
import math
import random

class Enemy(arcade.Sprite):
    """Enemy sprite that follows or moves in patterns."""

    def __init__(self, x, y, target=None, enemy_type="chaser"):
        """Initialize enemy with position and optional target."""
        super().__init__()

        # Set appearance
        self.texture = arcade.make_soft_square_texture(32, arcade.color.RED, outer_alpha=255)

        # Set position
        self.center_x = x
        self.center_y = y

        # Set target (usually the player)
        self.target = target

        # Set type and behavior
        self.enemy_type = enemy_type
        self._set_behavior_from_type()

        # Movement properties
        self.speed = 100
        self.direction_timer = 0
        self.direction = random.choice([(1, 0), (-1, 0), (0, 1), (0, -1)])

        # Shooting properties (for shooter type)
        self.shoot_timer = 0
        self.bullets = arcade.SpriteList()

    def _set_behavior_from_type(self):
        """Set behavior based on enemy type."""
        if self.enemy_type == "chaser":
            self.behavior = self._chase_behavior
        elif self.enemy_type == "wander":
            self.behavior = self._wander_behavior
        elif self.enemy_type == "shooter":
            self.behavior = self._shooter_behavior
        else:
            # Default to chaser
            self.behavior = self._chase_behavior

    def update(self, delta_time=1/60):
        """Update enemy position and behavior."""
        # Call the appropriate behavior method
        self.behavior(delta_time)

        # Update bullets if any
        if hasattr(self, 'bullets'):
            self.bullets.update()

    def _chase_behavior(self, delta_time):
        """Chase the target."""
        if self.target:
            # Calculate direction to target
            dx = self.target.center_x - self.center_x
            dy = self.target.center_y - self.center_y
            distance = max(1, math.hypot(dx, dy))

            # Normalize and apply speed
            self.center_x += (dx / distance) * self.speed * delta_time
            self.center_y += (dy / distance) * self.speed * delta_time

    def _wander_behavior(self, delta_time):
        """Wander randomly, changing direction occasionally."""
        # Update direction timer
        self.direction_timer += delta_time
        if self.direction_timer >= 2.0:  # Change direction every 2 seconds
            self.direction_timer = 0
            self.direction = random.choice([(1, 0), (-1, 0), (0, 1), (0, -1)])

        # Move in current direction
        dx, dy = self.direction
        self.center_x += dx * self.speed * 0.8 * delta_time  # Slower than chaser
        self.center_y += dy * self.speed * 0.8 * delta_time

        # Bounce off screen edges
        screen_width, screen_height = 800, 600  # Default values
        if self.left < 0 or self.right > screen_width:
            self.direction = (-self.direction[0], self.direction[1])
        if self.bottom < 0 or self.top > screen_height:
            self.direction = (self.direction[0], -self.direction[1])

    def _shooter_behavior(self, delta_time):
        """Move less but shoot at the target."""
        # Move slowly
        self._wander_behavior(delta_time * 0.5)  # Half speed of wanderer

        # Shoot at target
        if self.target:
            self.shoot_timer += delta_time
            if self.shoot_timer >= 1.5:  # Shoot every 1.5 seconds
                self.shoot_timer = 0
                self._shoot_at_target()

    def _shoot_at_target(self):
        """Create a bullet aimed at the target."""
        if not self.target:
            return

        # Create bullet
        bullet = Bullet(
            self.center_x, 
            self.center_y,
            self.target.center_x,
            self.target.center_y
        )
        self.bullets.append(bullet)

class Bullet(arcade.Sprite):
    """Bullet sprite shot by enemies."""

    def __init__(self, start_x, start_y, target_x, target_y):
        super().__init__()
        self.texture = arcade.make_soft_circle_texture(8, arcade.color.YELLOW)
        self.center_x = start_x
        self.center_y = start_y

        # Calculate direction to target
        dx = target_x - start_x
        dy = target_y - start_y
        distance = max(1, math.hypot(dx, dy))

        # Set velocity (normalize direction and multiply by speed)
        speed = 200
        self.change_x = dx / distance * speed
        self.change_y = dy / distance * speed

    def update(self):
        """Update bullet position."""
        # Move according to velocity
        self.center_x += self.change_x * 1/60
        self.center_y += self.change_y * 1/60

        # Remove if off-screen
        screen_width, screen_height = 800, 600  # Default values
        if (self.right < 0 or self.left > screen_width or 
            self.bottom > screen_height or self.top < 0):
            self.remove_from_sprite_lists()
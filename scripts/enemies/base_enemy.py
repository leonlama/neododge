import arcade
import random
import math
from src.core.resource_manager import resource_path

class BaseEnemy(arcade.Sprite):
    """Base class for all enemy types in the game."""

    def __init__(self, x, y, scale=1.0):
        super().__init__(scale=scale)

        # Position
        self.center_x = x
        self.center_y = y

        # Movement
        self.speed = 2.0
        self.max_speed = 4.0
        self.acceleration = 0.1
        self.target_x = x
        self.target_y = y

        # Combat
        self.health = 1
        self.damage = 1
        self.bullets = arcade.SpriteList()
        self.can_shoot = False
        self.shoot_cooldown = 2.0
        self.shoot_timer = 0

        # Behavior
        self.behavior_type = "chase"  # Options: "chase", "avoid", "patrol", "stationary"
        self.patrol_points = []
        self.current_patrol_point = 0
        self.patrol_wait_time = 0

        # Visual effects
        self.alpha = 255
        self.hit_flash_timer = 0

        # Game reference
        self.game_view = None

        # Sound effects
        try:
            self.death_sound = arcade.load_sound(resource_path("assets/audio/enemy_death.wav"))
        except:
            self.death_sound = None

    def update(self, delta_time=1/60):
        """Update enemy behavior and position."""
        # Update timers
        if self.shoot_timer > 0:
            self.shoot_timer -= delta_time

        if self.hit_flash_timer > 0:
            self.hit_flash_timer -= delta_time
            # Flash effect
            self.alpha = 128 + int(127 * math.sin(self.hit_flash_timer * 10))
        else:
            self.alpha = 255

        # Update behavior based on type
        if self.behavior_type == "chase":
            self._chase_behavior()
        elif self.behavior_type == "avoid":
            self._avoid_behavior()
        elif self.behavior_type == "patrol":
            self._patrol_behavior(delta_time)
        # Stationary enemies don't move

        # Shoot if able
        if self.can_shoot and self.shoot_timer <= 0:
            self._shoot()
            self.shoot_timer = self.shoot_cooldown

    def _chase_behavior(self):
        """Chase the player."""
        # This will be implemented by child classes
        pass

    def _avoid_behavior(self):
        """Move away from the player."""
        # This will be implemented by child classes
        pass

    def _patrol_behavior(self, delta_time):
        """Move between patrol points."""
        if not self.patrol_points:
            return

        # If waiting at a point
        if self.patrol_wait_time > 0:
            self.patrol_wait_time -= delta_time
            return

        # Get current target point
        target = self.patrol_points[self.current_patrol_point]

        # Move towards target
        dx = target[0] - self.center_x
        dy = target[1] - self.center_y
        distance = math.sqrt(dx*dx + dy*dy)

        # If we reached the point
        if distance < 10:
            # Move to next patrol point
            self.current_patrol_point = (self.current_patrol_point + 1) % len(self.patrol_points)
            self.patrol_wait_time = random.uniform(0.5, 2.0)
            return

        # Move towards target
        if distance > 0:
            self.change_x = dx / distance * self.speed
            self.change_y = dy / distance * self.speed

        # Update position
        self.center_x += self.change_x
        self.center_y += self.change_y

    def _shoot(self):
        """Shoot a bullet at the player."""
        # This will be implemented by child classes
        pass

    def take_damage(self, amount):
        """Take damage and check if dead."""
        self.health -= amount
        self.hit_flash_timer = 0.2

        if self.health <= 0:
            self._on_death()
            return True
        return False

    def _on_death(self):
        """Handle enemy death."""
        # Play death sound
        if self.death_sound:
            arcade.play_sound(self.death_sound, volume=0.2)

        # This will be extended by child classes
        self.kill()

    def set_target(self, x, y):
        """Set a target position for the enemy."""
        self.target_x = x
        self.target_y = y

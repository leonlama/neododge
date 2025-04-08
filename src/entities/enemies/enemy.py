import arcade
import math
import random
from src.skins.skin_manager import skin_manager
from src.audio.sound_manager import sound_manager

class Enemy(arcade.Sprite):
    """Base enemy class that all enemy types inherit from."""

    def __init__(self, x, y, target=None, enemy_type="wanderer"):
        """Initialize the enemy.

        Args:
            x: Initial x position.
            y: Initial y position.
            target: The target to follow (usually the player).
            enemy_type: Type of enemy behavior.
        """
        super().__init__()

        # Set position
        self.center_x = x
        self.center_y = y

        # Set target (usually the player)
        self.target = target

        # Set type and behavior
        self.enemy_type = enemy_type

        # Set up texture using skin manager
        try:
            self.texture = skin_manager.get_texture("enemies", enemy_type)
            if not self.texture:
                # Create a square texture as fallback
                if enemy_type == "wanderer":
                    color = arcade.color.BLUE
                elif enemy_type == "chaser":
                    color = arcade.color.RED
                elif enemy_type == "shooter":
                    color = arcade.color.PURPLE
                else:
                    color = arcade.color.ORANGE

                # Create a square texture
                self.texture = arcade.make_soft_square_texture(30, color, 255, 5)
        except Exception as e:
            print(f"⚠️ Error loading enemy texture: {e}")
            # Fallback to a simple square
            self.texture = arcade.make_soft_square_texture(30, arcade.color.RED, 255, 5)

        # Set scale
        self.scale = skin_manager.get_enemy_scale()

        # Set health and other properties
        self.health = 1
        self.max_health = 1
        self.speed = random.uniform(100, 150)
        self.damage = 1

        # Set velocity (random direction for wanderer)
        angle = random.uniform(0, 2 * math.pi)
        self.change_x = self.speed * math.cos(angle)
        self.change_y = self.speed * math.sin(angle)

        # Movement properties
        self.direction_timer = 0
        self.direction = random.choice([(1, 0), (-1, 0), (0, 1), (0, -1)])

        # Set up bullet firing for shooter
        self.shoot_timer = 0
        self.fire_rate = random.uniform(1.0, 3.0)  # Time between shots
        self.bullets = arcade.SpriteList()

    def update(self, delta_time=1/60):
        """Update enemy position and behavior."""
        # Update based on enemy type
        if self.enemy_type == "wanderer":
            self._update_wanderer(delta_time)
        elif self.enemy_type == "chaser":
            self._update_chaser(delta_time)
        elif self.enemy_type == "shooter":
            self._update_shooter(delta_time)
        else:
            self._update_wanderer(delta_time)  # Default behavior

        # Update bullets if any
        if hasattr(self, 'bullets'):
            self.bullets.update()
            for bullet in self.bullets:
                if hasattr(bullet, 'update_with_time'):
                    bullet.update_with_time(delta_time)

    def _update_wanderer(self, delta_time):
        """Update wanderer enemy that moves in straight lines and bounces off walls."""
        # Move in current direction
        self.center_x += self.change_x * delta_time
        self.center_y += self.change_y * delta_time

        # Bounce off screen edges
        window = arcade.get_window()
        if self.left < 0:
            self.left = 0
            self.change_x *= -1
            sound_manager.play_sound("enemy", "bounce")
        elif self.right > window.width:
            self.right = window.width
            self.change_x *= -1
            sound_manager.play_sound("enemy", "bounce")

        if self.bottom < 0:
            self.bottom = 0
            self.change_y *= -1
            sound_manager.play_sound("enemy", "bounce")
        elif self.top > window.height:
            self.top = window.height
            self.change_y *= -1
            sound_manager.play_sound("enemy", "bounce")

    def _update_chaser(self, delta_time):
        """Update chaser enemy that follows the player."""
        if self.target:
            # Calculate direction to target
            dx = self.target.center_x - self.center_x
            dy = self.target.center_y - self.center_y
            distance = max(1, math.hypot(dx, dy))

            # Normalize and apply speed
            self.change_x = (dx / distance) * self.speed
            self.change_y = (dy / distance) * self.speed

            # Move towards target
            self.center_x += self.change_x * delta_time
            self.center_y += self.change_y * delta_time

            # Bounce off screen edges
            window = arcade.get_window()
            if self.left < 0:
                self.left = 0
            elif self.right > window.width:
                self.right = window.width

            if self.bottom < 0:
                self.bottom = 0
            elif self.top > window.height:
                self.top = window.height

    def _update_shooter(self, delta_time):
        """Update shooter enemy that moves slowly and shoots at the player."""
        # Move slowly (half speed of wanderer)
        self.center_x += self.change_x * 0.5 * delta_time
        self.center_y += self.change_y * 0.5 * delta_time

        # Bounce off screen edges
        window = arcade.get_window()
        if self.left < 0:
            self.left = 0
            self.change_x *= -1
        elif self.right > window.width:
            self.right = window.width
            self.change_x *= -1

        if self.bottom < 0:
            self.bottom = 0
            self.change_y *= -1
        elif self.top > window.height:
            self.top = window.height
            self.change_y *= -1

        # Shoot at target
        if self.target:
            self.shoot_timer += delta_time
            if self.shoot_timer >= self.fire_rate:
                self.shoot_timer = 0
                self._shoot_at_target()

    def _shoot_at_target(self):
        """Shoot a bullet at the target."""
        if not self.target:
            return

        from src.entities.projectiles.enemy_bullet import EnemyBullet

        # Calculate direction to target
        dx = self.target.center_x - self.center_x
        dy = self.target.center_y - self.center_y
        distance = max(1, math.hypot(dx, dy))

        # Create bullet
        bullet = EnemyBullet(
            self.center_x,
            self.center_y,
            dx / distance,
            dy / distance
        )

        # Add to bullet list
        self.bullets.append(bullet)

        # Play sound
        sound_manager.play_sound("enemy", "shoot")

    def take_damage(self, amount):
        """Take damage and check if dead."""
        self.health -= amount

        # Play hit sound
        sound_manager.play_sound("enemy", "hit")

        if self.health <= 0:
            # Play death sound
            sound_manager.play_sound("enemy", "death")
            return True
        return False
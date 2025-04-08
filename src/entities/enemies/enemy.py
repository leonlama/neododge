import arcade
import math
import random

class Enemy(arcade.Sprite):
    """Enemy character that moves and shoots at the player."""

    def __init__(self, x, y, target=None, enemy_type="chaser"):
        """Initialize the enemy.

        Args:
            x: Initial x position.
            y: Initial y position.
            target: The target to follow (usually the player).
            enemy_type: Type of enemy behavior.
        """
        super().__init__()

        # Set up texture
        try:
            self.texture = arcade.load_texture("assets/images/enemies/enemy.png")
        except:
            # Fallback to a simple shape if texture can't be loaded
            self.texture = arcade.make_soft_circle_texture(30, arcade.color.RED)

        # Set position
        self.center_x = x
        self.center_y = y

        # Set target (usually the player)
        self.target = target

        # Set type and behavior
        self.enemy_type = enemy_type
        self._set_behavior_from_type()

        # Set velocity (random direction)
        speed = random.uniform(100, 150)
        angle = random.uniform(0, 2 * math.pi)
        self.change_x = speed * math.cos(angle)
        self.change_y = speed * math.sin(angle)

        # Movement properties
        self.speed = speed
        self.direction_timer = 0
        self.direction = random.choice([(1, 0), (-1, 0), (0, 1), (0, -1)])

        # Set up bullet firing
        self.shoot_timer = 0
        self.fire_timer = random.uniform(1.0, 3.0)
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
            # Update bullet list (without delta_time)
            self.bullets.update()
            
            # Update each bullet individually with delta_time
            for bullet in self.bullets:
                if hasattr(bullet, 'update_with_time'):
                    bullet.update_with_time(delta_time)

    def update_with_delta(self, delta_time):
        """Update the enemy's position and state with delta time.

        Args:
            delta_time: Time since last update.
        """
        # Update position based on velocity
        self.center_x += self.change_x * delta_time
        self.center_y += self.change_y * delta_time

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

        # Update bullet firing
        self.fire_timer -= delta_time
        if self.fire_timer <= 0:
            self.fire_bullet()
            self.fire_timer = random.uniform(1.0, 3.0)

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
        window = arcade.get_window()
        if self.left < 0:
            self.left = 0
            self.direction = (-self.direction[0], self.direction[1])
        elif self.right > window.width:
            self.right = window.width
            self.direction = (-self.direction[0], self.direction[1])

        if self.bottom < 0:
            self.bottom = 0
            self.direction = (self.direction[0], -self.direction[1])
        elif self.top > window.height:
            self.top = window.height
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

    def fire_bullet(self):
        """Fire a bullet at the player."""
        # Get player position
        window = arcade.get_window()
        view = window.current_view
        if hasattr(view, 'player'):
            player = view.player

            # Calculate direction to player
            dx = player.center_x - self.center_x
            dy = player.center_y - self.center_y
            distance = max(1, math.sqrt(dx*dx + dy*dy))

            # Normalize direction
            dx /= distance
            dy /= distance

            # Create bullet
            bullet = Bullet(self.center_x, self.center_y, dx, dy)

            # Add to bullets list
            self.bullets.append(bullet)

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
        """Update bullet position using default delta time."""
        # Move according to velocity using a default delta time
        self.center_x += self.change_x * 1/60
        self.center_y += self.change_y * 1/60

        # Remove if off-screen
        window = arcade.get_window()
        screen_width, screen_height = window.width, window.height
        if (self.right < 0 or self.left > screen_width or 
            self.bottom > screen_height or self.top < 0):
            self.remove_from_sprite_lists()

    def update_with_time(self, delta_time):
        """Update bullet position with specific delta time."""
        # Move according to velocity
        self.center_x += self.change_x * delta_time
        self.center_y += self.change_y * delta_time

        # Remove if off-screen
        window = arcade.get_window()
        screen_width, screen_height = window.width, window.height
        if (self.right < 0 or self.left > screen_width or 
            self.bottom > screen_height or self.top < 0):
            self.remove_from_sprite_lists()
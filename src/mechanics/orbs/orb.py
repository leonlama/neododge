import arcade
import random
from src.skins.skin_manager import skin_manager
from src.core.constants import SCREEN_WIDTH, SCREEN_HEIGHT

class Orb(arcade.Sprite):
    """Base class for all orbs in the game"""

    def __init__(self, x, y, orb_type="default", is_buff=True):
        super().__init__()

        # Set position
        self.center_x = x
        self.center_y = y

        # Set properties
        self.orb_type = orb_type
        self.is_buff = is_buff
        self.alpha = 255

        # Set up texture using skin manager
        try:
            # Use skin manager to get the texture
            category = "orbs"
            self.texture = skin_manager.get_texture(category, orb_type)

            # Get the scale from skin manager
            self.base_scale = skin_manager.get_orb_scale()
            self.scale = self.base_scale
        except Exception as e:
            print(f"⚠️ Error loading orb texture '{orb_type}': {e}")
            # Fallback to a simple shape
            if is_buff:
                color = arcade.color.GREEN
            else:
                color = arcade.color.RED
            self.texture = arcade.make_circle_texture(30, color)
            self.base_scale = 1.0
            self.scale = 1.0

        # Movement properties
        self.velocity = (random.uniform(-1, 1), random.uniform(-1, 1))
        self.speed = random.uniform(20, 40)

        # Lifetime properties
        self.lifetime = random.uniform(10, 15)  # Orbs disappear after this time
        self.fade_time = 2.0  # Time to fade out before disappearing

        # Set up animation
        self.pulse_scale = 1.0
        self.pulse_direction = 1
        self.pulse_min = 0.9
        self.pulse_max = 1.1
        self.pulse_speed = 1.0

    def set_texture(self):
        """Set the texture based on orb type"""
        # Get texture name based on orb type
        texture_name = self.get_texture_name()

        try:
            # Try to get the texture from the skin manager
            self.texture = skin_manager.get_texture("orbs", texture_name)
            self.scale = skin_manager.get_orb_scale()
        except Exception as e:
            print(f"⚠️ Error loading orb texture '{texture_name}': {e}")
            # If no texture found, create a default one
            color = arcade.color.GREEN if self.is_buff else arcade.color.RED
            self.texture = arcade.make_soft_circle_texture(30, color)
            self.scale = 1.0

    def get_texture_name(self):
        """Get the texture name based on orb type"""
        return self.orb_type

    def update(self, delta_time=1/60):
        """Update the orb's position and lifetime"""
        # Update position
        self.center_x += self.velocity[0] * self.speed * delta_time
        self.center_y += self.velocity[1] * self.speed * delta_time

        # Bounce off screen edges
        if self.left < 0 or self.right > SCREEN_WIDTH:
            self.velocity = (-self.velocity[0], self.velocity[1])
        if self.bottom < 0 or self.top > SCREEN_HEIGHT:
            self.velocity = (self.velocity[0], -self.velocity[1])

        # Update lifetime
        self.lifetime -= delta_time

        # Update pulse animation
        self.pulse_scale += self.pulse_direction * self.pulse_speed * delta_time
        if self.pulse_scale > self.pulse_max:
            self.pulse_scale = self.pulse_max
            self.pulse_direction = -1
        elif self.pulse_scale < self.pulse_min:
            self.pulse_scale = self.pulse_min
            self.pulse_direction = 1

        # Apply pulse scale
        self.scale = self.base_scale * self.pulse_scale

        # Fade out when nearing end of lifetime
        if self.lifetime < self.fade_time:
            # Ensure alpha is between 0 and 255
            alpha_value = max(0, min(255, int(255 * (self.lifetime / self.fade_time))))
            self.alpha = alpha_value

        # Remove when lifetime is over or very close to it
        if self.lifetime <= 0.01:  # Small buffer to prevent negative values
            self.remove_from_sprite_lists()

    def apply_effect(self, player):
        """Apply the orb's effect to the player - to be implemented by subclasses"""
        pass
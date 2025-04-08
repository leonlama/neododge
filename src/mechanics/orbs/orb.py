import arcade
import random
from src.core.constants import SCREEN_WIDTH, SCREEN_HEIGHT

class Orb(arcade.Sprite):
    """Base class for all orbs in the game"""

    def __init__(self, x, y, orb_type="default"):
        super().__init__()

        # Set position
        self.center_x = x
        self.center_y = y

        # Set properties
        self.orb_type = orb_type
        self.scale = 0.5
        self.alpha = 255

        # Movement properties
        self.velocity = (random.uniform(-1, 1), random.uniform(-1, 1))
        self.speed = random.uniform(20, 40)

        # Lifetime properties
        self.lifetime = random.uniform(10, 15)  # Orbs disappear after this time
        self.fade_time = 2.0  # Time to fade out before disappearing

        # Set texture based on orb type
        self.set_texture()

    def set_texture(self):
        """Set the texture based on orb type - to be implemented by subclasses"""
        # Default texture is a colored circle
        self.texture = arcade.make_circle_texture(
            32, 
            arcade.color.WHITE, 
            soft=True
        )

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

        # Fade out when nearing end of lifetime
        if self.lifetime < self.fade_time:
            self.alpha = int(255 * (self.lifetime / self.fade_time))

        # Remove when lifetime is over
        if self.lifetime <= 0:
            self.remove_from_sprite_lists()

    def apply_effect(self, player):
        """Apply the orb's effect to the player - to be implemented by subclasses"""
        pass
import arcade
import math
import random
from scripts.enemies.base_enemy import BaseEnemy
from src.core.resource_manager import resource_path

class ChaserEnemy(BaseEnemy):
    """An enemy that chases the player."""

    def __init__(self, x, y, scale=1.0):
        super().__init__(x, y, scale)

        # Set texture
        try:
            self.texture = arcade.load_texture(resource_path("assets/images/enemies/chaser.png"))
        except:
            # Fallback texture
            self.texture = arcade.make_soft_square_texture(30, arcade.color.BLUE, outer_alpha=255)

        # Movement
        self.speed = 3.0
        self.behavior_type = "chase"

        # Combat
        self.health = 2
        self.damage = 1
        self.can_shoot = False

    def _chase_behavior(self):
        """Chase the player."""
        # Get player from the game view
        if not self.game_view or not self.game_view.player:
            return

        player = self.game_view.player

        # Calculate direction to player
        dx = player.center_x - self.center_x
        dy = player.center_y - self.center_y
        distance = math.sqrt(dx*dx + dy*dy)

        # Move towards player
        if distance > 0:
            self.change_x = dx / distance * self.speed
            self.change_y = dy / distance * self.speed

        # Update position
        self.center_x += self.change_x
        self.center_y += self.change_y

import random
from scripts.mechanics.orbs.orb_pool import get_random_orb
from arcade import Sprite
import arcade

class DashArtifactPickup(Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.texture = arcade.make_soft_circle_texture(18, arcade.color.YELLOW, outer_alpha=255)
        self.center_x = x
        self.center_y = y
        self.name = "DashPickup"  # to identify it later

def spawn_random_orb(screen_width, screen_height):
    x = random.randint(50, screen_width - 50)
    y = random.randint(50, screen_height - 50)
    return get_random_orb(x, y)

def spawn_dash_artifact(screen_width, screen_height):
    x = random.randint(50, screen_width - 50)
    y = random.randint(50, screen_height - 50)
    return DashArtifactPickup(x, y)
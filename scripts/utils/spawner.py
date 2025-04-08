import random
from scripts.mechanics.orbs.orb_pool import get_random_orb
from arcade import Sprite
import arcade
from scripts.mechanics.artifacts.dash_artifact import DashArtifact

def spawn_random_orb(screen_width, screen_height):
    x = random.randint(50, screen_width - 50)
    y = random.randint(50, screen_height - 50)
    return get_random_orb(x, y)

def spawn_dash_artifact(screen_width, screen_height):
    x = random.randint(50, screen_width - 50)
    y = random.randint(50, screen_height - 50)
    return DashArtifact(x, y)

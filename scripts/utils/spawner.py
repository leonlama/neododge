import random
from scripts.mechanics.orbs.buff_orbs import BuffOrb
from scripts.mechanics.orbs.debuff_orbs import DebuffOrb
from scripts.mechanics.artifacts.dash_artifact import DashArtifact

def spawn_random_orb(screen_width, screen_height):
    x = random.randint(50, screen_width - 50)
    y = random.randint(50, screen_height - 50)
    return random.choice([BuffOrb(x, y), DebuffOrb(x, y)])

def spawn_dash_artifact(screen_width, screen_height):
    x = random.randint(50, screen_width - 50)
    y = random.randint(50, screen_height - 50)
    return DashArtifact(x, y)
import random
from scripts.mechanics.orbs.buff_orbs import BuffOrb
from scripts.mechanics.orbs.debuff_orbs import DebuffOrb
from scripts.mechanics.artifacts.artifacts import DashArtifact
from scripts.utils.constants import SCREEN_WIDTH, SCREEN_HEIGHT

def spawn_random_orb():
    x = random.randint(50, SCREEN_WIDTH - 50)
    y = random.randint(50, SCREEN_HEIGHT - 50)
    orb_cls = random.choice([BuffOrb, DebuffOrb])
    return orb_cls(x, y)

def spawn_dash_artifact():
    x = random.randint(50, SCREEN_WIDTH - 50)
    y = random.randint(50, SCREEN_HEIGHT - 50)
    return DashArtifact(x, y)
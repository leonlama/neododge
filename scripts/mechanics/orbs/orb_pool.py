import random
from scripts.mechanics.orbs.buff_orbs import BuffOrb
from scripts.mechanics.orbs.debuff_orbs import DebuffOrb


# Define all orb types you want to use
BUFF_ORBS = [
    "gray",
    "red",
    "gold",
    "speed_10",
    "speed_20",
    "speed_35",
    "mult_1_5",
    "mult_2",
    "cooldown",
    "shield",
]

DEBUFF_ORBS = [
    "slow",
    "mult_down_0_5",
    "mult_down_0_25",
    "cooldown_up",
    #"inverse_move",
    "vision_blur",
    "big_hitbox"
]


def get_random_orb(x: float, y: float):
    """Return a randomly selected BuffOrb (80%) or DebuffOrb (20%)."""
    is_debuff = random.choices([False, True], weights=[4, 1])[0]

    if is_debuff:
        orb_type = random.choice(DEBUFF_ORBS)
        return DebuffOrb(x, y, orb_type=orb_type)
    else:
        orb_type = random.choice(BUFF_ORBS)
        return BuffOrb(x, y, orb_type=orb_type)

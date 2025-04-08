import random
from src.mechanics.orbs.buff_orbs import BuffOrb
from src.mechanics.orbs.debuff_orbs import DebuffOrb

# Define orb pools with weights
BUFF_ORBS = {
    "speed_10": 30,
    "speed_20": 20,
    "speed_35": 10,
    "mult_1_5": 25,
    "mult_2": 15,
    "cooldown": 20,
    "shield": 10
}

DEBUFF_ORBS = {
    "slow": 30,
    "mult_down_0_5": 25,
    "mult_down_0_25": 15,
    "cooldown_up": 20,
    "vision_blur": 15,
    "big_hitbox": 15
}

def get_random_orb(x, y, buff_chance=0.7):
    """Generate a random orb at the given position

    Args:
        x (float): X position
        y (float): Y position
        buff_chance (float): Probability of generating a buff orb (0.0 to 1.0)

    Returns:
        Orb: A randomly generated orb
    """
    # Determine if it's a buff or debuff orb
    is_buff = random.random() < buff_chance

    if is_buff:
        # Select a random buff orb type based on weights
        orb_types = list(BUFF_ORBS.keys())
        weights = list(BUFF_ORBS.values())
        orb_type = random.choices(orb_types, weights=weights, k=1)[0]
        return BuffOrb(x, y, orb_type)
    else:
        # Select a random debuff orb type based on weights
        orb_types = list(DEBUFF_ORBS.keys())
        weights = list(DEBUFF_ORBS.values())
        orb_type = random.choices(orb_types, weights=weights, k=1)[0]
        return DebuffOrb(x, y, orb_type)
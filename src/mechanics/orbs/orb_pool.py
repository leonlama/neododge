import random
import arcade
from src.mechanics.orbs.buff_orbs import BuffOrb
from src.mechanics.orbs.debuff_orbs import DebuffOrb
from src.core.scaling import get_scale

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

class Orb(arcade.Sprite):
    def __init__(self, x, y, orb_type):
        super().__init__()
        self.center_x = x
        self.center_y = y
        self.orb_type = orb_type
        
        # Set scale using centralized system
        self.scale = get_scale('orb')

def get_random_orb(x, y, context=None):
    """Generate a random orb at the given position

    Args:
        x (float): X position
        y (float): Y position
        context (dict, optional): Dictionary with game context like 'wave', 'hp', 'mult', etc.

    Returns:
        Orb: A randomly generated orb
    """
    # Default to buff-heavy balance
    base_buff_chance = 0.65

    if context:
        wave = context.get("wave", 1)
        player_hp = context.get("hp", 3)
        multiplier = context.get("mult", 1.0)

        # More debuffs as waves progress
        base_buff_chance -= 0.05 * (wave // 5)

        # More buffs when health is low
        if player_hp <= 1:
            base_buff_chance += 0.25

        # Confuse the player with more speed/slow orbs when multiplier is high
        if multiplier > 1.5:
            BUFF_ORBS["speed_20"] += 10
            DEBUFF_ORBS["slow"] += 10

        # Clamp chance
        base_buff_chance = max(0.3, min(0.9, base_buff_chance))

    is_buff = random.random() < base_buff_chance

    if is_buff:
        orb_type = random.choices(list(BUFF_ORBS), weights=BUFF_ORBS.values(), k=1)[0]
        return BuffOrb(x, y, orb_type)
    else:
        orb_type = random.choices(list(DEBUFF_ORBS), weights=DEBUFF_ORBS.values(), k=1)[0]
        return DebuffOrb(x, y, orb_type)
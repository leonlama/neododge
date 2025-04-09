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
    """
    Get a random orb based on the current game context.

    Args:
        x (float): X position for the orb
        y (float): Y position for the orb
        context (dict): Game context information (wave, player stats, etc.)

    Returns:
        Orb: A randomly selected orb instance
    """
    # Default context if none provided
    if context is None:
        context = {}

    # Extract context variables with defaults
    wave = context.get('wave', 1)  # Default to wave 1 if not provided
    player_health = context.get('player_health', 3)
    player_speed = context.get('player_speed', 1.0)

    # Base chances for different orb types
    base_buff_chance = 0.7  # 70% chance for buff orbs

    # Adjust chances based on wave number
    if wave is not None:
        base_buff_chance -= 0.05 * (wave // 5)

    # Adjust chances based on player health
    if player_health <= 1:
        base_buff_chance += 0.2  # More likely to get buffs when low health

    # Clamp chance to reasonable range
    base_buff_chance = max(0.3, min(0.9, base_buff_chance))

    # Determine if this will be a buff or debuff orb
    is_buff = random.random() < base_buff_chance

    if is_buff:
        orb_type = random.choices(list(BUFF_ORBS), weights=BUFF_ORBS.values(), k=1)[0]
        return BuffOrb(x, y, orb_type)
    else:
        orb_type = random.choices(list(DEBUFF_ORBS), weights=DEBUFF_ORBS.values(), k=1)[0]
        return DebuffOrb(x, y, orb_type)
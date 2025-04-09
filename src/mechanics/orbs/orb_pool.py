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
    """Get a random orb based on game context."""
    if context is None:
        context = {}

    # Extract context variables with defaults
    wave_number = context.get('wave', 1)
    if isinstance(wave_number, dict):
        # If wave is a dictionary (like a wave configuration), extract the wave number
        wave_number = wave_number.get('wave_number', 1)

    player_health = context.get('player_health', 3)
    max_player_health = context.get('max_player_health', 3)
    score = context.get('score', 0)

    # Base chance for buff vs debuff
    base_buff_chance = 0.7

    # Adjust based on wave number (higher waves = more debuffs)
    if isinstance(wave_number, (int, float)):
        base_buff_chance -= 0.05 * (wave_number // 5)

    # Adjust based on player health (lower health = more buffs)
    health_ratio = player_health / max_player_health
    if health_ratio < 0.3:
        base_buff_chance += 0.2
    elif health_ratio < 0.6:
        base_buff_chance += 0.1

    # Determine if buff or debuff
    is_buff = random.random() < base_buff_chance

    # Get appropriate orb
    if is_buff:
        return get_random_buff_orb(x, y, context)
    else:
        return get_random_debuff_orb(x, y, context)

def get_random_buff_orb(x, y, context=None):
    """Get a random buff orb."""
    if context is None:
        context = {}

    # List of possible buff orbs with weights
    buff_types = {
        "speed_10": 30,
        "health": 20,
        "shield": 15,
        "score_2x": 25,
        "invincible": 10
    }

    # Adjust weights based on context
    player_health = context.get('player_health', 3)
    max_player_health = context.get('max_player_health', 3)

    # If player health is low, increase chance of health and shield
    if player_health / max_player_health < 0.5:
        buff_types["health"] += 15
        buff_types["shield"] += 10
        buff_types["invincible"] += 5

    # Choose a buff type based on weights
    buff_type = random.choices(
        list(buff_types.keys()),
        weights=list(buff_types.values())
    )[0]

    # Create the orb
    from src.mechanics.orbs.buff_orbs import BuffOrb
    return BuffOrb(x, y, buff_type)

def get_random_debuff_orb(x, y, context=None):
    """Get a random debuff orb."""
    if context is None:
        context = {}

    # List of possible debuff orbs with weights
    debuff_types = {
        "slow": 35,
        "reverse": 25,
        "blind": 20,
        "confusion": 15,
        "score_0.5x": 5
    }

    # Adjust weights based on context
    wave_number = context.get('wave', 1)
    if isinstance(wave_number, dict):
        wave_number = wave_number.get('wave_number', 1)

    # Higher waves get more severe debuffs
    if isinstance(wave_number, (int, float)) and wave_number > 5:
        debuff_types["blind"] += 5
        debuff_types["confusion"] += 5
        debuff_types["score_0.5x"] += 5

    # Choose a debuff type based on weights
    debuff_type = random.choices(
        list(debuff_types.keys()),
        weights=list(debuff_types.values())
    )[0]

    # Create the orb
    from src.mechanics.orbs.debuff_orbs import DebuffOrb
    return DebuffOrb(x, y, debuff_type)
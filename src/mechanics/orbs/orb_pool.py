import random
from scripts.mechanics.orbs.buff_orbs import BuffOrb
from scripts.mechanics.orbs.debuff_orbs import DebuffOrb
from scripts.skins.skin_manager import skin_manager
from scripts.utils.orb_utils import get_texture_name_from_orb_type

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
    "vision",
    "hitbox"
]


def get_random_orb(x: float, y: float):
    """Return a randomly selected BuffOrb (80%) or DebuffOrb (20%)."""
    is_debuff = random.choices([False, True], weights=[4, 1])[0]

    if is_debuff:
        orb_type = random.choice(DEBUFF_ORBS)
        orb = DebuffOrb(x, y, orb_type=orb_type)
        texture_name = get_texture_name_from_orb_type(orb_type)
        orb.texture = skin_manager.get_texture("orbs", texture_name)
        orb.scale = skin_manager.get_orb_scale()
        return orb
    else:
        orb_type = random.choice(BUFF_ORBS)
        orb = BuffOrb(x, y, orb_type=orb_type)
        texture_name = get_texture_name_from_orb_type(orb_type)
        orb.texture = skin_manager.get_texture("orbs", texture_name)
        orb.scale = skin_manager.get_orb_scale()
        return orb


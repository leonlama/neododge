from scripts.orbs.buff_orbs import BuffOrb
from scripts.orbs.debuff_orbs import DebuffOrb

def Orb(x, y, orb_type="gray"):
    if orb_type.startswith("debuff"):
        return DebuffOrb(x, y, orb_type)
    else:
        return BuffOrb(x, y, orb_type)
# scripts/utils/orb_utils.py

def get_texture_name_from_orb_type(orb_type: str) -> str:
    if "mult" in orb_type:
        return "multiplier"
    if "cool" in orb_type:
        return "cooldown"
    if "speed" in orb_type or "slow" in orb_type:
        return "speed"
    if "shield" in orb_type:
        return "shield"
    if "vision" in orb_type:
        return "vision"
    if "hitbox" in orb_type:
        return "hitbox"
    return "multiplier"


"""
Centralized scaling system for game entities.
"""

# Default scale values
DEFAULT_SCALES = {
    'player': 0.035,
    'enemy': 0.035,  # Updated to match player
    'bullet': 0.035,
    'orb': 0.1,
    'artifact': 0.1,
    'coin': 1,
    'heart': 1
}

# Current scale values (can be modified at runtime)
scales = DEFAULT_SCALES.copy()

def get_scale(entity_type):
    """Get the scale for a specific entity type.

    Args:
        entity_type: The type of entity (player, enemy, etc.)

    Returns:
        float: The scale value for the entity type
    """
    return scales.get(entity_type, 1.0)

def set_scale(entity_type, value):
    """Set the scale for a specific entity type.

    Args:
        entity_type: The type of entity (player, enemy, etc.)
        value: The scale value to set
    """
    scales[entity_type] = value

def reset_scales():
    """Reset all scales to default values."""
    global scales
    scales = DEFAULT_SCALES.copy()

def apply_scale_to_sprite(sprite, entity_type):
    """Apply the appropriate scale to a sprite.

    Args:
        sprite: The sprite to scale
        entity_type: The type of entity
    """
    sprite.scale = get_scale(entity_type)
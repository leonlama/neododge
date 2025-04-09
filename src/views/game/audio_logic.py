import arcade
from src.audio.sound_manager import sound_manager

def play_coin_sound(self):
    """Play the coin pickup sound."""
    try:
        sound_manager.play_sound("coin", "collect")
    except Exception as e:
        print(f"Error playing coin sound: {e}")

def play_damage_sound(self):
    """Play the damage sound."""
    # Check if player has damage sound cooldown
    if hasattr(self.player, 'damage_sound_cooldown') and self.player.damage_sound_cooldown:
        return

    try:
        # Always use the sound manager for consistent volume control
        sound_manager.play_sound("player", "damage")

        # Set cooldown
        self.player.damage_sound_cooldown = True

        # Reset cooldown after a short delay
        arcade.schedule(self.reset_damage_sound_cooldown, 0.5)
    except Exception as e:
        print(f"Error playing damage sound: {e}")

def play_buff_sound(self):
    """Play the buff pickup sound."""
    try:
        sound_manager.play_sound("orb", "buff")
    except Exception as e:
        print(f"Error playing buff sound: {e}")

def play_debuff_sound(self):
    """Play the debuff pickup sound."""
    try:
        sound_manager.play_sound("orb", "debuff")
    except Exception as e:
        print(f"Error playing debuff sound: {e}")

def setup_sounds(self):
    """Set up game sounds."""
    # We'll use the sound manager instead of loading sounds directly
    pass
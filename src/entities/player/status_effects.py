import arcade
import time
import uuid

class StatusEffect:
    """Base class for player status effects."""

    def __init__(self, duration=5.0, effect_type="generic"):
        self.duration = duration
        self.remaining_time = duration
        self.active = True
        self.effect_type = effect_type

        # For visual representation
        self.icon = None
        self.color = arcade.color.WHITE

    def update(self, delta_time):
        """Update the status effect."""
        if self.active:
            self.remaining_time -= delta_time
            if self.remaining_time <= 0:
                self.deactivate()
                return True  # Effect expired
        return False  # Effect still active

    def activate(self, player):
        """Apply the effect to the player."""
        self.active = True
        self.apply(player)

    def deactivate(self):
        """Deactivate the effect."""
        self.active = False

    def apply(self, player):
        """Apply the effect to the player. Override in subclasses."""
        pass

    def remove(self, player):
        """Remove the effect from the player. Override in subclasses."""
        pass

    def get_remaining_percentage(self):
        """Get the percentage of time remaining for this effect."""
        if self.duration <= 0:
            return 0
        return max(0, min(1, self.remaining_time / self.duration))

    def get_formatted_time(self):
        """Get a formatted string of the remaining time."""
        if self.remaining_time >= 10:
            return f"{int(self.remaining_time)}s"
        else:
            return f"{self.remaining_time:.1f}s"


class SpeedEffect(StatusEffect):
    def __init__(self, duration=5.0, bonus_percentage=20):
        super().__init__(duration, "speed")
        self.bonus_percentage = bonus_percentage
        self.color = arcade.color.BLUE

    def apply(self, player):
        player.speed_bonus += self.bonus_percentage / 100

    def remove(self, player):
        player.speed_bonus -= self.bonus_percentage / 100

class ShieldEffect(StatusEffect):
    def __init__(self, duration=5.0):
        super().__init__(duration, "shield")
        self.color = arcade.color.CYAN

    def apply(self, player):
        player.shield_active = True

    def remove(self, player):
        player.shield_active = False

class MultiplierEffect(StatusEffect):
    def __init__(self, duration=5.0, multiplier=1.5):
        super().__init__(duration, "multiplier")
        self.multiplier = multiplier
        self.color = arcade.color.YELLOW

    def apply(self, player):
        player.multiplier *= self.multiplier

    def remove(self, player):
        player.multiplier /= self.multiplier

class SlowEffect(StatusEffect):
    def __init__(self, duration=5.0):
        super().__init__(duration, "slow")
        self.color = arcade.color.PURPLE

    def apply(self, player):
        player.speed_bonus *= 0.5

    def remove(self, player):
        player.speed_bonus *= 2.0

class VisionEffect(StatusEffect):
    def __init__(self, duration=5.0):
        super().__init__(duration, "vision")
        self.color = arcade.color.GRAY

    def apply(self, player):
        # Set a flag for vision blur effect
        player.vision_blurred = True

    def remove(self, player):
        player.vision_blurred = False

class HitboxEffect(StatusEffect):
    def __init__(self, duration=5.0):
        super().__init__(duration, "hitbox")
        self.color = arcade.color.RED

    def apply(self, player):
        # Increase hitbox size
        player.hitbox_multiplier = 1.5
        player.update_hitbox()

    def remove(self, player):
        # Reset hitbox size
        player.hitbox_multiplier = 1.0
        player.update_hitbox()

# Mapping from orb effect types to icon names
EFFECT_ICON_MAP = {
    "speed_10": "speed",
    "speed_20": "speed",
    "speed_35": "speed",
    "mult_1_5": "multiplier",
    "mult_2": "multiplier",
    "mult_down_0_5": "multiplier",
    "mult_down_0_25": "multiplier",
    "cooldown": "cooldown",
    "cooldown_up": "cooldown",
    "shield": "shield",
    "slow": "speed",
    "vision_blur": "vision",
    "big_hitbox": "hitbox"
}

class StatusEffectManager:
    """Manages player status effects."""

    def __init__(self, player):
        self.player = player
        self.effects = {}  # effect_id -> effect instance

        # For UI display
        self.icon_textures = {}
        self.load_icons()

    def load_icons(self):
        """Load icon textures for status effects."""
        from src.skins.skin_manager import skin_manager
        # Try to load icons for each effect type
        effect_types = ["speed", "shield", "multiplier", "vision", "hitbox", "cooldown"]
        for effect_type in effect_types:
            texture = skin_manager.get_texture("ui", f"effects/{effect_type}")
            if texture:
                self.icon_textures[effect_type] = texture

    def add_effect(self, effect_type, duration, data=None):
        """Add or refresh an effect with optional extra data."""
        effect_id = f"{effect_type}_{uuid.uuid4().hex[:6]}"  # fix: unique ID
        
        if data is None:
            data = {}
            
        self.effects[effect_id] = {
            "type": effect_type,
            "remaining": duration,
            "active": True,
            "data": data
        }
        
        return True

    def update(self, delta_time):
        """Update all effects, reducing time and cleaning up expired ones."""
        for effect_id, effect in list(self.effects.items()):  # ✅ copy for safe removal
            effect["remaining"] -= delta_time
            if effect["remaining"] <= 0:
                effect["active"] = False
                del self.effects[effect_id]
            
    def get_total_value(self, effect_type: str) -> float:
        """Get the total value of all active effects of a specific type."""
        total = 0
        for effect in self.effects.values():
            if effect["active"] and effect["type"] == effect_type:
                total += effect["data"].get("value", 0)
        return total

    def get_active_effects_summary(self):
        """Get a summary of all active effects with their aggregated values."""
        summary = {}
        
        for effect_id, effect_data in self.effects.items():
            if effect_data["active"] and effect_data["remaining"] > 0:
                effect_type = effect_data["type"]
                value = effect_data["data"].get("value", 0)
                
                if effect_type in summary:
                    summary[effect_type] += value
                else:
                    summary[effect_type] = value
                    
        return summary

    def get_active_effects(self):
        """Get all currently active effects."""
        return [effect for effect in self.effects.values() if effect["active"]]

    def get_aggregated_effects(self):
        """Aggregate values by type, used for HUD display."""
        totals = {}
        for effect in self.effects.values():
            if effect["active"]:
                effect_type = effect["type"]
                if effect_type not in totals:
                    totals[effect_type] = {
                        "value": effect["data"].get("value", 0),
                        "remaining": effect["remaining"],
                        "icon": self.icon_textures.get(effect_type)
                    }
                else:
                    totals[effect_type]["value"] += effect["data"].get("value", 0)
        return totals

    def draw_effect_indicators(self, screen_width, screen_height):
        """Draw status effect indicators on screen."""
        # Add debug print
        #print(f"Drawing effects: {[effect['type'] for effect in self.effects.values()]}")

        if not self.effects:
            return

        # Configuration for effect display
        icon_size = 40
        spacing = 10
        start_x = screen_width - icon_size - spacing
        start_y = screen_height - icon_size - spacing

        # Draw each active effect
        for i, (effect_id, effect) in enumerate(self.effects.items()):
            if not effect["active"]:
                continue
                
            y_pos = start_y - (icon_size + spacing) * i

            # Black circle background removed as requested

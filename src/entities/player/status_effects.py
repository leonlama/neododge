import arcade
import time

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
        effect_types = ["speed", "shield", "multiplier", "slow", "vision", "hitbox"]
        for effect_type in effect_types:
            texture = skin_manager.get_texture("ui/effects", effect_type)
            if texture:
                self.icon_textures[effect_type] = texture

    def add_effect(self, effect_type, duration=None, effect_data=None):
        """Add or refresh an effect with optional extra data."""
        effect_id = f"{effect_type}_{int(time.time() * 1000)}"
        
        if effect_data is None:
            effect_data = {}
            
        self.effects[effect_id] = {
            "type": effect_type,
            "duration": duration,
            "remaining": duration,
            "value": effect_data.get("value", 0) if effect_data else 0,
            "color": effect_data.get("color", (255, 255, 255)) if effect_data else (255, 255, 255),
            "icon": effect_data.get("icon", None) if effect_data else None,
            "active": True,
        }
        
        return True

    def update(self, delta_time):
        """Update all effects, reducing time and cleaning up expired ones."""
        expired_keys = []
        for effect_id, effect in self.effects.items():
            effect["remaining"] -= delta_time
            if effect["remaining"] <= 0:
                expired_keys.append(effect_id)

        for key in expired_keys:
            del self.effects[key]

    def get_active_effects(self):
        """Get all currently active effects."""
        return [effect for effect in self.effects.values() if effect["active"]]

    def get_aggregated_effects(self):
        """Aggregate values by type, used for HUD display."""
        totals = {}
        for effect in self.effects.values():
            if effect["active"]:
                if effect["type"] not in totals:
                    totals[effect["type"]] = {
                        "value": effect["value"],
                        "color": effect["color"],
                        "icon": effect["icon"]
                    }
                else:
                    totals[effect["type"]]["value"] += effect["value"]
        return totals

    def draw_effect_indicators(self, screen_width, screen_height):
        """Draw status effect indicators on screen."""
        # Add debug print
        print(f"Drawing effects: {[effect['type'] for effect in self.effects.values()]}")

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

            # Draw icon background
            arcade.draw_circle_filled(
                start_x - icon_size/2, 
                y_pos - icon_size/2,
                icon_size/2 + 2,  # Slightly larger than icon
                arcade.color.BLACK
            )

            # Draw icon
            effect_type = effect["type"]
            if effect_type in self.icon_textures:
                arcade.draw_texture_rectangle(
                    start_x - icon_size/2,
                    y_pos - icon_size/2,
                    icon_size, icon_size,
                    self.icon_textures[effect_type]
                )
            else:
                # Fallback if no texture
                arcade.draw_circle_filled(
                    start_x - icon_size/2,
                    y_pos - icon_size/2,
                    icon_size/2,
                    effect["color"]
                )

            # Draw remaining time text
            remaining_time = effect["remaining"]
            formatted_time = f"{int(remaining_time)}s" if remaining_time >= 10 else f"{remaining_time:.1f}s"
            arcade.draw_text(
                formatted_time,
                start_x - icon_size,
                y_pos - icon_size/2 - 15,
                arcade.color.WHITE,
                font_size=12,
                anchor_x="center"
            )

            # Draw duration bar
            bar_width = icon_size
            bar_height = 5
            remaining_pct = max(0, min(1, effect["remaining"] / effect["duration"]))

            # Background bar
            arcade.draw_rectangle_filled(
                start_x - icon_size/2,
                y_pos - icon_size,
                bar_width, bar_height,
                arcade.color.GRAY
            )

            # Remaining time bar
            if remaining_pct > 0:
                arcade.draw_rectangle_filled(
                    start_x - icon_size/2 - (bar_width/2) * (1 - remaining_pct),
                    y_pos - icon_size,
                    bar_width * remaining_pct, bar_height,
                    effect["color"]
                )
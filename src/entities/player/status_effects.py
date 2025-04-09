import arcade

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
        self.effects = {}  # effect_type -> effect instance

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

    def add_effect(self, effect_type, duration=None, **kwargs):
        """Add a status effect to the player."""
        print(f"StatusEffectManager.add_effect called with: {effect_type}, {duration}, {kwargs}")

        # Create the effect based on type
        effect = None

        if effect_type == "speed":
            effect = SpeedEffect(duration or 5.0, 20)  # 20% speed boost
        elif effect_type == "shield":
            effect = ShieldEffect(duration or 5.0)
        elif effect_type == "multiplier":
            effect = MultiplierEffect(duration or 5.0, 1.5)  # 1.5x multiplier
        elif effect_type == "slow":
            effect = SlowEffect(duration or 5.0)
        elif effect_type == "vision":
            effect = VisionEffect(duration or 5.0)
        elif effect_type == "hitbox":
            effect = HitboxEffect(duration or 5.0)

        # If we created an effect, apply and store it
        if effect:
            print(f"Created effect: {effect_type}")

            # If this effect already exists, remove it first
            if effect_type in self.effects:
                old_effect = self.effects[effect_type]
                old_effect.remove(self.player)

                # If new effect has longer duration, use that, otherwise keep remaining time
                if duration and duration > old_effect.remaining_time:
                    effect.remaining_time = duration
                else:
                    effect.remaining_time = old_effect.remaining_time

            # Apply the effect
            effect.activate(self.player)

            # Store the effect
            self.effects[effect_type] = effect

            print(f"Active effects after adding: {list(self.effects.keys())}")
            return True

        print(f"Failed to create effect for type: {effect_type}")
        return False

    def update(self, delta_time):
        """Update all status effects."""
        expired_effects = []

        for effect_type, effect in self.effects.items():
            if effect.update(delta_time):  # Effect expired
                effect.remove(self.player)
                expired_effects.append(effect_type)

        # Remove expired effects
        for effect_type in expired_effects:
            del self.effects[effect_type]

    def draw_effect_indicators(self, screen_width, screen_height):
        """Draw status effect indicators on screen."""
        # Add debug print
        print(f"Drawing effects: {list(self.effects.keys())}")

        if not self.effects:
            return

        # Configuration for effect display
        icon_size = 40
        spacing = 10
        start_x = screen_width - icon_size - spacing
        start_y = screen_height - icon_size - spacing

        # Draw each active effect
        for i, (effect_type, effect) in enumerate(self.effects.items()):
            y_pos = start_y - (icon_size + spacing) * i

            # Draw icon background
            arcade.draw_circle_filled(
                start_x - icon_size/2, 
                y_pos - icon_size/2,
                icon_size/2 + 2,  # Slightly larger than icon
                arcade.color.BLACK
            )

            # Draw icon
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
                    effect.color
                )

            # Draw remaining time text
            arcade.draw_text(
                effect.get_formatted_time(),
                start_x - icon_size,
                y_pos - icon_size/2 - 15,
                arcade.color.WHITE,
                font_size=12,
                anchor_x="center"
            )

            # Draw duration bar
            bar_width = icon_size
            bar_height = 5
            remaining_pct = effect.get_remaining_percentage()

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
                    effect.color
                )
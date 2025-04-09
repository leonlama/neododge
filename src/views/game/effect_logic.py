import arcade
from src.ui.pickup_text import PickupText

def add_effect(self, effect_type, duration=None, value=None, is_percentage=True, color=None, icon_name=None):
        """Adds an effect with full flexibility."""
        # Apply the effect to the player
        if hasattr(self.player, 'apply_effect'):
            self.player.apply_effect(effect_type, value, duration, is_percentage)

        # Add a visual indicator
        if hasattr(self, 'effect_indicators'):
            self.effect_indicators.append({
                'type': effect_type,
                'value': value,
                'duration': duration,
                'is_percentage': is_percentage,
                'color': color,
                'icon': icon_name
            })

def apply_buff(self, buff_type, amount):
        """Apply a buff to the player.

        Args:
            buff_type: Type of buff (speed, health, damage)
            amount: Amount to buff (0.2 = 20% increase)
        """
        print(f"Applying {buff_type} buff: +{amount*100:.0f}%")

        if buff_type == "speed":
            # Increase player speed
            self.player.speed_multiplier = self.player.speed_multiplier * (1 + amount)
            print(f"Player speed now: {self.player.speed_multiplier:.2f}x")

        elif buff_type == "health":
            # Increase player max health
            old_max = self.player.max_health
            self.player.max_health = int(self.player.max_health * (1 + amount))
            # Also heal the player by the amount gained
            health_gained = self.player.max_health - old_max
            self.player.health = min(self.player.max_health, self.player.health + health_gained)
            print(f"Player health now: {self.player.health}/{self.player.max_health}")

        elif buff_type == "damage":
            # Increase player damage
            if hasattr(self.player, 'damage_multiplier'):
                self.player.damage_multiplier = self.player.damage_multiplier * (1 + amount)
            else:
                self.player.damage_multiplier = 1 + amount
            print(f"Player damage now: {self.player.damage_multiplier:.2f}x")

        # Update UI to show new buff
        self.update_buff_display()

def update_buff_display(self):
        """Update the buff display in the UI."""
        # Create buff text to display
        buff_text = []

        if hasattr(self.player, 'speed_boost_timer') and self.player.speed_boost_timer > 0:
            buff_text.append(f"Speed: +50% ({self.player.speed_boost_timer:.1f}s)")

        if hasattr(self.player, 'slow_timer') and self.player.slow_timer > 0:
            buff_text.append(f"Slow: -50% ({self.player.slow_timer:.1f}s)")

        if hasattr(self.player, 'shield_timer') and self.player.shield_timer > 0:
            buff_text.append(f"Shield: Active ({self.player.shield_timer:.1f}s)")

        if hasattr(self.player, 'invincibility_timer') and self.player.invincibility_timer > 0:
            buff_text.append(f"Invincible: ({self.player.invincibility_timer:.1f}s)")

        # Store buff text for drawing in on_draw
        self.buff_display_text = buff_text

def show_pickup_text(self, text, color=arcade.color.WHITE, x=None, y=None):
        if x is None or y is None:
            x, y = self.player.center_x, self.player.center_y + 30
        text_obj = arcade.Text(text, x, y, color, font_size=12, anchor_x="center")
        self.pickup_texts.append(text_obj)

def add_pickup_text(self, text, x, y):
        """Add floating text for item pickups."""
        if not hasattr(self, 'pickup_texts'):
            self.pickup_texts = []

        # Add text with position and lifetime
        self.pickup_texts.append(PickupText(text, x, y))  # 1.0 second lifetime
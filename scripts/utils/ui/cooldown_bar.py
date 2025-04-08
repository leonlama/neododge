import arcade
from scripts.utils.constants import DASH_COOLDOWN

class CooldownBar:
    def __init__(self, label: str, x: float, y: float, width: float, height: float):
        self.label = label
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.cooldown = DASH_COOLDOWN  # Default full cooldown (in seconds)
        self.timer = 0.0     # Time since last use

    def reset(self):
        """Reset the timer to 0 (just used)"""
        self.timer = 0.0

    def update(self, delta_time: float):
        """Increment the timer by delta_time"""
        if self.timer < self.cooldown:
            self.timer += delta_time

    def set_cooldown(self, cooldown: float):
        """Set the total cooldown time"""
        self.cooldown = cooldown

    def set_progress(self, fraction: float):
        """Set the progress of the cooldown bar directly (0.0 to 1.0)"""
        self.timer = self.cooldown * fraction

    def draw(self):
        """Draw the cooldown bar with the specified visual style"""
        # Calculate progress percentage (0.0 to 1.0)
        progress = min(self.timer / self.cooldown, 1.0)
        fill_width = self.width * progress
        
        # Determine color based on readiness
        ready = progress >= 1.0
        text_color = arcade.color.YELLOW if ready else arcade.color.GRAY
        fill_color = arcade.color.YELLOW if ready else arcade.color.GRAY

        # Draw label (uppercase "DASH")
        arcade.draw_text(
            self.label.upper(),  # Convert to uppercase
            self.x,
            self.y + 12,  # Position above the bar (adjusted for smaller height)
            text_color,
            font_size=10  # Smaller font size
        )

        # Draw background bar
        arcade.draw_lrtb_rectangle_filled(
            self.x, 
            self.x + self.width, 
            self.y + self.height, 
            self.y, 
            arcade.color.DARK_GRAY
        )

        # Draw fill
        if fill_width > 0:
            arcade.draw_lrtb_rectangle_filled(
                self.x, 
                self.x + fill_width, 
                self.y + self.height, 
                self.y, 
                fill_color
            )
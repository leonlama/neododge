import arcade
import math
from src.skins.skin_manager import skin_manager

class Artifact:
    """Base class for all artifacts in the game"""

    def __init__(self, player, name="Artifact"):
        self.player = player
        self.name = name
        self.cooldown = 0
        self.cooldown_max = 5.0  # Default cooldown time in seconds
        self.active = False
        self.active_time = 0
        self.active_duration = 3.0  # Default active duration in seconds
        self.icon = None
        self.load_icon()

    def load_icon(self):
        """Load the artifact icon"""
        # Try to get the icon from the skin manager
        icon_name = self.name.lower().replace(" ", "_")
        self.icon = skin_manager.get_texture(icon_name)

        # If no icon found, create a default one
        if not self.icon:
            self.icon = arcade.make_soft_square_texture(
                32, 
                arcade.color.PURPLE, 
                outer_alpha=255
            )

    def update(self, delta_time):
        """Update the artifact state"""
        # Update cooldown
        if self.cooldown > 0:
            self.cooldown -= delta_time

        # Update active time
        if self.active:
            self.active_time -= delta_time
            if self.active_time <= 0:
                self.deactivate()

    def activate(self):
        """Activate the artifact if not on cooldown"""
        if self.cooldown <= 0 and not self.active:
            self.active = True
            self.active_time = self.active_duration
            self.cooldown = self.cooldown_max
            return True
        return False

    def deactivate(self):
        """Deactivate the artifact"""
        self.active = False
        self.active_time = 0

    def draw(self, x, y, scale=1.0):
        """Draw the artifact icon"""
        if self.icon:
            # Draw the icon
            arcade.draw_scaled_texture_rectangle(
                x, y, 
                self.icon,
                scale
            )

            # Draw cooldown overlay if on cooldown
            if self.cooldown > 0:
                # Calculate cooldown percentage
                cooldown_pct = self.cooldown / self.cooldown_max

                # Draw semi-transparent overlay
                arcade.draw_arc_filled(
                    x, y,
                    self.icon.width * scale,
                    self.icon.height * scale,
                    arcade.color.BLACK + (150,),  # Semi-transparent black
                    0, 360 * cooldown_pct,
                    0, 64  # Segments
                )

                # Draw cooldown text
                arcade.draw_text(
                    f"{self.cooldown:.1f}",
                    x, y,
                    arcade.color.WHITE,
                    font_size=12,
                    anchor_x="center",
                    anchor_y="center"
                )

    def get_cooldown_percentage(self):
        """Get the cooldown percentage (0.0 to 1.0)"""
        if self.cooldown_max <= 0:
            return 0
        return max(0, min(1, self.cooldown / self.cooldown_max))

    def get_active_percentage(self):
        """Get the active time percentage (0.0 to 1.0)"""
        if self.active_duration <= 0:
            return 0
        return max(0, min(1, self.active_time / self.active_duration))
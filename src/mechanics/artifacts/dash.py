import arcade
import math
from src.mechanics.artifacts.base import Artifact

class DashArtifact(Artifact):
    """Artifact that allows the player to dash"""

    def __init__(self, player):
        super().__init__(player, "Dash")
        self.cooldown_max = 3.0  # 3 seconds cooldown
        self.dash_distance = 150  # Distance to dash
        self.dash_speed = 1500  # Speed of the dash
        self.dash_trail = []  # Trail of positions for visual effect

    def activate(self):
        """Activate the dash if not on cooldown"""
        if super().activate():
            # Get player's current direction
            if hasattr(self.player, 'target_x') and hasattr(self.player, 'target_y'):
                # Calculate direction vector
                dx = self.player.target_x - self.player.center_x
                dy = self.player.target_y - self.player.center_y
                distance = math.sqrt(dx*dx + dy*dy)

                if distance > 0:
                    # Normalize and scale by dash distance
                    dx = dx / distance * self.dash_distance
                    dy = dy / distance * self.dash_distance

                    # Store current position for trail effect
                    self.dash_trail = [(self.player.center_x, self.player.center_y)]

                    # Apply dash
                    self.player.center_x += dx
                    self.player.center_y += dy

                    # Keep player on screen after dash
                    self.player.center_x = max(self.player.width/2, min(self.player.center_x, arcade.get_window().width - self.player.width/2))
                    self.player.center_y = max(self.player.height/2, min(self.player.center_y, arcade.get_window().height - self.player.height/2))

                    # Add end position to trail
                    self.dash_trail.append((self.player.center_x, self.player.center_y))

                    # Make player briefly invincible
                    self.player.invincible = True
                    self.player.invincible_timer = 0.5  # 0.5 seconds of invincibility

                    # Play dash sound if available
                    if hasattr(self.player.parent_view, 'dash_sound'):
                        arcade.play_sound(self.player.parent_view.dash_sound)

                    return True

            # If we couldn't dash, reset the cooldown
            self.cooldown = 0
            self.active = False
            return False

        return False

    def update(self, delta_time):
        """Update the dash artifact"""
        super().update(delta_time)

        # Fade out the dash trail
        if self.dash_trail and self.active_time < self.active_duration - 0.1:
            self.dash_trail = []

    def draw_trail(self):
        """Draw the dash trail effect"""
        if len(self.dash_trail) >= 2:
            start_pos, end_pos = self.dash_trail

            # Draw a line between start and end positions
            arcade.draw_line(
                start_pos[0], start_pos[1],
                end_pos[0], end_pos[1],
                arcade.color.WHITE,
                2
            )

            # Draw particles along the trail
            num_particles = 10
            for i in range(num_particles):
                t = i / (num_particles - 1)
                x = start_pos[0] + t * (end_pos[0] - start_pos[0])
                y = start_pos[1] + t * (end_pos[1] - start_pos[1])

                # Fade out particles based on position
                alpha = int(255 * (1 - t))

                arcade.draw_circle_filled(
                    x, y,
                    3,
                    arcade.color.WHITE + (alpha,)
                )
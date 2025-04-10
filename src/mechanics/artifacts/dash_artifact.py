import arcade
import math
from src.mechanics.artifacts.base import BaseArtifact
from src.skins.skin_manager import skin_manager
from src.core.scaling import get_scale

class DashArtifact(BaseArtifact):
    """Artifact that allows the player to dash."""

    def __init__(self, position_x, position_y):
        """Initialize the dash artifact.

        Args:
            position_x: X position of the artifact.
            position_y: Y position of the artifact.
        """
        super().__init__(artifact_id="dash", position_x=position_x, position_y=position_y, name="Dash")

        # Override default cooldown
        self.cooldown_max = 5.0
        
        # Dash properties
        self.dash_distance = 150  # Distance to dash
        self.dash_speed = 1500  # Speed of the dash
        self.dash_trail = []  # Trail of positions for visual effect

    def update(self, delta_time):
        """Update the artifact state.

        Args:
            delta_time: Time since last update.
        """
        # Call parent update method to handle cooldown
        super().update(delta_time)
                
        # Fade out the dash trail
        if self.dash_trail and len(self.dash_trail) > 0:
            self.dash_trail = []

    def apply_effect(self, player, game_state=None):
        """Apply dash effect to the player.
        
        Args:
            player: The player to apply the effect to.
            game_state: The current game state (not used for dash).
            
        Returns:
            bool: True if the effect was applied, False otherwise.
        """
        if self.is_ready():
            # Store current position for trail effect
            start_pos = (player.center_x, player.center_y)
            
            # Apply dash to player
            player.dash()
            
            # Store end position for trail effect
            end_pos = (player.center_x, player.center_y)
            self.dash_trail = [start_pos, end_pos]
            
            # Set cooldown
            self.cooldown_timer = self.cooldown_max
            return True
        return False
        
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
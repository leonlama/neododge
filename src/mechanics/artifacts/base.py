import arcade
from src.skins.skin_manager import skin_manager
from src.core.scaling import get_scale

class BaseArtifact(arcade.Sprite):
    """Base class for all artifacts in the game"""

    def __init__(self, position_x=0, position_y=0, name="Artifact"):
        super().__init__()

        # Position
        self.center_x = position_x
        self.center_y = position_y

        # Metadata
        self.name = name

        # Cooldown system
        self.cooldown_max = 5.0  # Default cooldown time in seconds
        self.cooldown_timer = 0.0

        # Active state
        self.active = False
        self.active_duration = 3.0  # Default active duration in seconds
        self.active_time = 0.0

        # Load texture
        self._load_texture()

        # Set scale
        self.scale = get_scale('artifact')

    def _load_texture(self):
        """Load the artifact texture"""
        artifact_id = self.name.lower().replace(" ", "_")
        self.texture = skin_manager.get_texture("artifacts", artifact_id)

        # Fallback texture if not found
        if not self.texture:
            self.texture = arcade.make_circle_texture(32, arcade.color.PURPLE)

    def update(self, delta_time):
        """Update the artifact state"""
        # Update cooldown
        if self.cooldown_timer > 0:
            self.cooldown_timer -= delta_time
            if self.cooldown_timer < 0:
                self.cooldown_timer = 0

        # Update active time
        if self.active:
            self.active_time -= delta_time
            if self.active_time <= 0:
                self.deactivate()

    def is_ready(self):
        """Check if the artifact is ready to use"""
        return self.cooldown_timer <= 0

    def use(self):
        """Use the artifact"""
        if self.is_ready():
            self.active = True
            self.active_time = self.active_duration
            self.cooldown_timer = self.cooldown_max
            return True
        return False

    def deactivate(self):
        """Deactivate the artifact"""
        self.active = False
        self.active_time = 0

    def draw_cooldown_overlay(self):
        """Draw cooldown overlay on the artifact"""
        if self.cooldown_timer > 0:
            # Calculate cooldown percentage
            cooldown_pct = self.cooldown_timer / self.cooldown_max

            # Draw semi-transparent overlay
            arcade.draw_arc_filled(
                self.center_x, self.center_y,
                self.width, self.height,
                arcade.color.BLACK + (150,),  # Semi-transparent black
                0, 360 * cooldown_pct,
                0, 64  # Segments
            )

            # Draw cooldown text
            arcade.draw_text(
                f"{self.cooldown_timer:.1f}",
                self.center_x, self.center_y,
                arcade.color.WHITE,
                font_size=12,
                anchor_x="center",
                anchor_y="center"
            )
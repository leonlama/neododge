import arcade
import random

class Artifact(arcade.Sprite):
    def __init__(self, x, y, artifact_type="dash"):
        super().__init__()
        self.center_x = x
        self.center_y = y
        self.artifact_type = artifact_type
        self.name = self._get_display_name()
        self.cooldown = self._get_cooldown()
        self.current_cooldown = 0

        # Set appearance
        self._set_appearance()

    def _set_appearance(self):
        """Set the visual appearance of the artifact."""
        color = arcade.color.GOLD
        self.texture = arcade.make_soft_square_texture(24, color, outer_alpha=255)

    def _get_display_name(self):
        """Get the display name for the artifact type."""
        names = {
            "dash": "Dash",
            "magnet": "Magnet Pulse",
            "slow_field": "Slow Field",
            "bullet_time": "Bullet Time",
            "clone": "Clone Dash"
        }
        return names.get(self.artifact_type, self.artifact_type.title())

    def _get_cooldown(self):
        """Get the cooldown duration for the artifact type."""
        cooldowns = {
            "dash": 5.0,
            "magnet": 30.0,
            "slow_field": 30.0,
            "bullet_time": 30.0,
            "clone": 30.0
        }
        return cooldowns.get(self.artifact_type, 10.0)

    def activate(self, player, game_state=None):
        """Activate the artifact ability."""
        if self.current_cooldown <= 0:
            if self.artifact_type == "dash":
                self._activate_dash(player)
            elif self.artifact_type == "magnet":
                self._activate_magnet(player, game_state)
            elif self.artifact_type == "slow_field":
                self._activate_slow_field(player, game_state)
            elif self.artifact_type == "bullet_time":
                self._activate_bullet_time(player, game_state)
            elif self.artifact_type == "clone":
                self._activate_clone(player)

            self.current_cooldown = self.cooldown
            return True
        return False

    def update(self, delta_time):
        """Update artifact cooldown."""
        if self.current_cooldown > 0:
            self.current_cooldown -= delta_time

    def _activate_dash(self, player):
        """Activate dash ability."""
        player.dash()

    def _activate_magnet(self, player, game_state):
        """Activate magnet pulse ability."""
        if game_state and hasattr(game_state, "coins"):
            # Pull all coins toward player
            for coin in game_state.coins:
                dx = player.center_x - coin.center_x
                dy = player.center_y - coin.center_y
                distance = max(1, (dx**2 + dy**2)**0.5)

                # Normalize and apply force
                coin.change_x = dx / distance * 200
                coin.change_y = dy / distance * 200

    def _activate_slow_field(self, player, game_state):
        """Activate slow field ability."""
        if game_state and hasattr(game_state, "enemies"):
            # Slow all enemies
            for enemy in game_state.enemies:
                enemy.slow_factor = 0.5
                enemy.slow_timer = 5.0  # 5 seconds of slow

    def _activate_bullet_time(self, player, game_state):
        """Activate bullet time ability."""
        if game_state:
            game_state.time_scale = 0.5
            game_state.bullet_time_timer = 5.0  # 5 seconds of bullet time

    def _activate_clone(self, player):
        """Activate clone dash ability."""
        # This would create a clone of the player that dashes in a different direction
        # Implementation depends on your player class
        pass

class ArtifactManager:
    """Manages artifact creation and effects."""

    def __init__(self):
        self.artifact_types = ["dash", "magnet", "slow_field", "bullet_time", "clone"]

    def create_artifact(self, artifact_type, x, y):
        """Create an artifact of the specified type."""
        return Artifact(x, y, artifact_type)

    def create_random_artifact(self, x, y, excluded_types=None):
        """Create a random artifact, excluding specified types."""
        if excluded_types is None:
            excluded_types = []

        available_types = [t for t in self.artifact_types if t not in excluded_types]

        if not available_types:
            return None

        artifact_type = random.choice(available_types)
        return self.create_artifact(artifact_type, x, y)

    def update_artifacts(self, artifacts, delta_time):
        """Update all artifacts."""
        for artifact in artifacts:
            if hasattr(artifact, "update"):
                artifact.update(delta_time)
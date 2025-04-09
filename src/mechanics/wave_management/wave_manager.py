import random
import time
from src.mechanics.wave_management.wave_generator import WaveGenerator

class WaveManager:
    """Manages the creation and progression of waves in the game."""

    def __init__(self, game_view=None):
        """Initialize the wave manager.

        Args:
            game_view: The game view that this wave manager is associated with.
        """
        self.game_view = game_view
        self.wave_generator = WaveGenerator()
        self.current_wave = None
        self.wave_number = 0
        self.in_wave = False
        self.wave_timer = 0
        self.wave_duration = 0
        self.spawn_timer = 0
        self.spawn_delay = 1.0
        self.enemies_to_spawn = 0

        # Callbacks
        self.on_spawn_enemy = None
        self.on_clear_enemies = None
        self.on_wave_complete = None

        # Player data
        self.player_profile = {
            "playstyle": {
                "aggression": 0.5,
                "risk": 0.5
            },
            "skill_level": 0.5
        }
        self.engagement_score = 0.5

        # Set up callbacks if game_view is provided
        if game_view:
            self._setup_callbacks()

    def _setup_callbacks(self):
        """Set up callbacks based on the game_view."""
        # Check if game_view has the necessary methods
        if hasattr(self.game_view, 'spawn_enemy'):
            self.on_spawn_enemy = self.game_view.spawn_enemy

        if hasattr(self.game_view, 'clear_enemies'):
            self.on_clear_enemies = self.game_view.clear_enemies

        if hasattr(self.game_view, 'on_wave_complete'):
            self.on_wave_complete = self.game_view.on_wave_complete

    def update(self, delta_time):
        """Update the wave manager."""
        if not self.in_wave:
            return

        # Update wave timer
        self.wave_timer += delta_time

        # Check if wave is complete
        if self.wave_timer >= self.wave_duration:
            print(f"Wave {self.wave_number} completed (timer: {self.wave_timer:.2f}, duration: {self.wave_duration:.2f})")
            self.end_wave()
            if self.on_wave_complete:
                self.on_wave_complete(self.wave_number)
            return

        # Update spawn timer
        if self.enemies_to_spawn > 0:
            self.spawn_timer += delta_time
            if self.spawn_timer >= self.spawn_delay:
                self.spawn_timer = 0
                self.spawn_enemy()

    def start_wave(self):
        """Start a new wave."""
        self.wave_number += 1
        self.in_wave = True
        self.wave_timer = 0
        self.spawn_timer = 0

        # Generate wave configuration
        self.current_wave = self.wave_generator.create_wave(
            self.wave_number, 
            self.player_profile, 
            self.engagement_score
        )

        # Set wave parameters
        self.wave_duration = self.current_wave.get("duration", 45.0)
        self.spawn_delay = self.current_wave.get("spawn_delay", 1.0)
        self.enemies_to_spawn = self.current_wave.get("enemy_count", 0)

        print(f"Starting Wave {self.wave_number}")
        print(f"  Type: {self.current_wave.get('type', 'normal')}")
        print(f"  Enemy Count: {self.enemies_to_spawn}")
        print(f"  Enemy Types: {self.current_wave.get('enemy_types', [])}")
        print(f"  Enemy Speed: {self.current_wave.get('enemy_speed', 1.0)}")
        print(f"  Spawn Delay: {self.spawn_delay}")
        print(f"  Duration: {self.wave_duration}")

        return self.current_wave

    def end_wave(self):
        """End the current wave."""
        # Clear any remaining enemies
        if self.on_clear_enemies:
            self.on_clear_enemies()

        # Reset wave timer
        self.wave_timer = 0
        self.in_wave = False

    def spawn_enemy(self):
        """Spawn an enemy from the current wave."""
        if self.enemies_to_spawn <= 0 or not self.on_spawn_enemy:
            return

        # Get enemy type
        enemy_types = self.current_wave.get("enemy_types", ["basic"])
        enemy_index = min(self.current_wave.get("enemy_count", 0) - self.enemies_to_spawn, len(enemy_types) - 1)
        enemy_type = enemy_types[enemy_index]

        # Get enemy parameters
        enemy_params = {
            "speed": self.current_wave.get("enemy_speed", 1.0),
            "health": self.current_wave.get("enemy_health", 1.0)
        }

        print(f"Spawning enemy: {enemy_type} with params {enemy_params}")

        # Spawn the enemy
        self.on_spawn_enemy(enemy_type, enemy_params)
        self.enemies_to_spawn -= 1

    def set_player_profile(self, profile):
        """Set the player profile for wave generation."""
        self.player_profile = profile

    def set_engagement_score(self, score):
        """Set the engagement score for wave generation."""
        self.engagement_score = score
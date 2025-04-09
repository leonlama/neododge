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
            print("Not in wave, starting new wave...")
            self.start_wave()
            return

        # Update wave timer
        self.wave_timer += delta_time

        # Check if wave is complete
        if self.wave_timer >= self.wave_duration:
            print(f"Wave {self.wave_number} completed (duration reached)")
            self.end_wave()
            return

        # Update spawn timer
        self.spawn_timer += delta_time

        # Spawn enemies if it's time and there are enemies to spawn
        if self.spawn_timer >= self.spawn_delay and self.enemies_to_spawn > 0:
            print(f"Spawning enemy ({self.enemies_to_spawn} remaining)")
            self.spawn_timer = 0
            self.spawn_enemy()

        # Set targets for enemies if game_view has player and enemies
        if hasattr(self.game_view, 'player') and hasattr(self.game_view, 'enemies'):
            for enemy in self.game_view.enemies:
                if hasattr(enemy, 'set_target') and enemy.target is None:
                    enemy.set_target(self.game_view.player)

    def start_wave(self):
        """Start a new wave."""
        self.wave_number += 1

        # Get player analytics if available
        if hasattr(self.game_view, 'player_analytics'):
            self.player_profile = self.game_view.player_analytics.get_player_profile()
            self.engagement_score = self.game_view.player_analytics.calculate_engagement_score()

        # Generate wave configuration
        self.current_wave = self.wave_generator.create_wave(
            self.wave_number, 
            self.player_profile,
            self.engagement_score
        )

        # Set wave parameters
        self.wave_duration = self.current_wave["duration"]
        self.spawn_delay = self.current_wave["spawn_delay"]
        self.enemies_to_spawn = self.current_wave["enemy_count"]

        # Reset timers
        self.wave_timer = 0
        self.spawn_timer = 0
        self.in_wave = True

        # Display wave message if available
        if "message" in self.current_wave and hasattr(self.game_view, 'show_message'):
            self.game_view.show_message(self.current_wave["message"])

        print(f"Starting Wave {self.wave_number}")

        # Spawn orbs
        if hasattr(self.game_view, 'spawn_orbs'):
            self.game_view.spawn_orbs(
                self.current_wave["orb_count"],
                self.current_wave["orb_types"]
            )

        # Spawn artifact if needed
        if self.current_wave["spawn_artifact"] and hasattr(self.game_view, 'spawn_artifact'):
            self.game_view.spawn_artifact()

        return self.current_wave

    def end_wave(self):
        """End the current wave."""
        self.in_wave = False

        # Clear remaining enemies if callback exists
        if self.on_clear_enemies:
            self.on_clear_enemies()

    def spawn_enemy(self):
        """Spawn an enemy from the current wave."""
        if self.enemies_to_spawn <= 0:
            return

        # Get enemy type for this spawn
        enemy_index = self.current_wave["enemy_count"] - self.enemies_to_spawn
        enemy_type = self.current_wave["enemy_types"][min(enemy_index, len(self.current_wave["enemy_types"]) - 1)]

        print(f"Spawning enemy of type: {enemy_type}")

        # Generate formation if not already done
        if not hasattr(self, 'spawn_positions') or not self.spawn_positions:
            self._generate_formation()

        # Get position from formation
        position = None
        if hasattr(self, 'spawn_positions') and self.spawn_positions:
            if enemy_index < len(self.spawn_positions):
                position = self.spawn_positions[enemy_index]
            else:
                # Fallback: generate a random position
                screen_width, screen_height = self.game_view.get_screen_dimensions()
                position = (
                    random.randint(50, screen_width - 50),
                    random.randint(50, screen_height - 50)
                )
        else:
            # Fallback: generate a random position
            screen_width, screen_height = self.game_view.get_screen_dimensions()
            position = (
                random.randint(50, screen_width - 50),
                random.randint(50, screen_height - 50)
            )

        # Get enemy modifiers
        speed = self.current_wave.get("enemy_speed", 1.0)
        health = self.current_wave.get("enemy_health", 1.0)

        # Spawn the enemy
        print(f"Calling on_spawn_enemy with: {enemy_type}, {position}")
        self.on_spawn_enemy(
            enemy_type=enemy_type,
            position=position,
            speed=speed,
            health=health
        )

        # Decrement enemies to spawn
        self.enemies_to_spawn -= 1

    def _generate_formation(self):
        """Generate spawn positions based on the current wave formation."""
        formation = self.current_wave.get("formation", "random")
        screen_width, screen_height = 800, 600  # Default values

        if hasattr(self.game_view, 'get_screen_dimensions'):
            screen_width, screen_height = self.game_view.get_screen_dimensions()

        self.spawn_positions = self.wave_generator.formation_generator.generate_formation(
            formation,
            self.current_wave["enemy_count"],
            screen_width,
            screen_height
        )

    def set_player_profile(self, profile):
        """Set the player profile for wave generation."""
        self.player_profile = profile

    def set_engagement_score(self, score):
        """Set the engagement score for wave generation."""
        self.engagement_score = score
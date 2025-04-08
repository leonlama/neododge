import arcade
import random
from typing import Optional, List, Dict

# Import only what exists in your project
from src.mechanics.wave_management.wave_manager import WaveManager
from src.mechanics.wave_management.difficulty_adjuster import DifficultyAdjuster
from src.mechanics.wave_management.wave_generator import WaveGenerator
from src.mechanics.wave_management.wave_analytics import WaveAnalytics, PlayerAnalytics

from src.entities.enemies.enemy import Enemy
from src.mechanics.orbs.orb_manager import OrbManager
from src.mechanics.artifacts.artifact_manager import ArtifactManager

class GameController:
    """Controls the game flow, wave progression, and entity management."""

    def __init__(self, player, screen_width, screen_height):
        self.player = player
        self.screen_width = screen_width
        self.screen_height = screen_height

        # Wave management components - only use what exists
        self.difficulty_adjuster = DifficultyAdjuster()
        self.wave_generator = WaveGenerator()
        self.wave_manager = WaveManager()

        # Game state
        self.current_wave_number = 0
        self.wave_timer = 0
        self.wave_duration = 20.0  # seconds
        self.rest_period = False
        self.rest_timer = 0
        self.rest_duration = 5.0  # seconds
        self.wave_message = ""
        self.wave_message_alpha = 0

        # Entity lists (references to the main game's sprite lists)
        self.enemies = None
        self.orbs = None
        self.coins = None
        self.artifacts = None

    def initialize(self, enemies, orbs, coins, artifacts):
        """Initialize with references to game's sprite lists."""
        self.enemies = enemies
        self.orbs = orbs
        self.coins = coins
        self.artifacts = artifacts

        # Start the first wave
        self.start_next_wave()

    def start_next_wave(self):
        """Start the next wave of enemies."""
        self.current_wave_number += 1

        # Clear existing enemies
        if self.enemies:
            self.enemies.clear()

        # Get difficulty parameters based on wave number
        difficulty = self.difficulty_adjuster.get_difficulty(self.current_wave_number)

        # Generate wave configuration
        wave_config = self.wave_generator.generate_wave(
            self.current_wave_number, 
            difficulty,
            self.player
        )

        # Spawn enemies according to wave configuration
        self.spawn_wave_entities(wave_config)

        # Set wave message
        if wave_config.get("is_rest_wave", False):
            self.wave_message = f"Rest Wave {self.current_wave_number}"
            self.rest_period = True
            self.wave_duration = self.rest_duration
        else:
            self.wave_message = f"Wave {self.current_wave_number}"
            self.rest_period = False
            self.wave_duration = 20.0 + (self.current_wave_number * 0.5)  # Waves get longer

        self.wave_message_alpha = 255
        self.wave_timer = 0

        return wave_config

    def spawn_wave_entities(self, wave_config):
        """Spawn entities based on wave configuration."""
        # Spawn enemies
        for enemy_data in wave_config.get("enemies", []):
            self.spawn_enemy(enemy_data)

        # Spawn orbs
        for orb_data in wave_config.get("orbs", []):
            self.spawn_orb(orb_data)

        # Spawn coins
        for coin_data in wave_config.get("coins", []):
            self.spawn_coin(coin_data)

        # Maybe spawn artifact
        if wave_config.get("artifact"):
            self.spawn_artifact(wave_config["artifact"])

    def spawn_enemy(self, enemy_data):
        """Spawn an enemy based on configuration data."""
        # This should create the appropriate enemy type and add it to self.enemies
        # The implementation depends on your enemy class structure
        enemy_type = enemy_data.get("type", "basic")
        x = enemy_data.get("x", random.randint(50, self.screen_width - 50))
        y = enemy_data.get("y", random.randint(50, self.screen_height - 50))

        # Create enemy (implementation depends on your enemy classes)
        enemy = Enemy(x, y, self.player, behavior=enemy_type)
        self.enemies.append(enemy)

    def spawn_orb(self, orb_data):
        """Spawn an orb based on configuration data."""
        # Implementation depends on your orb class structure
        orb_type = orb_data.get("type", "basic")
        x = orb_data.get("x", random.randint(50, self.screen_width - 50))
        y = orb_data.get("y", random.randint(50, self.screen_height - 50))

        # Create orb (implementation depends on your orb classes)
        orb = create_orb(orb_type, x, y)
        if orb:
            self.orbs.append(orb)

    def spawn_coin(self, coin_data):
        """Spawn a coin based on configuration data."""
        x = coin_data.get("x", random.randint(50, self.screen_width - 50))
        y = coin_data.get("y", random.randint(50, self.screen_height - 50))

        # Create coin
        from src.mechanics.coins.coin import Coin
        coin = Coin(x, y)
        self.coins.append(coin)

    def spawn_artifact(self, artifact_data):
        """Spawn an artifact based on configuration data."""
        artifact_type = artifact_data.get("type")
        x = artifact_data.get("x", random.randint(50, self.screen_width - 50))
        y = artifact_data.get("y", random.randint(50, self.screen_height - 50))

        # Create artifact (implementation depends on your artifact classes)
        artifact = create_artifact(artifact_type, x, y)
        if artifact:
            self.artifacts.append(artifact)

    def update(self, delta_time):
        """Update game state and wave progression."""
        # Update wave timer
        self.wave_timer += delta_time

        # Fade wave message
        if self.wave_message_alpha > 0:
            self.wave_message_alpha = max(0, self.wave_message_alpha - 2)

        # Check if wave is complete
        if self.wave_timer >= self.wave_duration:
            # Wave complete
            if self.rest_period:
                # Rest period is over, start next wave
                self.start_next_wave()
            else:
                # Start rest period between waves
                self.rest_period = True
                self.wave_timer = 0
                self.wave_duration = self.rest_duration
                self.wave_message = f"Wave {self.current_wave_number} Complete!"
                self.wave_message_alpha = 255

        # Check if all enemies are defeated
        if not self.rest_period and len(self.enemies) == 0:
            # All enemies defeated, start rest period
            self.rest_period = True
            self.wave_timer = 0
            self.wave_duration = self.rest_duration
            self.wave_message = f"Wave {self.current_wave_number} Complete!"
            self.wave_message_alpha = 255

    def should_show_shop(self):
        """Determine if the shop should be shown."""
        # Show shop every 5 waves
        return self.current_wave_number % 5 == 0 and self.rest_period

    def get_wave_info(self):
        """Get current wave information for display."""
        return {
            "wave_number": self.current_wave_number,
            "is_rest": self.rest_period,
            "time_remaining": max(0, self.wave_duration - self.wave_timer),
            "message": self.wave_message,
            "message_alpha": self.wave_message_alpha
        }
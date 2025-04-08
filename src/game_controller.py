import arcade
import random
from typing import Optional, List, Dict

# Import wave management components
from src.mechanics.wave_management.wave_manager import WaveManager
from src.mechanics.wave_management.difficulty_adjuster import DifficultyAdjuster
from src.mechanics.wave_management.wave_generator import WaveGenerator

# Import entity managers
from src.entities.enemies.enemy import Enemy
from src.mechanics.orbs.orb_manager import OrbManager, Orb
from src.mechanics.artifacts.artifact_manager import ArtifactManager, Artifact

class GameController:
    """Controls the game flow, wave progression, and entity management."""

    def __init__(self, player, screen_width, screen_height):
        self.player = player
        self.screen_width = screen_width
        self.screen_height = screen_height

        # Wave management components
        self.difficulty_adjuster = DifficultyAdjuster()
        self.wave_generator = WaveGenerator()
        self.wave_manager = WaveManager(player)  # Pass player to WaveManager

        # Entity managers
        self.orb_manager = OrbManager()
        self.artifact_manager = ArtifactManager()

        # Game state
        self.current_wave_number = 0
        self.wave_timer = 0
        self.wave_duration = 20.0  # seconds
        self.rest_period = False
        self.rest_timer = 0
        self.rest_duration = 5.0  # seconds
        self.wave_message = ""
        self.wave_message_alpha = 0
        self.time_scale = 1.0
        self.bullet_time_timer = 0

        # Player profile (simplified for now)
        self.player_profile = {
            "skill_level": 0.5,
            "playstyle": {
                "aggression": 0.5,
                "caution": 0.5
            },
            "preferences": {
                "orb_preference": None
            }
        }

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
        # Use calculate_parameters instead of get_difficulty
        try:
            difficulty_params = self.difficulty_adjuster.calculate_parameters(
                self.current_wave_number, 
                self.player_profile,
                0.7  # Default engagement score
            )
        except Exception as e:
            print(f"Error calculating difficulty: {e}")
            # Fallback to default difficulty
            difficulty_params = self._get_default_difficulty(self.current_wave_number)

        # Generate wave configuration
        # Use create_wave instead of generate_wave
        try:
            wave_config = self.wave_generator.create_wave(
                self.current_wave_number, 
                difficulty_params,
                self.player_profile
            )
        except Exception as e:
            print(f"Error creating wave: {e}")
            # Fallback to default wave
            wave_config = self._get_default_wave(self.current_wave_number)

        # Spawn enemies according to wave configuration
        self.spawn_wave_entities(wave_config)

        # Set wave message
        if wave_config.get("type") == "rest":
            self.wave_message = wave_config.get("message", f"Rest Wave {self.current_wave_number}")
            self.rest_period = True
            self.wave_duration = self.rest_duration
        else:
            self.wave_message = wave_config.get("message", f"Wave {self.current_wave_number}")
            self.rest_period = False
            self.wave_duration = 20.0 + (self.current_wave_number * 0.5)  # Waves get longer

        self.wave_message_alpha = 255
        self.wave_timer = 0

    def _get_default_difficulty(self, wave_number):
        """Fallback method to get default difficulty parameters."""
        return {
            "difficulty": min(0.9, 0.3 + (wave_number * 0.03)),
            "enemy_count": min(25, 3 + wave_number + wave_number // 3),
            "enemy_speed": 0.8 + min(0.9, 0.3 + (wave_number * 0.03)) * 0.4,
            "enemy_health": 0.8 + min(0.9, 0.3 + (wave_number * 0.03)) * 0.4,
            "enemy_types": {"chaser": 0.5, "wander": 0.5},
            "orb_count": min(3, wave_number // 5),
            "orb_types": {"buff": 0.8, "debuff": 0.2},
            "spawn_artifact": wave_number % 5 == 0
        }

    def _get_default_wave(self, wave_number):
        """Fallback method to get a default wave configuration."""
        is_rest = wave_number % 6 == 0

        if is_rest:
            return {
                "type": "rest",
                "enemies": [{"type": "wander"}, {"type": "wander"}],
                "orbs": [],
                "coins": [{"x": random.randint(100, 700), "y": random.randint(100, 500)} for _ in range(5)],
                "artifact": None,
                "message": f"Rest Wave {wave_number}"
            }
        else:
            return {
                "type": "normal",
                "enemies": [{"type": "chaser"}, {"type": "wander"}, {"type": "wander"}],
                "orbs": [{"type": "speed"}],
                "coins": [{"x": random.randint(100, 700), "y": random.randint(100, 500)} for _ in range(3)],
                "artifact": {"type": "dash"} if wave_number % 5 == 0 else None,
                "message": f"Wave {wave_number}"
            }

    def spawn_wave_entities(self, wave_config):
        """Spawn entities based on wave configuration."""
        # Adapt to different wave config formats

        # Spawn enemies
        enemy_data = wave_config.get("enemies", [])
        if isinstance(enemy_data, list):
            # If it's a list of enemy data
            for enemy in enemy_data:
                if isinstance(enemy, dict):
                    self.spawn_enemy(enemy)
        elif isinstance(enemy_data, int):
            # If it's just a count
            enemy_types = wave_config.get("enemy_types", ["chaser"])
            if isinstance(enemy_types, list):
                for i in range(min(enemy_data, len(enemy_types))):
                    self.spawn_enemy({"type": enemy_types[i]})
            else:
                for _ in range(enemy_data):
                    self.spawn_enemy({"type": "chaser"})

        # Spawn orbs
        orb_data = wave_config.get("orbs", [])
        if isinstance(orb_data, list):
            # If it's a list of orb data
            for orb in orb_data:
                if isinstance(orb, dict):
                    self.spawn_orb(orb)
        elif isinstance(orb_data, int):
            # If it's just a count
            for _ in range(orb_data):
                orb_type = "speed"  # Default
                self.spawn_orb({"type": orb_type})

        # Spawn coins
        coin_data = wave_config.get("coins", [])
        if isinstance(coin_data, list):
            # If it's a list of coin data
            for coin in coin_data:
                if isinstance(coin, dict):
                    self.spawn_coin(coin)
        elif isinstance(coin_data, int):
            # If it's just a count
            for _ in range(coin_data):
                self.spawn_coin({"x": random.randint(100, 700), "y": random.randint(100, 500)})

        # Maybe spawn artifact
        artifact_data = wave_config.get("artifact")
        if artifact_data:
            if isinstance(artifact_data, dict):
                self.spawn_artifact(artifact_data)
            elif artifact_data is True:
                self.spawn_artifact({"type": "dash"})

    def spawn_enemy(self, enemy_data):
        """Spawn an enemy based on configuration data."""
        enemy_type = enemy_data.get("type", "chaser")
        x = enemy_data.get("x", random.randint(50, self.screen_width - 50))
        y = enemy_data.get("y", random.randint(50, self.screen_height - 50))

        # Create enemy using the correct interface
        enemy = Enemy(x, y, self.player, enemy_type=enemy_type)
        self.enemies.append(enemy)

    def spawn_orb(self, orb_data):
        """Spawn an orb based on configuration data."""
        orb_type = orb_data.get("type", "speed")
        x = orb_data.get("x", random.randint(50, self.screen_width - 50))
        y = orb_data.get("y", random.randint(50, self.screen_height - 50))

        # Create orb using the orb manager
        orb = self.orb_manager.create_orb(orb_type, x, y)
        self.orbs.append(orb)

    def spawn_coin(self, coin_data):
        """Spawn a coin based on configuration data."""
        x = coin_data.get("x", random.randint(50, self.screen_width - 50))
        y = coin_data.get("y", random.randint(50, self.screen_height - 50))

        # Create a simple coin sprite
        coin = arcade.Sprite()
        coin.texture = arcade.make_soft_circle_texture(16, arcade.color.GOLD)
        coin.center_x = x
        coin.center_y = y
        self.coins.append(coin)

    def spawn_artifact(self, artifact_data):
        """Spawn an artifact based on configuration data."""
        artifact_type = artifact_data.get("type", "dash")
        x = artifact_data.get("x", random.randint(50, self.screen_width - 50))
        y = artifact_data.get("y", random.randint(50, self.screen_height - 50))

        # Create artifact using the artifact manager
        artifact = self.artifact_manager.create_artifact(artifact_type, x, y)
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

        # Update bullet time effect
        if self.bullet_time_timer > 0:
            self.bullet_time_timer -= delta_time
            if self.bullet_time_timer <= 0:
                self.time_scale = 1.0

        # Update orb effects on player
        self.orb_manager.update_player_orb_effects(self.player, delta_time)

        # Update artifacts
        self.artifact_manager.update_artifacts(self.artifacts, delta_time)

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
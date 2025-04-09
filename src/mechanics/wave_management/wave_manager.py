import random
import math
from src.audio.sound_manager import sound_manager

class WaveManager:
    def __init__(self, player):
        self.wave = 1
        self.player = player
        self.wave_history = []
        self.last_message_drawn = ""
        self.base_enemies = 5
        self.enemies_per_wave = 2
        self.max_enemies = 20
        
        # Wave timing
        self.in_wave = False
        self.wave_timer = 0
        self.wave_duration = 30.0  # 30 seconds per wave
        self.between_wave_timer = 0
        self.between_wave_duration = 5.0  # 5 seconds between waves
        
        # Callbacks
        self.on_wave_start = None
        self.on_wave_end = None
        self.on_spawn_enemies = None
        self.on_clear_enemies = None

    def update(self, delta_time):
        """Update the wave manager.

        Args:
            delta_time: Time since last update
        """
        # Update wave timer
        if self.in_wave:
            self.wave_timer += delta_time

            # Check if wave is over
            if self.wave_timer >= self.wave_duration:
                print(f"🌊 Wave {self.wave} completed!")
                self.end_wave()

                # Start next wave after delay
                self.between_wave_timer = 0
                self.in_wave = False

                # Increment wave counter
                self.wave += 1

                # Trigger wave end event
                if self.on_wave_end:
                    self.on_wave_end(self.wave - 1)  # Pass the completed wave number
        else:
            # Between waves
            self.between_wave_timer += delta_time

            # Check if it's time for next wave
            if self.between_wave_timer >= self.between_wave_duration:
                self.start_wave()

                # Trigger wave start event
                if self.on_wave_start:
                    self.on_wave_start(self.wave)

    def start_wave(self):
        """Start a new wave."""
        print(f"🌊 Starting wave {self.wave}")
        self.in_wave = True
        self.wave_timer = 0

        # Spawn enemies for this wave
        if self.on_spawn_enemies:
            self.on_spawn_enemies()

        # Play wave start sound
        try:
            sound_manager.play_sound("ui", "wave")
        except:
            pass

    def end_wave(self):
        """End the current wave."""
        # Clear any remaining enemies
        if self.on_clear_enemies:
            self.on_clear_enemies()

        # Reset wave timer
        self.wave_timer = 0
        self.in_wave = False

    def generate_wave(self, wave_number):
        """Generate a wave configuration based on wave number"""
        # Determine wave type
        if wave_number % 10 == 0:
            return self._create_boss_wave(wave_number)
        elif wave_number % 5 == 0:
            return self._create_rest_wave(wave_number)
        else:
            return self._create_normal_wave(wave_number)

    def _create_normal_wave(self, wave_number):
        """Create a standard wave with varied enemies"""
        # Calculate base difficulty
        difficulty = min(0.9, 0.3 + (wave_number * 0.05))

        # Calculate enemy count based on wave number
        enemy_count = min(20, 3 + wave_number + (wave_number // 3))

        # Determine enemy types
        enemy_types = []
        for _ in range(enemy_count):
            if wave_number < 3:
                enemy_type = "basic"
            elif wave_number < 7:
                enemy_type = random.choice(["basic", "chaser"])
            else:
                enemy_type = random.choice(["basic", "chaser", "shooter"])

            enemy_types.append(enemy_type)

        # Determine orb count
        orb_count = 0
        if wave_number >= 3:
            orb_count = min(3, wave_number // 3)

        # Determine if artifact should spawn
        spawn_artifact = (wave_number % 5 == 0)

        return {
            "type": "normal",
            "wave_number": wave_number,
            "difficulty": difficulty,
            "enemy_count": enemy_count,
            "enemy_types": enemy_types,
            "enemy_params": {
                "speed": 0.8 + (difficulty * 0.4),
                "health": 0.8 + (difficulty * 0.4)
            },
            "orb_count": orb_count,
            "orb_types": {"buff": 0.8, "debuff": 0.2},
            "spawn_artifact": spawn_artifact,
            "coin_count": random.randint(3, 7),
            "message": f"Wave {wave_number} - Good luck!"
        }

    def _create_boss_wave(self, wave_number):
        """Create a boss wave with a powerful enemy"""
        return {
            "type": "boss",
            "wave_number": wave_number,
            "difficulty": 0.8,
            "enemy_count": 1,
            "enemy_types": ["boss"],
            "enemy_params": {
                "speed": 0.9,
                "health": 5.0
            },
            "orb_count": 2,
            "orb_types": {"buff": 1.0, "debuff": 0.0},
            "spawn_artifact": True,
            "coin_count": random.randint(10, 15),
            "message": f"Boss Wave {wave_number//10} - Good luck!"
        }

    def _create_rest_wave(self, wave_number):
        """Create a rest wave with minimal enemies"""
        return {
            "type": "rest",
            "wave_number": wave_number,
            "difficulty": 0.3,
            "enemy_count": 2,
            "enemy_types": ["basic", "basic"],
            "enemy_params": {
                "speed": 0.7,
                "health": 0.8
            },
            "orb_count": 1,
            "orb_types": {"buff": 1.0, "debuff": 0.0},
            "spawn_artifact": False,
            "coin_count": random.randint(5, 10),
            "message": "Rest Wave - Catch your breath!"
        }

    def spawn_enemies(self, enemy_list, screen_width, screen_height, player=None):
        """Spawn enemies for the current wave.

        Args:
            enemy_list: The sprite list to add enemies to
            screen_width: Width of the screen
            screen_height: Height of the screen
            player: The player sprite (for targeting)
        """
        # Determine number of enemies based on wave
        num_enemies = self.base_enemies + (self.wave - 1) * self.enemies_per_wave

        # Cap at maximum enemies
        num_enemies = min(num_enemies, self.max_enemies)

        print(f"🔴 Spawning {num_enemies} enemies for wave {self.wave}")

        # Determine enemy type distribution based on wave
        # Early waves: mostly wanderers
        # Mid waves: mix of wanderers and chasers
        # Later waves: mix of all types with more shooters
        wanderer_percent = max(20, 100 - self.wave * 10)
        chaser_percent = min(60, self.wave * 8)
        shooter_percent = min(40, max(0, self.wave * 5 - 10))

        # Normalize percentages
        total = wanderer_percent + chaser_percent + shooter_percent
        wanderer_percent = wanderer_percent / total * 100
        chaser_percent = chaser_percent / total * 100
        shooter_percent = shooter_percent / total * 100

        # Spawn enemies
        for i in range(num_enemies):
            # Determine enemy type
            roll = random.uniform(0, 100)

            if roll < wanderer_percent:
                enemy_type = "wanderer"
            elif roll < wanderer_percent + chaser_percent:
                enemy_type = "chaser"
            else:
                enemy_type = "shooter"

            # Determine spawn position (away from player)
            min_distance = 200  # Minimum distance from player

            if player:
                # Keep trying until we find a position far enough from player
                for _ in range(10):  # Try up to 10 times
                    x = random.randint(50, screen_width - 50)
                    y = random.randint(50, screen_height - 50)

                    # Check distance from player
                    dx = x - player.center_x
                    dy = y - player.center_y
                    distance = math.sqrt(dx*dx + dy*dy)

                    if distance >= min_distance:
                        break
            else:
                # No player, just pick random position
                x = random.randint(50, screen_width - 50)
                y = random.randint(50, screen_height - 50)

            # Create the appropriate enemy type
            try:
                if enemy_type == "wanderer":
                    from src.entities.enemies.wanderer import WandererEnemy
                    enemy = WandererEnemy(x, y, player)
                elif enemy_type == "chaser":
                    from src.entities.enemies.chaser import ChaserEnemy
                    enemy = ChaserEnemy(x, y, player)
                elif enemy_type == "shooter":
                    from src.entities.enemies.shooter import ShooterEnemy
                    enemy = ShooterEnemy(x, y, player)
                else:
                    # Fallback to base enemy
                    from src.entities.enemies.enemy import Enemy
                    enemy = Enemy(x, y, player, enemy_type)

                # Add to enemy list
                enemy_list.append(enemy)

            except ImportError as e:
                print(f"Error importing enemy class: {e}")
                # Fallback to base enemy
                from src.entities.enemies.enemy import Enemy
                enemy = Enemy(x, y, player)
                enemy_list.append(enemy)

    def update_analytics(self, delta_time):
        """Placeholder for analytics update"""
        pass

    def end_wave_analysis(self):
        """Placeholder for end of wave analysis"""
        return {
            "damage_taken": 0,
            "enemies_defeated": 0,
            "orbs_collected": 0,
            "survival_time": 0
        }

    def maybe_spawn_artifact(self, current_artifacts, current_dash_artifact, screen_width, screen_height):
        """Determine if an artifact should spawn and which type"""
        artifact_types = [
            "dash",
            "magnet_pulse",
            "slow_field",
            "bullet_time",
            "clone_dash"
        ]

        # Filter out artifacts the player already has
        available_types = [t for t in artifact_types if t not in current_artifacts]

        if not available_types:
            return None

        artifact_type = random.choice(available_types)
        x = random.randint(100, screen_width - 100)
        y = random.randint(100, screen_height - 100)

        if artifact_type == "dash":
            from src.mechanics.artifacts.dash import DashArtifact
            return DashArtifact(x, y)
        # elif artifact_type == "magnet_pulse":
        #     from src.mechanics.artifacts.magnet_pulse import MagnetPulseArtifact
        #     return MagnetPulseArtifact(x, y)
        # elif artifact_type == "slow_field":
        #     from src.mechanics.artifacts.slow_field import SlowFieldArtifact
        #     return SlowFieldArtifact(x, y)
        # elif artifact_type == "bullet_time":
        #     from src.mechanics.artifacts.bullet_time import BulletTimeArtifact
        #     return BulletTimeArtifact(x, y)
        # elif artifact_type == "clone_dash":
        #     from src.mechanics.artifacts.clone_dash import CloneDashArtifact
        #     return CloneDashArtifact(x, y)
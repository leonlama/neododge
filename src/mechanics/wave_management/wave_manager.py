import random
import math
from src.audio.sound_manager import sound_manager

class WaveManager:
    def __init__(self, game_view):
        """Initialize the wave manager."""
        self.game_view = game_view
        self.wave = 0
        self.wave_timer = 0
        self.enemy_spawn_timer = 0
        self.between_wave_timer = 0
        self.in_wave = False
        self.wave_duration = 30.0
        self.between_wave_duration = 5.0
        self.wave_message = ""
        self.wave_message_alpha = 0.0
        self.last_message_drawn = ""

        # Enemy spawn parameters
        self.base_enemies = 3
        self.enemies_per_wave = 2
        self.max_enemies = 20

        # Event callbacks
        self.on_wave_start = None
        self.on_wave_end = None
        self.on_spawn_enemies = None
        self.on_clear_enemies = None

        # Initialize wave generator
        from src.mechanics.wave_management.wave_generator import WaveGenerator
        self.wave_generator = WaveGenerator()

        # Initialize wave analytics
        from src.mechanics.wave_management.wave_analytics import WaveAnalytics
        self.wave_analytics = WaveAnalytics()

        # Initialize difficulty adjuster
        from src.mechanics.wave_management.difficulty_adjuster import DifficultyAdjuster
        self.difficulty_adjuster = DifficultyAdjuster()

    def update(self, delta_time):
        """Update the wave manager.

        Args:
            delta_time: Time since last update
        """
        # Update wave message fade
        if hasattr(self, 'wave_message_alpha') and self.wave_message_alpha > 0:
            self.wave_message_alpha -= delta_time * 0.5
            
        # Update wave timer
        if self.in_wave:
            self.wave_timer += delta_time

            # Check if wave is over
            if self.wave_timer >= self.wave_duration:
                print(f"🌊 Wave {self.wave} completed!")
                self.end_wave()

                # Display wave completion message
                self.wave_message = f"Wave {self.wave} Complete!"
                self.wave_message_alpha = 1.0

                # Start next wave after delay
                self.between_wave_timer = 0
                self.in_wave = False

                # Increment wave counter
                self.wave += 1
                # Keep current_wave in sync with wave
                self.current_wave = self.wave

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

    def _calculate_engagement_score(self):
        """
        Calculate player engagement score based on recent performance.
        Higher score = more engaged player who can handle more challenge.
        """
        # Default engagement if we don't have enough data
        if not hasattr(self, 'wave_analytics') or not hasattr(self.game_view, 'player'):
            return 0.5

        # Get basic stats
        player = self.game_view.player
        health_percent = getattr(player, 'health', 3) / getattr(player, 'max_health', 3)

        # Get recent performance metrics
        recent_score = getattr(self.game_view, 'score', 0)
        recent_deaths = getattr(player, 'deaths', 0)

        # Calculate engagement (0.0 to 1.0)
        # High engagement = player is doing well and can handle more challenge
        # Low engagement = player is struggling and needs easier content

        # Health factor (lower health = lower engagement)
        health_factor = health_percent

        # Score factor (higher score = higher engagement)
        score_factor = min(1.0, recent_score / 1000)

        # Death penalty (more deaths = lower engagement)
        death_penalty = max(0.0, 1.0 - (recent_deaths * 0.2))

        # Combine factors (adjust weights as needed)
        engagement = (health_factor * 0.4) + (score_factor * 0.4) + (death_penalty * 0.2)

        # Ensure result is between 0.0 and 1.0
        engagement = max(0.1, min(1.0, engagement))

        print(f"[ENGAGEMENT] Score: {engagement:.2f} (Health: {health_factor:.2f}, Score: {score_factor:.2f}, Deaths: {death_penalty:.2f})")

        return engagement

    def start_wave(self, wave_number=None):
        """Start a new wave of enemies."""
        if wave_number is not None:
            self.wave = wave_number
        else:
            self.wave += 1
            
        # Update current_wave alias
        self.current_wave = self.wave
        
        # Get player profile from game state
        player_profile = getattr(self.game_view, 'player_profile', {"playstyle": {}, "skill_level": 0.5})

        # Calculate engagement score based on recent performance
        engagement_score = self._calculate_engagement_score()

        # Generate wave configuration
        wave_config = self.wave_generator.create_wave(self.wave, player_profile, engagement_score)

        # Store wave configuration
        self.current_wave_config = wave_config

        # Set wave parameters from configuration
        self.wave_message = wave_config.get("message", f"Wave {self.wave}")
        self.wave_message_alpha = 1.0
        self.enemy_count = wave_config.get("enemy_count", 5)
        self.enemy_speed = wave_config.get("enemy_speed", 1.0)
        self.spawn_delay = wave_config.get("spawn_delay", 1.0)
        self.wave_duration = wave_config.get("duration", 30.0)
        self.enemy_types = wave_config.get("enemy_types", ["basic"])

        # Reset wave timers
        self.wave_timer = 0
        self.enemy_spawn_timer = 0
        self.in_wave = True

        # Start tracking wave statistics
        self.wave_analytics.start_wave_tracking(self.wave)

        print(f"Starting Wave {self.wave} with {self.enemy_count} enemies at speed {self.enemy_speed:.1f}")

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
        # Get wave statistics
        wave_stats = self.wave_analytics.get_wave_stats(self.wave)

        # Update player profile
        self.difficulty_adjuster.update_player_profile(self.game_view.player_profile, wave_stats)
        
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

    def end_wave(self):
        """End the current wave."""
        if self.on_clear_enemies:
            self.on_clear_enemies()

        print(f"Successfully passed wave {self.wave}!") 
        self.last_message_drawn = f"Successfully passed wave {self.wave}!"

        self.wave_timer = 0
        self.in_wave = False

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
            from src.mechanics.artifacts.dash_artifact import DashArtifact
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
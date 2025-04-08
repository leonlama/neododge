import random

class WaveManager:
    def __init__(self, player):
        self.wave = 1
        self.player = player
        self.wave_history = []
        self.last_message_drawn = ""

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

    def spawn_enemies(self, enemy_list, screen_width, screen_height):
        """Spawn enemies for the current wave"""
        from src.entities.enemies.enemy import Enemy
        from src.entities.enemies.chaser import ChaserEnemy
        #from src.entities.enemies.shooter_enemy import ShooterEnemy
        
        # Generate wave configuration
        wave_config = self.generate_wave(self.wave)
        
        # Clear existing enemies
        enemy_list.clear()
        
        # Spawn new enemies based on wave configuration
        for enemy_type in wave_config["enemy_types"]:
            # Random position away from player
            while True:
                x = random.randint(50, screen_width - 50)
                y = random.randint(50, screen_height - 50)
                
                # Make sure enemy doesn't spawn too close to player
                dx = x - self.player.center_x
                dy = y - self.player.center_y
                distance = (dx**2 + dy**2)**0.5
                
                if distance > 200:  # Minimum distance from player
                    break
            
            # Create appropriate enemy type
            if enemy_type == "basic":
                enemy = Enemy(x, y)
            elif enemy_type == "chaser":
                enemy = ChaserEnemy(x, y)
            elif enemy_type == "shooter":
                #enemy = ShooterEnemy(x, y)
                enemy = Enemy(x, y)  # Fallback to basic enemy
            elif enemy_type == "boss":
                # For now, use shooter as boss
                #enemy = ShooterEnemy(x, y)
                enemy = Enemy(x, y)  # Fallback to basic enemy
                enemy.scale = 1.5
                enemy.health = 5
            else:
                enemy = Enemy(x, y)
            
            # Apply wave parameters
            enemy.speed *= wave_config["enemy_params"]["speed"]
            if hasattr(enemy, "health"):
                enemy.health *= wave_config["enemy_params"]["health"]
            
            # Add to enemy list
            enemy_list.append(enemy)
        
        # Return the wave message
        return wave_config["message"]

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
            from src.mechanics.artifacts.dash_artifact import DashArtifact
            return DashArtifact(x, y)
        elif artifact_type == "magnet_pulse":
            from src.mechanics.artifacts.magnet_pulse import MagnetPulseArtifact
            return MagnetPulseArtifact(x, y)
        elif artifact_type == "slow_field":
            from src.mechanics.artifacts.slow_field import SlowFieldArtifact
            return SlowFieldArtifact(x, y)
        elif artifact_type == "bullet_time":
            from src.mechanics.artifacts.bullet_time import BulletTimeArtifact
            return BulletTimeArtifact(x, y)
        elif artifact_type == "clone_dash":
            from src.mechanics.artifacts.clone_dash import CloneDashArtifact
            return CloneDashArtifact(x, y)
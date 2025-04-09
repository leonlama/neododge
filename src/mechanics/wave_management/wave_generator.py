import random
import math
from src.mechanics.wave_management.difficulty_adjuster import DifficultyAdjuster
from src.mechanics.wave_management.formation_generator import FormationGenerator

class WaveGenerator:
    """Generates wave configurations based on wave number and player profile."""

    def __init__(self, wave_analytics):
        """Initialize the wave generator."""
        self.wave_analytics = wave_analytics
        self.formation_generator = FormationGenerator()
        self.difficulty_adjuster = DifficultyAdjuster()

    def create_wave(self, wave_number, player_profile=None, engagement_score=0.5):
        """Create a wave configuration based on wave number and player profile."""
        print(f"Creating wave {wave_number}")

        # Get difficulty parameters
        params = self.difficulty_adjuster.calculate_parameters(
            wave_number, 
            player_profile or {"skill_level": 0.5, "playstyle": {"aggression": 0.5}},
            engagement_score
        )

        # Determine wave type
        wave_type = self._determine_wave_type(wave_number)
        print(f"Wave type: {wave_type}")

        # Create wave based on type
        if wave_type == "boss":
            wave = self._create_boss_wave(wave_number, params)
        elif wave_type == "swarm":
            wave = self._create_swarm_wave(wave_number, params)
        elif wave_type == "rest":
            wave = self._create_rest_wave(wave_number, params)
        else:  # normal
            wave = self._create_normal_wave(wave_number, params, player_profile)

        print(f"Wave configuration: {wave}")
        return wave

    def _determine_wave_type(self, wave_number, player_profile=None):
        """Determine what type of wave to generate"""
        if wave_number % 6 == 0:  # Every 6th wave is a rest wave
            return "rest"
        elif wave_number % 10 == 0:  # Every 10th wave is a boss wave
            return "boss"
        elif wave_number % 7 == 0:  # Every 7th wave is a swarm wave
            return "swarm"
        else:
            return "normal"

    def _create_rest_wave(self, wave_number, params):
        """Create a rest wave with minimal enemies"""
        return {
            "type": "rest",
            "wave_number": wave_number,
            "difficulty": 0.3,
            "enemy_count": 2,
            "enemy_types": ["wander", "wander"],
            "enemy_speed": 0.7,
            "enemy_health": 0.8,
            "spawn_delay": 2.0,
            "duration": 30.0,
            "orb_count": 1,
            "orb_types": {"buff": 1.0, "debuff": 0.0},
            "spawn_artifact": False,
            "coin_count": random.randint(5, 10),
            "message": "Rest Wave - Catch your breath!"
        }

    def _create_boss_wave(self, wave_number, params):
        """Create a boss wave with a powerful enemy."""
        return {
            "type": "boss",
            "wave_number": wave_number,
            "difficulty": params["difficulty"] * 1.2,
            "enemy_count": 1,
            "enemy_types": ["boss"],
            "boss_type": self._determine_boss_type(wave_number),
            "enemy_speed": params["enemy_speed"] * 0.8,
            "enemy_health": params["enemy_health"] * 5.0,
            "spawn_delay": 0.0,
            "duration": 90.0,
            "orb_count": params["orb_count"] + 1,
            "orb_types": params["orb_types"],
            "spawn_artifact": True,
            "coin_count": random.randint(30, 50 + wave_number * 2),
            "message": f"Boss Wave {wave_number//10} - Prepare for a challenge!"
        }

    def _determine_boss_type(self, wave_number):
        """Determine which boss type to spawn based on wave number."""
        boss_tier = min(3, wave_number // 10)
        boss_types = ["mini_boss", "mid_boss", "final_boss", "ultra_boss"]
        return boss_types[boss_tier]

    def _create_swarm_wave(self, wave_number, params):
        """Create a wave with many weak enemies."""
        return {
            "type": "swarm",
            "wave_number": wave_number,
            "difficulty": params["difficulty"],
            "enemy_count": params["enemy_count"] * 2,
            "enemy_types": ["wander"] * (params["enemy_count"] * 2),
            "enemy_speed": params["enemy_speed"] * 1.2,
            "enemy_health": params["enemy_health"] * 0.6,
            "formation": "random",
            "spawn_delay": 0.2,
            "duration": 40.0,
            "orb_count": params["orb_count"],
            "orb_types": params["orb_types"],
            "spawn_artifact": params["spawn_artifact"],
            "coin_count": random.randint(15, 25 + wave_number),
            "message": "Swarm Wave - They're everywhere!"
        }

    def _create_normal_wave(self, wave_number, params, player_profile):
        """Create a standard wave with varied enemies."""
        formation = random.choice(["circle", "line", "random", "grid", "v_shape"])

        # Distribute enemy types according to the distribution in params
        enemy_types = []
        for _ in range(params["enemy_count"]):
            enemy_type = random.choices(
                list(params["enemy_types"].keys()),
                weights=list(params["enemy_types"].values())
            )[0]
            enemy_types.append(enemy_type)

        return {
            "type": "normal",
            "wave_number": wave_number,
            "difficulty": params["difficulty"],
            "enemy_count": params["enemy_count"],
            "enemy_types": enemy_types,
            "enemy_speed": params["enemy_speed"],
            "enemy_health": params["enemy_health"],
            "formation": formation,
            "spawn_delay": max(0.2, 1.0 - (params["difficulty"] * 0.5)),
            "duration": 45.0 + (wave_number * 0.5),
            "orb_count": params["orb_count"],
            "orb_types": params["orb_types"],
            "spawn_artifact": params["spawn_artifact"],
            "coin_count": random.randint(10, 20 + wave_number),
        }

    def _calculate_coins(self, wave_number, difficulty):
        """Calculate number of coins based on wave number and difficulty"""
        base_coins = 3 + (wave_number // 3)
        difficulty_bonus = int(difficulty * 5)
        return random.randint(base_coins, base_coins + difficulty_bonus)

    def _weighted_choice(self, weights_dict):
        """Choose a random item based on weights."""
        if not weights_dict:
            return "basic"  # Default

        items = list(weights_dict.keys())
        weights = list(weights_dict.values())

        # Normalize weights if they don't sum to 1
        total = sum(weights)
        if total != 1.0:
            weights = [w/total for w in weights]

        # Choose a random item based on weights
        r = random.random()
        cumulative_weight = 0
        for i, weight in enumerate(weights):
            cumulative_weight += weight
            if r <= cumulative_weight:
                return items[i]

        # Fallback
        return items[-1]
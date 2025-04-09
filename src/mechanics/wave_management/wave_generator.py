import random
import math
from src.mechanics.wave_management.difficulty_adjuster import DifficultyAdjuster
from src.mechanics.wave_management.formation_generator import FormationGenerator

class WaveGenerator:
    """Generates wave configurations based on wave number and player profile."""

    def __init__(self):
        """Initialize the wave generator."""
        self.formation_generator = FormationGenerator()
        self.difficulty_adjuster = DifficultyAdjuster()

    def create_wave(self, wave_number, player_profile, engagement_score):
        """
        Create a wave configuration based on wave number and player profile.

        Args:
            wave_number: The current wave number
            player_profile: Dictionary containing player playstyle data
            engagement_score: Player engagement score (0.0 to 1.0)

        Returns:
            Dictionary containing wave configuration
        """
        # Calculate difficulty parameters
        params = self.difficulty_adjuster.calculate_parameters(wave_number, player_profile, engagement_score)

        # Determine wave type
        wave_type = self._determine_wave_type(wave_number, player_profile)

        if wave_type == "rest":
            return self._create_rest_wave(wave_number, params)
        elif wave_type == "boss":
            return self._create_boss_wave(wave_number, params)
        elif wave_type == "swarm":
            return self._create_swarm_wave(wave_number, params)
        else:  # "normal"
            return self._create_normal_wave(wave_number, params, player_profile)

    def _determine_wave_type(self, wave_number, player_profile):
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
        """Create a boss wave with a powerful boss enemy and some minions"""
        # Boss waves have a boss and some minions
        enemy_count = 1 + math.ceil(wave_number / 10)  # More minions in later boss waves

        # Create a mix of boss and minion enemy types
        enemy_types = ["boss"]
        for _ in range(enemy_count - 1):
            enemy_types.append(random.choice(["basic", "chaser"]))

        return {
            "type": "boss",
            "wave_number": wave_number,
            "difficulty": 0.8,
            "enemy_count": enemy_count,
            "enemy_types": enemy_types,
            "enemy_speed": 0.9,
            "enemy_health": 5.0,
            "spawn_delay": 3.0,
            "duration": 60.0,
            "orb_count": params.get("orb_count", 2),
            "orb_types": params.get("orb_types", {"buff": 1.0, "debuff": 0.0}),
            "spawn_artifact": True,
            "coin_count": random.randint(10, 15),
            "message": f"Boss Wave {wave_number//10} - Good luck!"
        }

    def _create_swarm_wave(self, wave_number, params):
        """Create a swarm wave with many weak enemies"""
        enemy_count = min(40, params.get("enemy_count", 10) * 2)

        return {
            "type": "swarm",
            "wave_number": wave_number,
            "difficulty": 0.6,
            "enemy_count": enemy_count,
            "enemy_types": ["wander"] * enemy_count,
            "enemy_speed": 1.2,
            "enemy_health": 0.6,
            "spawn_delay": 0.3,
            "duration": 45.0,
            "orb_count": params.get("orb_count", 2),
            "orb_types": params.get("orb_types", {"buff": 0.7, "debuff": 0.3}),
            "spawn_artifact": params.get("spawn_artifact", False),
            "coin_count": random.randint(5, 10),
            "message": "Swarm Wave - They're everywhere!"
        }

    def _create_normal_wave(self, wave_number, params, player_profile):
        """Create a standard wave with varied enemies"""
        enemy_count = params.get("enemy_count", 5)

        # Determine enemy types based on wave number
        enemy_types = []
        available_types = ["basic"]

        # Add more enemy types as waves progress
        if wave_number >= 3:
            available_types.append("chaser")
        if wave_number >= 5:
            available_types.append("shooter")

        # Create a mix of enemy types
        for _ in range(enemy_count):
            enemy_type = random.choice(available_types)
            enemy_types.append(enemy_type)

        # Generate formation if available
        formation = None
        if hasattr(self, 'formation_generator') and self.formation_generator:
            formation = self.formation_generator.generate_formation(
                enemy_types,
                player_profile.get("playstyle", {}).get("aggression", 0.5),
                params.get("difficulty", 0.5)
            )

        return {
            "type": "normal",
            "wave_number": wave_number,
            "difficulty": params.get("difficulty", 0.5),
            "enemy_count": enemy_count,
            "enemy_types": enemy_types,
            "enemy_speed": params.get("enemy_speed", 1.0),
            "enemy_health": params.get("enemy_health", 1.0),
            "formation": formation,
            "spawn_delay": 1.0,
            "duration": 45.0,
            "orb_count": params.get("orb_count", 1),
            "orb_types": params.get("orb_types", {"buff": 0.8, "debuff": 0.2}),
            "spawn_artifact": params.get("spawn_artifact", False),
            "coin_count": self._calculate_coins(wave_number, params.get("difficulty", 0.5)),
            "message": f"Wave {wave_number}"
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
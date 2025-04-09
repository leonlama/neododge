import random
from src.mechanics.wave_management.enemy_formation import FormationGenerator
from src.mechanics.wave_management.difficulty_adjuster import DifficultyAdjuster

class WaveGenerator:
    def __init__(self):
        self.formation_generator = FormationGenerator()
        self.difficulty_adjuster = DifficultyAdjuster()

    def create_wave(self, wave_number, player_profile, engagement_score):
        """Create a complete wave configuration"""
        # Calculate difficulty parameters
        params = self.difficulty_adjuster.calculate_parameters(wave_number, player_profile, engagement_score)
        
        # Determine wave type
        wave_type = self._determine_wave_type(wave_number, player_profile)

        if wave_type == "rest":
            return self._create_rest_wave(wave_number)
        elif wave_type == "boss":
            return self._create_boss_wave(wave_number, params)
        elif wave_type == "swarm":
            return self._create_swarm_wave(wave_number, params)
        else:  # "normal"
            return self._create_normal_wave(wave_number, params, player_profile)

    def _determine_wave_type(self, wave_number, player_profile):
        """Determine what type of wave to generate"""
        if wave_number % 6 == 0:
            return "rest"
        elif wave_number % 10 == 0:
            return "boss"
        elif wave_number % 7 == 0:
            return "swarm"
        else:
            return "normal"

    def _create_rest_wave(self, wave_number):
        """Create a rest wave with minimal enemies"""
        return {
            "type": "rest",
            "enemies": 2,
            "enemy_types": ["wander", "wander"],
            "enemy_params": {"speed": 0.7, "health": 0.8},
            "orbs": 1,
            "orb_types": {"buff": 1.0, "debuff": 0.0},
            "artifact": False,
            "coins": random.randint(3, 7),
            "message": "Rest Wave - Catch your breath!"
        }

    def _create_boss_wave(self, wave_number, params):
        """Create a boss wave with a powerful enemy"""
        return {
            "type": "boss",
            "enemies": 1,
            "enemy_types": ["boss"],
            "enemy_params": {
                "speed": 0.9, 
                "health": 5.0,
                "attack_pattern": random.choice(["circle", "spiral", "targeted"])
            },
            "orbs": params["orb_count"],
            "orb_types": params["orb_types"],
            "artifact": params["spawn_artifact"],
            "coins": random.randint(10, 15),
            "message": f"Boss Wave {wave_number//10} - Good luck!"
        }

    def _create_swarm_wave(self, wave_number, params):
        """Create a swarm wave with many weak enemies"""
        enemy_count = min(40, params["enemy_count"] * 2)
        return {
            "type": "swarm",
            "enemies": enemy_count,
            "enemy_types": ["wander"] * enemy_count,
            "enemy_params": {"speed": 1.2, "health": 0.6},
            "orbs": params["orb_count"],
            "orb_types": params["orb_types"],
            "artifact": params["spawn_artifact"],
            "coins": random.randint(5, 10),
            "message": "Swarm Wave - They're everywhere!"
        }

    def _create_normal_wave(self, wave_number, params, player_profile):
        """Create a standard wave with varied enemies"""
        enemy_count = params["enemy_count"]

        # Determine enemy types based on distribution
        enemy_types = []
        for _ in range(enemy_count):
            enemy_type = self._weighted_choice(params["enemy_types"])
            enemy_types.append(enemy_type)

        # Generate enemy formation
        formation = self.formation_generator.generate_formation(
            enemy_types,
            player_profile["playstyle"],
            params["difficulty"]
        )

        return {
            "type": "normal",
            "enemies": enemy_count,
            "enemy_types": enemy_types,
            "enemy_params": {
                "speed": params["enemy_speed"],
                "health": params["enemy_health"]
            },
            "formation": formation,
            "orbs": params["orb_count"],
            "orb_types": params["orb_types"],
            "artifact": params["spawn_artifact"],
            "coins": self._calculate_coins(wave_number, params["difficulty"]),
            "message": f"Wave {wave_number}"
        }
    
    def _weighted_choice(self, weights_dict):
        """Choose a random item based on weights."""
        if not weights_dict:
            return "chaser"  # Default

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
        
    def _calculate_coins(self, wave_number, difficulty):
        """Calculate number of coins based on wave number and difficulty"""
        base_coins = 3 + (wave_number // 3)
        difficulty_bonus = int(difficulty * 5)
        return random.randint(base_coins, base_coins + difficulty_bonus)
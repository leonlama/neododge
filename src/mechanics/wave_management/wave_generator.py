import random
from src.mechanics.wave_management.enemy_formation import FormationGenerator

class WaveGenerator:
    def __init__(self):
        self.formation_generator = FormationGenerator()

    def create_wave(self, wave_number, difficulty_params, player_profile):
        """Create a complete wave configuration"""
        # Determine wave type
        wave_type = self._determine_wave_type(wave_number, player_profile)

        if wave_type == "rest":
            return self._create_rest_wave(wave_number)
        elif wave_type == "boss":
            return self._create_boss_wave(wave_number, difficulty_params)
        elif wave_type == "swarm":
            return self._create_swarm_wave(wave_number, difficulty_params)
        else:  # "normal"
            return self._create_normal_wave(wave_number, difficulty_params, player_profile)

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

    def _create_boss_wave(self, wave_number, difficulty_params):
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
            "orbs": 2,
            "orb_types": {"buff": 0.9, "debuff": 0.1},
            "artifact": True,
            "coins": random.randint(10, 15),
            "message": f"Boss Wave {wave_number//10} - Good luck!"
        }

    def _create_swarm_wave(self, wave_number, difficulty_params):
        """Create a swarm wave with many weak enemies"""
        enemy_count = min(40, difficulty_params["enemy_count"] * 2)
        return {
            "type": "swarm",
            "enemies": enemy_count,
            "enemy_types": ["wander"] * enemy_count,
            "enemy_params": {"speed": 1.2, "health": 0.6},
            "orbs": difficulty_params["orb_count"],
            "orb_types": difficulty_params["orb_types"],
            "artifact": False,
            "coins": random.randint(5, 10),
            "message": "Swarm Wave - They're everywhere!"
        }

    def _create_normal_wave(self, wave_number, difficulty_params, player_profile):
        """Create a standard wave with varied enemies"""
        enemy_count = difficulty_params["enemy_count"]

        # Determine enemy types based on distribution
        enemy_types = []
        for _ in range(enemy_count):
            enemy_type = self._weighted_choice(difficulty_params["enemy_types"])
            enemy_types.append(enemy_type)

        # Generate enemy formation
        formation = self.formation_generator.generate_formation(
            enemy_types,
            player_profile["playstyle"],
            difficulty_params["difficulty"]
        )

        return {
            "type": "normal",
            "enemies": enemy_count,
            "enemy_types": enemy_types,
            "enemy_params": {
                "speed": difficulty_params["enemy_speed"],
                "health": difficulty_params["enemy_health"]
            },
            "formation": formation,
            "orbs": difficulty_params["orb_count"],
            "orb_types": difficulty_params["orb_types"],
            "artifact": difficulty_params["spawn_artifact"],
            "coins": random.randint(3, 8),
            "message": f"Wave {wave_number}"
        }
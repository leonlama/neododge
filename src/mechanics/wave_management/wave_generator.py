import random

class WaveGenerator:
    """Generates wave configurations based on wave number and player profile."""

    def __init__(self):
        """Initialize the wave generator."""
        pass

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
        # Default configuration
        config = {
            "type": "normal",
            "message": f"Wave {wave_number}",
            "enemy_count": 5 + (wave_number * 2),
            "enemy_speed": 1.0 + (wave_number * 0.1),
            "spawn_delay": max(0.5, 2.0 - (wave_number * 0.1)),
            "enemy_types": ["basic"],
            "duration": 30.0
        }

        # Every 5th wave is a boss wave
        if wave_number % 5 == 0:
            config["type"] = "boss"
            config["message"] = f"Boss Wave {wave_number}"
            config["enemy_count"] = 1 + (wave_number // 10)
            config["enemy_types"] = ["boss"]
            config["duration"] = 60.0

        # Every 3rd wave (not divisible by 5) is a swarm wave
        elif wave_number % 3 == 0:
            config["type"] = "swarm"
            config["message"] = f"Swarm Wave {wave_number}"
            config["enemy_count"] = 10 + (wave_number * 3)
            config["enemy_speed"] = 0.8 + (wave_number * 0.05)
            config["spawn_delay"] = max(0.2, 1.0 - (wave_number * 0.05))

        # Adjust based on engagement score
        if engagement_score < 0.3:
            # Player is struggling, make it easier
            config["enemy_count"] = max(3, int(config["enemy_count"] * 0.7))
            config["enemy_speed"] = max(0.8, config["enemy_speed"] * 0.8)
            config["spawn_delay"] = min(3.0, config["spawn_delay"] * 1.5)
        elif engagement_score > 0.7:
            # Player is doing well, make it harder
            config["enemy_count"] = int(config["enemy_count"] * 1.3)
            config["enemy_speed"] = config["enemy_speed"] * 1.2
            config["spawn_delay"] = max(0.3, config["spawn_delay"] * 0.8)

        # Add some randomness
        config["enemy_count"] += random.randint(-2, 2)
        config["enemy_speed"] += random.uniform(-0.1, 0.1)

        # Ensure values are within reasonable bounds
        config["enemy_count"] = max(1, config["enemy_count"])
        config["enemy_speed"] = max(0.5, min(5.0, config["enemy_speed"]))
        config["spawn_delay"] = max(0.1, min(5.0, config["spawn_delay"]))

        print(f"[WAVE GENERATOR] Created {config['type']} wave with {config['enemy_count']} enemies")

        return config
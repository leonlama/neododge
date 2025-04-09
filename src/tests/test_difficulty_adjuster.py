import pytest
from src.mechanics.wave_management.difficulty_adjuster import DifficultyAdjuster

class TestDifficultyAdjuster:
    def test_difficulty_scaling(self):
        """Test that difficulty scales with wave number."""
        adjuster = DifficultyAdjuster()

        # Create a simple player profile
        player_profile = {"skill_level": 0.5, "playstyle": {"aggression": 0.5}}

        # Test early wave
        params_wave1 = adjuster.calculate_parameters(1, player_profile, 0.5)

        # Test later wave
        params_wave10 = adjuster.calculate_parameters(10, player_profile, 0.5)

        assert params_wave10["difficulty"] > params_wave1["difficulty"]
        assert params_wave10["enemy_count"] > params_wave1["enemy_count"]

    def test_player_skill_adjustment(self):
        """Test that difficulty adjusts based on player skill."""
        adjuster = DifficultyAdjuster()

        # Low skill player
        low_skill = {"skill_level": 0.2, "playstyle": {"aggression": 0.5}}
        params_low = adjuster.calculate_parameters(5, low_skill, 0.5)

        # High skill player
        high_skill = {"skill_level": 0.8, "playstyle": {"aggression": 0.5}}
        params_high = adjuster.calculate_parameters(5, high_skill, 0.5)

        assert params_high["difficulty"] > params_low["difficulty"]
import unittest
import sys
import os
from unittest.mock import MagicMock, patch

# Add the src directory to the path so imports work correctly
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))

from src.mechanics.wave_management.wave_manager import WaveManager
from src.mechanics.wave_management.wave_analytics import PlayerAnalytics
from src.mechanics.wave_management.wave_generator import WaveGenerator
from src.mechanics.wave_management.difficulty_adjuster import DifficultyAdjuster

class TestWaveGeneration(unittest.TestCase):
    def setUp(self):
        # Create a mock player
        self.player = MagicMock()
        self.player.center_x = 400
        self.player.center_y = 300
        self.player.change_x = 0
        self.player.change_y = 0
        self.player.artifacts = []

        # Create the wave management components
        self.wave_manager = WaveManager(self.player)

    def test_wave_manager_initialization(self):
        """Test that the wave manager initializes correctly"""
        self.assertEqual(self.wave_manager.wave, 1)
        self.assertEqual(self.wave_manager.player, self.player)
        self.assertIsInstance(self.wave_manager.analytics, PlayerAnalytics)
        self.assertIsInstance(self.wave_manager.difficulty, DifficultyAdjuster)
        self.assertIsInstance(self.wave_manager.generator, WaveGenerator)

    def test_generate_normal_wave(self):
        """Test generation of a normal wave"""
        # Set up for a normal wave (not a rest, boss, or swarm wave)
        self.wave_manager.wave = 2  # Wave 2 should be a normal wave

        wave_config = self.wave_manager.generate_wave(self.wave_manager.wave)

        # Verify the wave has the expected structure
        self.assertEqual(wave_config["type"], "normal")
        self.assertIn("enemies", wave_config)
        self.assertIn("enemy_types", wave_config)
        self.assertIn("orbs", wave_config)

        # Check that enemy count is reasonable
        self.assertGreaterEqual(len(wave_config["enemy_types"]), 3)  # At least 3 enemies in wave 2

    def test_generate_rest_wave(self):
        """Test generation of a rest wave"""
        # Set up for a rest wave
        self.wave_manager.wave = 6  # Wave 6 should be a rest wave

        wave_config = self.wave_manager.generate_wave(self.wave_manager.wave)

        # Verify it's a rest wave
        self.assertEqual(wave_config["type"], "rest")
        self.assertEqual(len(wave_config["enemy_types"]), 2)  # Rest waves have 2 enemies
        self.assertEqual(wave_config["enemy_types"], ["wander", "wander"])

    def test_generate_boss_wave(self):
        """Test generation of a boss wave"""
        # Set up for a boss wave
        self.wave_manager.wave = 10  # Wave 10 should be a boss wave

        wave_config = self.wave_manager.generate_wave(self.wave_manager.wave)

        # Verify it's a boss wave
        self.assertEqual(wave_config["type"], "boss")
        self.assertEqual(len(wave_config["enemy_types"]), 1)  # Boss waves have 1 enemy
        self.assertEqual(wave_config["enemy_types"], ["boss"])

    def test_generate_swarm_wave(self):
        """Test generation of a swarm wave"""
        # Set up for a swarm wave
        self.wave_manager.wave = 7  # Wave 7 should be a swarm wave

        wave_config = self.wave_manager.generate_wave(self.wave_manager.wave)

        # Verify it's a swarm wave
        self.assertEqual(wave_config["type"], "swarm")
        self.assertGreater(len(wave_config["enemy_types"]), 10)  # Swarm waves have many enemies

    def test_difficulty_progression(self):
        """Test that difficulty increases with wave number"""
        # Generate waves at different points
        wave1 = self.wave_manager.generate_wave(1)
        wave5 = self.wave_manager.generate_wave(5)
        wave15 = self.wave_manager.generate_wave(15)

        # Check enemy parameters increase with wave number
        if wave1["type"] == "normal" and wave5["type"] == "normal" and wave15["type"] == "normal":
            self.assertLess(wave1["enemy_params"]["speed"], wave15["enemy_params"]["speed"])
            self.assertLess(wave1["enemy_params"]["health"], wave15["enemy_params"]["health"])

    def test_player_analytics_integration(self):
        """Test that player analytics affect wave generation"""
        # Mock the player analytics to simulate an aggressive player
        aggressive_profile = {
            "skill_level": 0.7,
            "playstyle": {
                "aggression": 0.8,
                "caution": 0.1,
                "balance": 0.1
            },
            "preferences": {
                "dash_frequency": 0.5,
                "orb_preference": {},
                "artifact_usage": {}
            },
            "engagement": 0.9
        }

        self.wave_manager.analytics.get_player_profile = MagicMock(return_value=aggressive_profile)

        # Generate a wave for this aggressive player
        wave_config = self.wave_manager.generate_wave(3)

        # For aggressive players, we expect more defensive enemies (shooters)
        if wave_config["type"] == "normal":
            enemy_types = wave_config["enemy_types"]
            shooter_count = enemy_types.count("shooter") if "shooter" in enemy_types else 0
            self.assertGreater(shooter_count, 0)

    def test_wave_history_tracking(self):
        """Test that wave history is properly tracked"""
        # Generate a few waves
        self.wave_manager.generate_wave(1)
        self.wave_manager.generate_wave(2)
        self.wave_manager.generate_wave(3)

        # Check that history is being recorded
        self.assertEqual(len(self.wave_manager.wave_history), 3)
        self.assertEqual(self.wave_manager.wave_history[0]["wave_number"], 1)
        self.assertEqual(self.wave_manager.wave_history[1]["wave_number"], 2)
        self.assertEqual(self.wave_manager.wave_history[2]["wave_number"], 3)

    def test_end_wave_analysis(self):
        """Test the end-of-wave analysis"""
        # Mock the analytics to return specific wave stats
        mock_stats = {
            "damage_taken": 2,
            "enemies_defeated": 5,
            "orbs_collected": 1,
            "survival_time": 25
        }
        self.wave_manager.analytics.analyze_wave_performance = MagicMock(return_value=mock_stats)
        self.wave_manager.analytics.calculate_engagement_score = MagicMock(return_value=0.8)

        # Run the end wave analysis
        stats = self.wave_manager.end_wave_analysis()

        # Verify the analysis was performed
        self.assertEqual(stats, mock_stats)
        self.assertEqual(self.wave_manager.engagement_score, 0.8)

        # Verify the difficulty adjuster was called
        self.wave_manager.difficulty.adjust_based_on_performance.assert_called_once_with(mock_stats)

if __name__ == '__main__':
    unittest.main()
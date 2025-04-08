from src.mechanics.wave_management.wave_analytics import PlayerAnalytics
from src.mechanics.wave_management.wave_generator import WaveGenerator
from src.mechanics.wave_management.difficulty_adjuster import DifficultyAdjuster

class WaveManager:
    def __init__(self, player):
        self.wave = 1
        self.player = player
        self.analytics = PlayerAnalytics(player)
        self.difficulty = DifficultyAdjuster()
        self.generator = WaveGenerator()

        # Wave history for analysis
        self.wave_history = []

        # Player engagement metrics
        self.engagement_score = 0.5  # 0.0 to 1.0

    def generate_wave(self, wave_number):
        # Analyze player performance
        player_profile = self.analytics.get_player_profile()

        # Adjust difficulty based on player performance
        difficulty_params = self.difficulty.calculate_parameters(
            wave_number, 
            player_profile,
            self.engagement_score
        )

        # Generate wave with appropriate challenge level
        wave_config = self.generator.create_wave(
            wave_number,
            difficulty_params,
            player_profile
        )

        # Store wave for later analysis
        self.wave_history.append({
            "wave_number": wave_number,
            "config": wave_config,
            "player_state": player_profile
        })

        return wave_config

    def update_analytics(self, delta_time):
        """Update player analytics during gameplay"""
        self.analytics.update(delta_time)

    def end_wave_analysis(self):
        """Analyze player performance after wave completion"""
        wave_stats = self.analytics.analyze_wave_performance()
        self.engagement_score = self.analytics.calculate_engagement_score()
        self.difficulty.adjust_based_on_performance(wave_stats)
        return wave_stats
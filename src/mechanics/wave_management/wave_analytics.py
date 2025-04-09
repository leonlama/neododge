import arcade
import numpy as np
from collections import deque

class WaveAnalytics:
    """Track statistics for waves to help with balancing"""

    def __init__(self):
        self.wave_stats = {}

    def initialize_wave(self, wave_number):
        """Initialize stats for a new wave"""
        self.wave_stats[wave_number] = {
            "enemies_spawned": 0,
            "enemies_killed": 0,
            "player_damage_taken": 0,
            "orbs_collected": 0,
            "coins_collected": 0,
            "time_to_complete": 0,
            "player_position_heatmap": [],  # Track where player spends time
        }

    def update_wave_stat(self, wave_number, stat_name, value):
        """Update a specific stat for a wave"""
        if wave_number not in self.wave_stats:
            self.initialize_wave(wave_number)

        if stat_name in self.wave_stats[wave_number]:
            self.wave_stats[wave_number][stat_name] += value
        else:
            self.wave_stats[wave_number][stat_name] = value

    def record_player_position(self, wave_number, x, y):
        """Record player position for heatmap"""
        if wave_number not in self.wave_stats:
            self.initialize_wave(wave_number)

        self.wave_stats[wave_number]["player_position_heatmap"].append((x, y))

    def get_wave_summary(self, wave_number):
        """Get a summary of wave statistics"""
        if wave_number not in self.wave_stats:
            return None

        stats = self.wave_stats[wave_number]

        # Calculate derived stats
        kill_ratio = stats["enemies_killed"] / max(1, stats["enemies_spawned"])

        return {
            "wave_number": wave_number,
            "kill_ratio": kill_ratio,
            "damage_taken": stats["player_damage_taken"],
            "orbs_collected": stats["orbs_collected"],
            "coins_collected": stats["coins_collected"],
            "time_to_complete": stats["time_to_complete"]
        }

    def get_difficulty_recommendation(self):
        """Analyze performance and recommend difficulty adjustments"""
        if not self.wave_stats:
            return 0  # No change

        recent_waves = sorted(self.wave_stats.keys())[-3:]  # Last 3 waves

        # Calculate average kill ratio for recent waves
        avg_kill_ratio = 0
        for wave in recent_waves:
            stats = self.wave_stats[wave]
            kill_ratio = stats["enemies_killed"] / max(1, stats["enemies_spawned"])
            avg_kill_ratio += kill_ratio

        avg_kill_ratio /= len(recent_waves)

        # Recommend difficulty changes
        if avg_kill_ratio > 0.9:
            return 0.05  # Increase difficulty
        elif avg_kill_ratio < 0.5:
            return -0.03  # Decrease difficulty

        return 0  # No change

class PlayerAnalytics:
    def __init__(self, player):
        self.player = player

        # Performance metrics
        self.damage_taken_history = deque(maxlen=5)  # Last 5 waves
        self.close_calls = 0  # Near misses with enemies
        self.avg_reaction_time = 0.5  # seconds
        self.movement_patterns = {
            "aggressive": 0,
            "defensive": 0,
            "balanced": 0
        }

        # Playstyle detection
        self.dash_frequency = 0
        self.orb_preference = {}
        self.artifact_usage = {}

        # Engagement metrics
        self.idle_time = 0
        self.active_time = 0

    def update(self, delta_time):
        """Update analytics during gameplay"""
        # Track movement patterns
        if self.player.change_x != 0 or self.player.change_y != 0:
            self.active_time += delta_time

            # Analyze movement style
            if self._is_moving_toward_enemies():
                self.movement_patterns["aggressive"] += delta_time
            elif self._is_moving_away_from_enemies():
                self.movement_patterns["defensive"] += delta_time
            else:
                self.movement_patterns["balanced"] += delta_time
        else:
            self.idle_time += delta_time

        # Detect close calls (near misses)
        self._detect_close_calls()

    def _is_moving_toward_enemies(self):
        # Implementation would check if player is moving toward nearest enemies
        return False

    def _is_moving_away_from_enemies(self):
        # Implementation would check if player is moving away from enemies
        return False

    def _detect_close_calls(self):
        # Implementation would detect when player narrowly avoids enemies
        pass

    def get_player_profile(self):
        """Return a profile of the player's playstyle and skill"""
        total_movement = sum(self.movement_patterns.values()) or 1

        return {
            "skill_level": self._calculate_skill_level(),
            "playstyle": {
                "aggression": self.movement_patterns["aggressive"] / total_movement,
                "caution": self.movement_patterns["defensive"] / total_movement,
                "balance": self.movement_patterns["balanced"] / total_movement
            },
            "preferences": {
                "dash_frequency": self.dash_frequency,
                "orb_preference": self.orb_preference,
                "artifact_usage": self.artifact_usage
            },
            "engagement": self._calculate_engagement()
        }

    def _calculate_skill_level(self):
        """Calculate player skill on a scale of 0.0 to 1.0"""
        # Implementation would consider damage taken, survival time, etc.
        return 0.5

    def _calculate_engagement(self):
        """Calculate player engagement on a scale of 0.0 to 1.0"""
        total_time = self.active_time + self.idle_time or 1
        return min(1.0, self.active_time / total_time)

    def analyze_wave_performance(self):
        """Analyze performance for the just-completed wave"""
        # Implementation would analyze various metrics
        return {
            "damage_taken": 0,
            "enemies_defeated": 0,
            "orbs_collected": 0,
            "survival_time": 0
        }

    def calculate_engagement_score(self):
        """Calculate how engaged the player seems to be"""
        # A more sophisticated implementation would consider multiple factors
        return self._calculate_engagement()
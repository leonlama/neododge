import arcade
import numpy as np
from collections import deque

class WaveAnalytics:
    """Tracks and analyzes wave statistics."""

    def __init__(self):
        """Initialize the wave analytics."""
        self.wave_stats = {}

    def start_wave_tracking(self, wave_number):
        """Start tracking statistics for a wave."""
        self.wave_stats[wave_number] = {
            "enemies_spawned": 0,
            "enemies_killed": 0,
            "damage_taken": 0,
            "coins_collected": 0,
            "orbs_collected": 0,
            "start_time": 0,
            "end_time": 0,
            "duration": 0
        }

    def update_wave_stat(self, wave_number, stat_name, value):
        """Update a specific statistic for a wave."""
        if wave_number in self.wave_stats:
            if stat_name in self.wave_stats[wave_number]:
                self.wave_stats[wave_number][stat_name] += value
            else:
                self.wave_stats[wave_number][stat_name] = value

    def get_wave_stats(self, wave_number):
        """Get statistics for a specific wave."""
        return self.wave_stats.get(wave_number, {})

    def get_recent_stats(self, num_waves=3):
        """Get aggregated statistics for the most recent waves."""
        recent_stats = {
            "enemies_spawned": 0,
            "enemies_killed": 0,
            "damage_taken": 0,
            "coins_collected": 0,
            "orbs_collected": 0,
            "avg_duration": 0
        }

        # Get the most recent wave numbers
        wave_numbers = sorted(self.wave_stats.keys())
        if len(wave_numbers) > num_waves:
            wave_numbers = wave_numbers[-num_waves:]

        if not wave_numbers:
            return recent_stats

        # Aggregate stats
        for wave in wave_numbers:
            stats = self.wave_stats[wave]
            recent_stats["enemies_spawned"] += stats.get("enemies_spawned", 0)
            recent_stats["enemies_killed"] += stats.get("enemies_killed", 0)
            recent_stats["damage_taken"] += stats.get("damage_taken", 0)
            recent_stats["coins_collected"] += stats.get("coins_collected", 0)
            recent_stats["orbs_collected"] += stats.get("orbs_collected", 0)
            recent_stats["avg_duration"] += stats.get("duration", 0)

        # Calculate averages
        recent_stats["avg_duration"] /= len(wave_numbers)

        return recent_stats

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
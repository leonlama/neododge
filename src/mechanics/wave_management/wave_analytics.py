import numpy as np
from collections import deque

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
"""
Singleton class to manage global game state.
Provides centralized access to player stats, progress, and settings.
"""
import json
import os
import appdirs

class GameState:
    """
    Manages global game state including score, player stats, and unlocks.
    Uses singleton pattern to ensure consistent access across the application.
    """
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(GameState, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        """Initialize default game state values"""
        # Game session state
        self.score = 0
        self.coins = 0
        self.current_wave = 1
        self.wave_timer = 0
        self.game_active = False

        # Player stats
        self.player_stats = {
            "max_health": 3,
            "speed": 1.0,
            "orb_rate": 1.0,
            "coin_rate": 1.0,
            "damage_absorption": 0.0
        }

        # Persistence
        self.app_name = "Neododge"
        self.user_data_dir = os.path.join(appdirs.user_data_dir(self.app_name), "data")
        os.makedirs(self.user_data_dir, exist_ok=True)
        self.save_file = os.path.join(self.user_data_dir, "save_data.json")

        # Load saved data if available
        self._load_data()

    def reset_game_session(self):
        """Reset temporary game state for a new game"""
        self.score = 0
        self.current_wave = 1
        self.wave_timer = 0
        self.game_active = True

    def _load_data(self):
        """Load persistent game data from file"""
        try:
            if os.path.exists(self.save_file):
                with open(self.save_file, 'r') as f:
                    data = json.load(f)
                    self.coins = data.get("coins", 0)
                    self.player_stats = data.get("player_stats", self.player_stats)
        except Exception as e:
            print(f"Error loading game data: {e}")

    def save_data(self):
        """Save persistent game data to file"""
        try:
            data = {
                "coins": self.coins,
                "player_stats": self.player_stats
            }
            with open(self.save_file, 'w') as f:
                json.dump(data, f)
        except Exception as e:
            print(f"Error saving game data: {e}")

    def add_score(self, points):
        """Add points to the current score"""
        self.score += points

    def add_coins(self, amount):
        """Add coins to the player's total"""
        self.coins += amount
        self.save_data()

    def spend_coins(self, amount):
        """Spend coins if available"""
        if self.coins >= amount:
            self.coins -= amount
            self.save_data()
            return True
        return False

# Create singleton instance
game_state = GameState()

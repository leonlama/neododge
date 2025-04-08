"""
Game-wide constants and configuration values.
Centralizes all configurable parameters for easy tuning.
"""

# Screen settings
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "NeoDodge"

# Asset paths
DEFAULT_SKIN_PATH = "assets/skins/default/"
MDMA_SKIN_PATH = "assets/skins/mdma/"
SKINS_DIR = "assets/skins/"  # Add this missing constant

# Object scaling
ARTIFACT_SCALE = 0.035

# Gameplay settings (new, won't break existing code)
BASE_WAVE_DURATION = 20.0
WAVE_DIFFICULTY_MULTIPLIER = 1.2
ORB_SPAWN_INTERVAL = (4, 8)
ARTIFACT_SPAWN_INTERVAL = (20, 30)

# Player settings (new, won't break existing code)
PLAYER_BASE_SPEED = 2
PLAYER_BASE_HEALTH = 3

# Enemy settings (new, won't break existing code)
ENEMY_BASE_SPEED = 3.0
ENEMY_SPAWN_RATE_BASE = 1.0

# Bullet settings (new, won't break existing code)
BULLET_SPEED = 250
BULLET_LIFETIME = 5.0  # seconds

# Artifact settings (new, won't break existing code)
ARTIFACT_COOLDOWNS = {
    "Dash": 5,
    "MagnetPulse": 30,
    "SlowField": 30,
    "BulletTime": 30,
    "CloneDash": 30
}
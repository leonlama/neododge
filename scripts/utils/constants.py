from pathlib import Path

# Base directories
BASE_DIR = Path(__file__).parent.parent.parent  # Go up to project root
ASSETS_DIR = BASE_DIR / "assets"
SKINS_DIR = ASSETS_DIR / "skins"

# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "NeoDodge"

# Skin paths
DEFAULT_SKIN_PATH = str(SKINS_DIR / "default")
MDMA_SKIN_PATH = str(SKINS_DIR / "mdma")

# Default skin
DEFAULT_SKIN = "default"

# Game constants
ARTIFACT_SCALE = 0.035
PLAYER_SPEED = 5.0
ENEMY_SPEED = 3.0
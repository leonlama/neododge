from pathlib import Path

BASE_DIR = Path(__file__).parent.parent.parent  # Go up two levels to reach project root
SKINS_DIR = BASE_DIR / "assets" / "skins"

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "NeoDodge"

# Update these paths to be absolute
DEFAULT_SKIN_PATH = str(SKINS_DIR / "default")
MDMA_SKIN_PATH = str(SKINS_DIR / "mdma")

ARTIFACT_SCALE = 0.035

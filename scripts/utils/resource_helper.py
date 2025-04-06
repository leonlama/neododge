import sys
from pathlib import Path

def resource_path(relative_path):
    """
    Get the absolute path to a resource, whether we're running from source or from a PyInstaller bundle.
    """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = Path(sys._MEIPASS)
    except AttributeError:
        base_path = Path().absolute()

    return base_path / relative_path
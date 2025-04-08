"""Resource loading and management utilities."""

import os
import sys
import arcade

def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller."""
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

def load_sound(path):
    """Load a sound file with proper path resolution."""
    return arcade.load_sound(resource_path(path))

def load_texture(path):
    """Load a texture with proper path resolution."""
    return arcade.load_texture(resource_path(path))

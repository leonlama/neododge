import os
import arcade

def resource_path(relative_path):
    """Get the absolute path to a resource file"""
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
        return os.path.join(base_path, '..', '..', relative_path)
    except Exception:
        return os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', relative_path)

def load_texture(path, fallback=None):
    """Load a texture with fallback option"""
    try:
        return arcade.load_texture(resource_path(path))
    except Exception as e:
        print(f"Error loading texture: {path} - {e}")
        if fallback:
            try:
                return arcade.load_texture(resource_path(fallback))
            except:
                pass
        # Return a placeholder texture
        return arcade.make_soft_square_texture(32, arcade.color.PURPLE, outer_alpha=255)

def load_sound(path, fallback=None):
    """Load a sound with fallback option"""
    try:
        return arcade.load_sound(resource_path(path))
    except Exception as e:
        print(f"Error loading sound: {path} - {e}")
        if fallback:
            try:
                return arcade.load_sound(resource_path(fallback))
            except:
                pass
        # Return None for sound
        return None
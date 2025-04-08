import os
import json
import arcade

class SoundManager:
    """Manages game sounds and their volume levels."""

    def __init__(self):
        """Initialize the sound manager."""
        self.sounds = {}
        self.music = {}
        self.volume_levels = {
            "master": 1.0,
            "sfx": 0.8,
            "music": 0.5,
            "ui": 0.7
        }
        self.sound_categories = {
            "player": 0.8,
            "enemy": 0.6,
            "orb": 0.7,
            "artifact": 0.9,
            "coin": 0.5,
            "ui": 0.7
        }

        # Load configuration
        self.load_config()

    def load_config(self):
        """Load sound configuration from config.json."""
        config_path = "assets/audio/config.json"
        if os.path.exists(config_path):
            try:
                with open(config_path, "r") as f:
                    config = json.load(f)

                    # Update volume levels if defined
                    if "volume_levels" in config:
                        self.volume_levels.update(config["volume_levels"])

                    # Update sound categories if defined
                    if "sound_categories" in config:
                        self.sound_categories.update(config["sound_categories"])

                    print("🔊 Loaded sound configuration")
            except Exception as e:
                print(f"⚠️ Error loading sound config: {e}")

    def get_sound(self, category, name):
        """Get a sound by category and name.

        Args:
            category: Category of the sound (player, enemy, etc.)
            name: Name of the sound

        Returns:
            arcade.Sound: The requested sound
        """
        sound_key = f"{category}/{name}"

        # Return cached sound if available
        if sound_key in self.sounds:
            return self.sounds[sound_key]

        # Try to load the sound
        try:
            sound_path = f"assets/audio/{category}/{name}.wav"
            if os.path.exists(sound_path):
                sound = arcade.load_sound(sound_path)
                self.sounds[sound_key] = sound
                return sound
        except Exception as e:
            print(f"⚠️ Error loading sound '{name}': {e}")

        return None

    def play_sound(self, category, name):
        """Play a sound with the appropriate volume.

        Args:
            category: Category of the sound (player, enemy, etc.)
            name: Name of the sound

        Returns:
            int: The sound player ID or None if sound couldn't be played
        """
        sound = self.get_sound(category, name)
        if sound:
            # Calculate volume based on master, category, and sfx levels
            volume = (
                self.volume_levels["master"] * 
                self.volume_levels["sfx"] * 
                self.sound_categories.get(category, 0.8)
            )
            return arcade.play_sound(sound, volume)
        return None

    def play_music(self, name, loop=True):
        """Play background music.

        Args:
            name: Name of the music file (without extension)
            loop: Whether to loop the music

        Returns:
            int: The music player ID or None if music couldn't be played
        """
        # Stop any currently playing music
        arcade.stop_sound(self.current_music_player)

        # Try to load and play the music
        try:
            music_path = f"assets/audio/music/{name}.mp3"
            if os.path.exists(music_path):
                volume = self.volume_levels["master"] * self.volume_levels["music"]
                self.current_music_player = arcade.play_sound(
                    arcade.load_sound(music_path), 
                    volume, 
                    looping=loop
                )
                return self.current_music_player
        except Exception as e:
            print(f"⚠️ Error playing music '{name}': {e}")

        return None

    def update_volume(self, volume_type, value):
        """Update a volume setting.

        Args:
            volume_type: Type of volume to update (master, sfx, music, ui)
            value: New volume value (0.0 to 1.0)
        """
        if volume_type in self.volume_levels:
            self.volume_levels[volume_type] = max(0.0, min(1.0, value))
            print(f"🔊 {volume_type.capitalize()} volume set to {value}")

            # Update music volume if it's playing
            if hasattr(self, 'current_music_player') and self.current_music_player:
                new_volume = self.volume_levels["master"] * self.volume_levels["music"]
                arcade.set_volume(self.current_music_player, new_volume)

# Create a global instance
sound_manager = SoundManager()
import os
import json
import arcade

class SoundManager:
    """Manages game sounds and their volume levels."""

    def __init__(self):
        """Initialize the sound manager."""
        self.sounds = {}
        self.music = {}
        self.current_music_player = None

        # Default volume settings
        self.volume_levels = {
            "master": 1.0,
            "sfx": 0.8,
            "music": 0.5,
            "ui": 0.7
        }

        # Default category volumes
        self.category_volumes = {
            "player": 0.6,
            "enemy": 0.5,
            "orb": 0.7,
            "coin": 0.6,
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
                    print(f"🔊 Loading sound config from: {config_path}")

                    # Update volume levels if defined
                    if "volume_levels" in config:
                        self.volume_levels.update(config["volume_levels"])
                        print(f"🔊 Updated volume levels: {self.volume_levels}")

                    # Handle either category_volumes or sound_categories
                    if "category_volumes" in config:
                        self.category_volumes.update(config["category_volumes"])
                        print(f"🔊 Updated category volumes from 'category_volumes'")
                    elif "sound_categories" in config:
                        # Map sound_categories to category_volumes
                        self.category_volumes = config["sound_categories"]
                        print(f"🔊 Updated category volumes from 'sound_categories'")

                    print("🔊 Loaded sound configuration successfully")
            except Exception as e:
                print(f"⚠️ Error loading sound config: {e}")
                self.create_default_config()
        else:
            # Create default config if it doesn't exist
            self.create_default_config()

    def create_default_config(self):
        """Create a default sound configuration file."""
        config = {
            "volume_levels": {
                "master": 1.0,
                "sfx": 0.7,
                "music": 0.5,
                "ui": 0.7
            },
            "sound_categories": {  # Changed from category_volumes to sound_categories
                "player": {
                    "damage": 0.1,  # Drastically reduced damage sound
                    "dash": 0.5,
                    "death": 0.6
                },
                "enemy": {
                    "hit": 0.5,
                    "death": 0.6,
                    "shoot": 0.4,
                    "bounce": 0.0  # Explicitly silence bounce sound
                },
                "orb": {
                    "buff": 0.5,
                    "debuff": 0.05,  # Significantly reduced debuff sound
                    "collect": 0.5
                },
                "coin": {
                    "collect": 0.8  # Increased coin sound
                },
                "ui": {
                    "click": 0.5,
                    "hover": 0.3,
                    "wave": 0.7
                }
            }
        }

        try:
            os.makedirs(os.path.dirname("assets/audio/config.json"), exist_ok=True)
            with open("assets/audio/config.json", "w") as f:
                json.dump(config, f, indent=4)
            print("🔊 Created default sound configuration")
        except Exception as e:
            print(f"⚠️ Error creating sound config: {e}")

    def save_config(self):
        """Save the current sound configuration to file."""
        config = {
            "volume_levels": self.volume_levels,
            "sound_categories": self.category_volumes  # Use sound_categories for consistency
        }

        try:
            os.makedirs(os.path.dirname("assets/audio/config.json"), exist_ok=True)
            with open("assets/audio/config.json", "w") as f:
                json.dump(config, f, indent=4)
            print("🔊 Saved sound configuration")
            return True
        except Exception as e:
            print(f"⚠️ Error saving sound config: {e}")
            return False

    def get_sound(self, category, name):
        """Get a sound by category and name.

        Args:
            category: Category of the sound (player, enemy, etc.)
            name: Name of the sound

        Returns:
            arcade.Sound: The requested sound
        """
        # Check if we should skip this sound (for bounce sound)
        if category == "enemy" and name == "bounce":
            return None  # Silently skip bounce sounds
            
        sound_key = f"{category}/{name}"

        # Return cached sound if available
        if sound_key in self.sounds:
            return self.sounds[sound_key]

        # Try to load the sound
        try:
            # Map sound names to actual files with correct extensions
            if category == "coin" and name == "collect":
                sound_path = f"assets/audio/coin/coin.flac"
            elif category == "enemy" and name == "shoot":
                sound_path = f"assets/audio/enemy/shoot.mp3"
            elif category == "ui" and name == "wave":
                sound_path = f"assets/audio/ui/wave.mp3"
            else:
                # Try wav first, then mp3
                sound_path = f"assets/audio/{category}/{name}.wav"
                if not os.path.exists(sound_path):
                    sound_path = f"assets/audio/{category}/{name}.mp3"

            if os.path.exists(sound_path):
                sound = arcade.load_sound(sound_path)
                self.sounds[sound_key] = sound
                return sound
            else:
                # Only log for sounds we actually want
                if not (category == "enemy" and name == "bounce"):
                    print(f"⚠️ Sound file not found: {sound_path}")
        except Exception as e:
            if not (category == "enemy" and name == "bounce"):
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
        # Check if we should skip this sound (for bounce sound)
        if category == "enemy" and name == "bounce":
            return None  # Silently skip bounce sounds
            
        sound = self.get_sound(category, name)
        if sound:
            # Calculate volume based on master, sfx, and category levels
            category_volume = 0.5  # Default volume if nothing else is specified

            # Get category volume, handling both flat and nested structures
            if category in self.category_volumes:
                cat_vol = self.category_volumes[category]
                if isinstance(cat_vol, dict):
                    # Nested structure (e.g., {"player": {"damage": 0.1}})
                    if name in cat_vol:
                        category_volume = cat_vol[name]
                    else:
                        # Use a default for this category if sound name not found
                        category_volume = 0.5
                        print(f"⚠️ No volume setting for {category}/{name}, using default: {category_volume}")
                else:
                    # Flat structure (e.g., {"player": 0.6})
                    category_volume = cat_vol

            # Calculate final volume
            volume = self.volume_levels["master"] * self.volume_levels["sfx"] * category_volume

            # Extra reduction for damage sound as a failsafe
            if category == "player" and name == "damage":
                volume *= 0.1  # Additional 90% reduction

            # Ensure volume is in valid range
            volume = max(0.0, min(1.0, volume))

            print(f"🔊 Playing sound {category}/{name} at volume {volume:.2f}")
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
        if hasattr(self, 'current_music_player') and self.current_music_player:
            arcade.stop_sound(self.current_music_player)

        # Try to load and play the music
        try:
            if name == "shop":
                music_path = f"assets/audio/ui/shop.mp3"
            elif name == "theme":
                music_path = f"assets/audio/ui/themev1.mp3"
            else:
                music_path = f"assets/audio/music/{name}.mp3"

            if os.path.exists(music_path):
                volume = self.volume_levels["master"] * self.volume_levels["music"]
                self.current_music_player = arcade.play_sound(
                    arcade.load_sound(music_path), 
                    volume, 
                    looping=loop
                )
                return self.current_music_player
            else:
                print(f"⚠️ Music file not found: {music_path}")
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
    
    def update_category_volume(self, category, value):
        """Update a category's volume.

        Args:
            category: Category to update (player, enemy, etc.)
            value: New volume value (0.0 to 1.0)
        """
        if isinstance(self.category_volumes.get(category), dict):
            # If it's a nested structure, we need to update all sub-volumes
            for sound_name in self.category_volumes[category]:
                self.update_sound_volume(category, sound_name, value)
        else:
            # Simple flat structure
            self.category_volumes[category] = max(0.0, min(1.0, value))
            print(f"🔊 {category.capitalize()} volume set to {value}")

        # Save the updated config
        self.save_config()

    def update_sound_volume(self, category, sound_name, value):
        """Update a specific sound's volume.

        Args:
            category: Sound category (player, enemy, etc.)
            sound_name: Name of the sound (damage, shoot, etc.)
            value: New volume value (0.0 to 1.0)
        """
        # Ensure category exists and is a dict
        if category not in self.category_volumes:
            self.category_volumes[category] = {}

        if not isinstance(self.category_volumes[category], dict):
            # Convert from flat to nested structure
            old_value = self.category_volumes[category]
            self.category_volumes[category] = {sound_name: old_value}

        # Update the specific sound volume
        self.category_volumes[category][sound_name] = max(0.0, min(1.0, value))
        print(f"🔊 {category.capitalize()}/{sound_name} volume set to {value}")

        # Save the updated config
        self.save_config()

    def reload_config(self):
        """Reload the sound configuration from file."""
        # Store current music player
        current_music = self.current_music_player

        # Reset to defaults
        self.volume_levels = {
            "master": 1.0,
            "sfx": 0.8,
            "music": 0.5,
            "ui": 0.7
        }

        self.category_volumes = {
            "player": 0.6,
            "enemy": 0.5,
            "orb": 0.7,
            "coin": 0.6,
            "ui": 0.7
        }

        # Load from file
        self.load_config()

        # Update music volume if it was playing
        if current_music:
            new_volume = self.volume_levels["master"] * self.volume_levels["music"]
            arcade.set_volume(current_music, new_volume)
            self.current_music_player = current_music

        print("🔊 Reloaded sound configuration")
    
    def test_sounds(self):
        """Play all sounds for testing volume levels."""
        print("🔊 Testing sounds...")

        # Play each sound with a delay

        def play_next(sound_index=0):
            sounds = [
                ("player", "damage", "Player Damage"),
                ("orb", "buff", "Orb Buff"),
                ("orb", "debuff", "Orb Debuff"),
                ("coin", "collect", "Coin Collect"),
                ("enemy", "hit", "Enemy Hit"),
                ("enemy", "death", "Enemy Death"),
                ("enemy", "shoot", "Enemy Shoot"),
                ("ui", "wave", "Wave Start")
            ]

            if sound_index < len(sounds):
                category, name, label = sounds[sound_index]
                print(f"Playing: {label}")
                self.play_sound(category, name)
                # Schedule next sound
                arcade.schedule(lambda dt: play_next(sound_index + 1), 1.5)

        # Start the test
        play_next()

# Create a global instance
sound_manager = SoundManager()
import random
import arcade
from src.core.constants import SCREEN_WIDTH, SCREEN_HEIGHT, WAVE_DURATION

class WaveManager:
    """Manages game waves, difficulty progression, and wave transitions"""

    def __init__(self, game_view):
        self.game_view = game_view
        self.wave = 1
        self.level_timer = 0
        self.wave_duration = WAVE_DURATION
        self.wave_message = ""
        self.wave_message_animation = None
        self.wave_transition_active = False
        self.wave_transition_timer = 0
        self.special_event = None
        self.special_event_timer = 0

        # Start with initial wave message
        self._show_wave_message(f"Wave {self.wave}")

    def update(self, delta_time):
        """Update wave state and handle transitions"""
        # Update wave message animation
        if self.wave_message_animation:
            self._update_message_animation(delta_time)

        # Update special event timer
        if self.special_event:
            self.special_event_timer -= delta_time
            if self.special_event_timer <= 0:
                self.special_event = None

        # If in wave transition, don't update the level timer
        if self.wave_transition_active:
            self.wave_transition_timer -= delta_time
            if self.wave_transition_timer <= 0:
                self.wave_transition_active = False
            return

        # Update level timer
        self.level_timer += delta_time

        # Check if wave is complete
        if self.level_timer >= self.wave_duration:
            self._complete_wave()

    def _complete_wave(self):
        """Handle wave completion and transition to next wave"""
        # Reset level timer
        self.level_timer = 0

        # Show wave completion message
        self._show_wave_message(f"Wave {self.wave} Completed!")

        # Start wave transition
        self.wave_transition_active = True
        self.wave_transition_timer = 3.0  # 3 seconds transition

        # Increment wave
        self.wave += 1

        # Check for special events
        self._check_special_events()

        # Clear enemies
        self.game_view.enemies.clear()

    def _check_special_events(self):
        """Check and apply special events for the current wave"""
        # Every 5th wave is a milestone
        if self.wave % 5 == 0:
            # Give player a reward
            self.game_view.player.coins += 5

            # Show milestone message after a delay
            arcade.schedule(
                lambda dt: self._show_wave_message(f"Milestone Wave {self.wave}!"),
                3.0  # Show after 3 seconds
            )

        # Special events based on wave number
        if self.wave == 10:
            self.special_event = "Orb Storm"
            self.special_event_timer = 10.0
            arcade.schedule(
                lambda dt: self._show_wave_message("ORB STORM!"),
                4.0  # Show after 4 seconds
            )
        elif self.wave == 15:
            self.special_event = "No Buffs"
            self.special_event_timer = 15.0
            arcade.schedule(
                lambda dt: self._show_wave_message("DEBUFF ZONE!"),
                4.0  # Show after 4 seconds
            )
        elif self.wave == 25:
            self.special_event = "Bullet Speed Up"
            self.special_event_timer = 20.0
            arcade.schedule(
                lambda dt: self._show_wave_message("BULLET FRENZY!"),
                4.0  # Show after 4 seconds
            )
        elif self.wave == 35:
            self.special_event = "Double Enemies"
            self.special_event_timer = 25.0
            arcade.schedule(
                lambda dt: self._show_wave_message("DOUBLE TROUBLE!"),
                4.0  # Show after 4 seconds
            )

    def _show_wave_message(self, message):
        """Show an animated wave message"""
        self.wave_message = message

        # Calculate letter positions for the animation
        text_width = len(message) * 15  # Approximate width per letter
        center_x = SCREEN_WIDTH / 2
        start_x = center_x - text_width / 2

        letter_positions = []
        for i in range(len(message)):
            letter_x = start_x + i * 15 + 7.5  # Center of each letter
            letter_positions.append(letter_x)

        # Initialize animation state
        self.wave_message_animation = {
            "phase": "fade_in",
            "timer": 0,
            "duration": {
                "fade_in": 1.0,    # 1 second fade in
                "hold": 1.5,       # 1.5 seconds hold
                "letter_fade": 1.5  # 1.5 seconds letter fade
            },
            "alpha": 0,
            "letter_positions": letter_positions,
            "letter_alphas": [255] * len(message)
        }

    def _update_message_animation(self, delta_time):
        """Update the wave message animation state"""
        if not self.wave_message_animation:
            return

        animation = self.wave_message_animation
        animation["timer"] += delta_time

        if animation["phase"] == "fade_in":
            # Fade in the entire message
            progress = min(1.0, animation["timer"] / animation["duration"]["fade_in"])
            animation["alpha"] = int(255 * progress)

            if progress >= 1.0:
                animation["phase"] = "hold"
                animation["timer"] = 0

        elif animation["phase"] == "hold":
            # Hold the message at full opacity
            if animation["timer"] >= animation["duration"]["hold"]:
                animation["phase"] = "letter_fade"
                animation["timer"] = 0

        elif animation["phase"] == "letter_fade":
            # Fade out letters one by one
            letter_duration = animation["duration"]["letter_fade"] / len(self.wave_message)
            current_letter = int(animation["timer"] / letter_duration)

            # Fade out letters that have been reached
            for i in range(min(current_letter + 1, len(self.wave_message))):
                letter_progress = min(1.0, (animation["timer"] - i * letter_duration) / letter_duration)
                animation["letter_alphas"][i] = int(255 * (1.0 - letter_progress))

            # Check if animation is complete
            if current_letter >= len(self.wave_message):
                self.wave_message = ""
                self.wave_message_animation = None

    def get_enemy_count(self):
        """Get the number of enemies to spawn based on current wave"""
        base_count = 3

        if self.wave <= 5:
            return random.randint(3, 6)
        elif self.wave <= 10:
            return random.randint(6, 9)
        elif self.wave <= 20:
            return random.randint(8, 12)
        elif self.wave <= 30:
            return random.randint(10, 15)
        else:
            return random.randint(15, 20)

    def get_enemy_speed(self):
        """Get the enemy speed multiplier based on current wave"""
        if self.wave <= 5:
            return 0.7  # 70% of base speed
        elif self.wave <= 10:
            return 0.85  # 85% of base speed
        elif self.wave <= 20:
            return 1.0  # Base speed
        elif self.wave <= 30:
            return 1.2  # 120% of base speed
        else:
            return 1.3  # 130% of base speed

    def get_spawn_interval(self):
        """Get the enemy spawn interval based on current wave"""
        if self.wave <= 5:
            return random.uniform(3.0, 4.0)
        elif self.wave <= 10:
            return random.uniform(2.5, 3.5)
        elif self.wave <= 20:
            return random.uniform(2.0, 3.0)
        elif self.wave <= 30:
            return random.uniform(1.5, 2.5)
        else:
            return random.uniform(1.0, 2.0)

    def get_orb_interval(self):
        """Get the orb spawn interval based on current wave"""
        if self.wave <= 5:
            return random.uniform(6.0, 8.0)
        elif self.wave <= 15:
            return random.uniform(5.0, 7.0)
        elif self.wave <= 30:
            return random.uniform(4.0, 6.0)
        else:
            return random.uniform(3.0, 5.0)

    def get_orb_ratio(self):
        """Get the buff to debuff orb ratio based on current wave"""
        if self.wave <= 5:
            return 0.7, 0.3  # 70% buff, 30% debuff
        elif self.wave <= 15:
            return 0.6, 0.4  # 60% buff, 40% debuff
        elif self.wave <= 30:
            return 0.5, 0.5  # 50% buff, 50% debuff
        else:
            return 0.4, 0.6  # 40% buff, 60% debuff

    def get_available_artifacts(self):
        """Get the list of available artifacts based on current wave"""
        if self.wave <= 10:
            return ["Dash", "Magnet Pulse"]
        elif self.wave <= 20:
            return ["Dash", "Magnet Pulse", "Slow Field"]
        elif self.wave <= 30:
            return ["Dash", "Magnet Pulse", "Slow Field", "Bullet Time"]
        else:
            return ["Dash", "Magnet Pulse", "Slow Field", "Bullet Time", "Clone Dash"]
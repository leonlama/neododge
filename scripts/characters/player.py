"""
Player character implementation with movement, health, and artifact management.
"""
import arcade
import math
import random
from scripts.utils.constants import PLAYER_BASE_SPEED, PLAYER_BASE_HEALTH
from scripts.skins.skin_manager import skin_manager
from scripts.utils.resource_helper import resource_path
from scripts.mechanics.game_state import game_state
from scripts.mechanics.event_manager import event_manager

# Load sound effects
damage_sound = arcade.load_sound(resource_path("assets/audio/damage.wav"))

class Player(arcade.Sprite):
    """
    Player character with movement, health management, and artifact usage.
    Responds to user input and manages player state.
    """

    def __init__(self, x, y):
        """
        Initialize the player character

        Args:
            x: Initial x position
            y: Initial y position
        """
        super().__init__()

        # Core properties
        self.center_x = x
        self.center_y = y

        # Load textures based on selected skin
        self._load_textures()

        # Stats
        self.health = game_state.player_stats["max_health"]
        self.base_speed = PLAYER_BASE_SPEED
        self.speed = self.base_speed * game_state.player_stats["speed"]

        # Movement
        self.change_x = 0
        self.change_y = 0
        self.last_move_direction = (0, 1)  # Default facing up

        # Artifact management
        self.artifacts = {}
        self.active_artifacts = []

        # Invincibility after taking damage
        self.invincible = False
        self.invincible_timer = 0

        # Vision effects
        self.vision_blur = False  # Add this missing attribute

        # Additional attributes from original Player class
        self.current_hearts = 3  # Default heart count
        self.max_slots = 3       # Maximum heart slots
        self.gold_hearts = 0     # Gold hearts count
        self.shield = False      # Shield status
        self.dash_timer = 0      # Dash cooldown timer
        self.blink_state = True  # For blinking when invincible
        self.window = None       # Reference to game window
        self.parent_view = None  # Reference to parent view
        self.target_x = None     # Target X for dash
        self.target_y = None     # Target Y for dash

        # Orb status attributes
        self.orb_effects = {
            "speed": 1.0,
            "cooldown": 1.0,
            "multiplier": 1.0,
            "vision": False,
            "hitbox": 1.0
        }
        self.orb_timers = {
            "speed": 0,
            "cooldown": 0,
            "multiplier": 0,
            "vision": 0,
            "hitbox": 0
        }

        # Register for events
        event_manager.subscribe("artifact_collected", self._on_artifact_collected)
        event_manager.subscribe("coin_collected", self._on_coin_collected)

    def _load_textures(self):
        """Load player textures based on selected skin"""
        # Load player texture
        player_texture = skin_manager.get_texture("player", "default")
        if player_texture:
            self.texture = player_texture
            self.scale = skin_manager.get_player_scale()
        else:
            # Fallback texture if skin doesn't have player texture
            self.texture = arcade.make_soft_square_texture(
                30, arcade.color.WHITE, outer_alpha=255
            )

        # Load orb textures using skin manager
        self.orb_textures = {}
        orb_types = ["speed", "cooldown", "multiplier", "vision", "hitbox"]
        for orb_type in orb_types:
            texture = skin_manager.get_texture("orbs", orb_type)
            if texture:
                self.orb_textures[orb_type] = texture
            else:
                # Fallback textures
                color = arcade.color.BLUE if orb_type == "speed" else \
                       arcade.color.PURPLE if orb_type == "cooldown" else \
                       arcade.color.GOLD if orb_type == "multiplier" else \
                       arcade.color.GRAY if orb_type == "vision" else \
                       arcade.color.RED
                self.orb_textures[orb_type] = arcade.make_soft_circle_texture(18, color)

        # Load heart textures using skin manager
        self.heart_textures = {}
        heart_types = ["red", "gray", "gold"]
        for heart_type in heart_types:
            texture = skin_manager.get_texture("hearts", heart_type)
            if texture:
                self.heart_textures[heart_type] = texture
            else:
                # Fallback to direct loading
                try:
                    self.heart_textures[heart_type] = arcade.load_texture(
                        resource_path(f"assets/ui/heart_{heart_type}.png")
                    )
                except:
                    # Ultimate fallback
                    color = arcade.color.RED if heart_type == "red" else \
                           arcade.color.GRAY if heart_type == "gray" else \
                           arcade.color.GOLD
                    self.heart_textures[heart_type] = arcade.make_soft_circle_texture(18, color)

    def update(self, delta_time):
        """
        Update player state

        Args:
            delta_time: Time since last update in seconds
        """
        # Update position
        self.center_x += self.change_x * self.speed * delta_time
        self.center_y += self.change_y * self.speed * delta_time

        # Update invincibility
        if self.invincible:
            self.invincible_timer += delta_time
            # Blink effect
            if int(self.invincible_timer * 10) % 2 == 0:
                self.blink_state = True
            else:
                self.blink_state = False

            # End invincibility after 1.5 seconds
            if self.invincible_timer >= 1.5:
                self.invincible = False
                self.blink_state = True

        # Update dash timer
        if self.dash_timer < 5:  # 5 second cooldown
            self.dash_timer += delta_time

        # Update artifact cooldowns
        for artifact_name, cooldown in list(self.artifacts.items()):
            if cooldown > 0:
                self.artifacts[artifact_name] -= delta_time
                if self.artifacts[artifact_name] <= 0:
                    self.artifacts[artifact_name] = 0

        # Update orb timers
        for orb_type, timer in list(self.orb_timers.items()):
            if timer > 0:
                self.orb_timers[orb_type] -= delta_time
                if self.orb_timers[orb_type] <= 0:
                    self.orb_timers[orb_type] = 0
                    # Reset effect when timer expires
                    if orb_type == "speed":
                        self.orb_effects["speed"] = 1.0
                        self.speed = self.base_speed * game_state.player_stats["speed"]
                    elif orb_type == "cooldown":
                        self.orb_effects["cooldown"] = 1.0
                    elif orb_type == "multiplier":
                        self.orb_effects["multiplier"] = 1.0
                    elif orb_type == "vision":
                        self.orb_effects["vision"] = False
                        self.vision_blur = False
                    elif orb_type == "hitbox":
                        self.orb_effects["hitbox"] = 1.0
                        self.scale = 1.0

        # Store last move direction if moving
        if self.change_x != 0 or self.change_y != 0:
            magnitude = math.sqrt(self.change_x**2 + self.change_y**2)
            if magnitude > 0:
                self.last_move_direction = (
                    self.change_x / magnitude,
                    self.change_y / magnitude
                )

    def perform_dash(self):
        """Perform a dash move in the direction of the target"""
        # Fallback if target is None
        if self.target_x is None or self.target_y is None:
            self.target_x = self.center_x + 1  # minimal dash
            self.target_y = self.center_y

        dx = self.target_x - self.center_x
        dy = self.target_y - self.center_y
        distance = math.hypot(dx, dy)

        if distance == 0:
            return

        dash_distance = 100  # Dash distance in pixels
        self.center_x += (dx / distance) * dash_distance
        self.center_y += (dy / distance) * dash_distance
        self.invincible = True
        self.invincibility_timer = 0
        self.dash_timer = 0

    def take_damage(self, amount: float = 0.5):
        """
        Handle player taking damage

        Args:
            amount: Amount of damage to take
        """
        # Skip if already invincible
        if self.invincible:
            return False

        # Check for shield
        if self.shield:
            self.shield = False
            return False

        # Play damage sound
        arcade.play_sound(damage_sound)

        # Set invincibility
        self.invincible = True
        self.invincibility_timer = 0

        # Apply damage to hearts
        while amount > 0:
            if self.gold_hearts > 0:
                self.gold_hearts -= 1
                amount -= 1
            elif self.current_hearts > 0:
                self.current_hearts -= 0.5
                amount -= 0.5
            else:
                break

        # Check for game over
        if self.current_hearts + self.gold_hearts <= 0:
            if self.window and hasattr(self, 'parent_view') and self.parent_view:
                from scripts.views.game_over_view import GameOverView
                self.window.show_view(GameOverView(self.parent_view.score))

        return True

    def draw(self):
        """Draw the player sprite with invincibility effect"""
        if not self.invincible or self.blink_state:
            super().draw()

    def draw_hearts(self, x_start=30, y=570):
        """
        Draw the player's health hearts

        Args:
            x_start: Starting X position for hearts
            y: Y position for hearts
        """
        for i in range(self.max_slots):
            x = x_start + i * 40
            if i < int(self.current_hearts):
                arcade.draw_texture_rectangle(x, y, 32, 32, self.heart_textures["red"])
            elif i < self.current_hearts:
                arcade.draw_texture_rectangle(x, y, 32, 32, self.heart_textures["red"], alpha=128)
            else:
                arcade.draw_texture_rectangle(x, y, 32, 32, self.heart_textures["gray"])
        for i in range(self.gold_hearts):
            x = x_start + (self.max_slots + i) * 40
            arcade.draw_texture_rectangle(x, y, 32, 32, self.heart_textures["gold"])

    def draw_orb_status(self, x_start=700, y_start=570):
        """
        Draw the player's active orb effects

        Args:
            x_start: Starting X position for orb status
            y_start: Starting Y position for orb status
        """
        x = x_start
        y = y_start

        # Draw active orb effects
        for orb_type, timer in self.orb_timers.items():
            if timer > 0:
                # Draw orb icon
                if orb_type in self.orb_textures:
                    arcade.draw_texture_rectangle(x, y, 24, 24, self.orb_textures[orb_type])

                # Draw timer text
                arcade.draw_text(
                    f"{timer:.1f}s",
                    x + 15,
                    y - 8,
                    arcade.color.WHITE,
                    font_size=10,
                    anchor_x="center"
                )

                # Move to next position
                y -= 30

    def apply_orb_effect(self, orb_type, duration, value=None):
        """
        Apply an orb effect to the player

        Args:
            orb_type: Type of orb effect
            duration: Duration of the effect in seconds
            value: Optional value for the effect
        """
        # Set the timer
        self.orb_timers[orb_type] = duration

        # Apply the effect
        if orb_type == "speed":
            # Speed orb (positive or negative)
            if value is not None:
                self.orb_effects["speed"] = value
                self.speed = self.base_speed * game_state.player_stats["speed"] * value
        elif orb_type == "cooldown":
            # Cooldown reduction orb
            if value is not None:
                self.orb_effects["cooldown"] = value
        elif orb_type == "multiplier":
            # Score multiplier orb
            if value is not None:
                self.orb_effects["multiplier"] = value
        elif orb_type == "vision":
            # Vision blur orb
            self.orb_effects["vision"] = True
            self.vision_blur = True
        elif orb_type == "hitbox":
            # Hitbox size orb
            if value is not None:
                self.orb_effects["hitbox"] = value
                self.scale = value

    def use_artifact(self, artifact_name):
        """
        Use an artifact if available

        Args:
            artifact_name: Name of the artifact to use

        Returns:
            bool: True if artifact was used, False otherwise
        """
        if artifact_name in self.artifacts and self.artifacts[artifact_name] <= 0:
            # Artifact is available, use it
            event_manager.publish("artifact_used", artifact_name)
            return True
        return False

    def add_artifact(self, artifact_name, cooldown):
        """
        Add or reset cooldown for an artifact

        Args:
            artifact_name: Name of the artifact
            cooldown: Cooldown time in seconds
        """
        self.artifacts[artifact_name] = cooldown
        event_manager.publish("artifact_added", artifact_name)

    def _on_artifact_collected(self, artifact_data):
        """Handle artifact collection event"""
        if isinstance(artifact_data, dict) and "name" in artifact_data and "cooldown" in artifact_data:
            self.add_artifact(artifact_data["name"], artifact_data["cooldown"])

    def _on_coin_collected(self, amount):
        """Handle coin collection event"""
        game_state.add_coins(amount)
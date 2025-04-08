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

from scripts.utils.constants import PLAYER_BASE_SPEED

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

        # Health-related attributes
        self.max_slots = 3        # Maximum number of heart slots
        self.current_hearts = 3   # Current number of hearts
        self.gold_hearts = 0      # Number of gold hearts (extra lives)

        # Movement-related attributes
        self.change_x = 0
        self.change_y = 0
        self.speed_bonus = 1.0    # Speed multiplier from orbs
        self.inverse_move = False # Whether movement is inverted
        self.last_move_direction = (0, 1)  # Default facing up

        # Dash-related attributes
        self.cooldown = 15.0      # Base cooldown in seconds
        self.cooldown_factor = 1.0  # Cooldown multiplier (lower is better)
        self.dash_timer = self.cooldown  # Start with dash available

        # Effect-related attributes
        self.shield = False       # Shield status
        self.invincible = False   # Invincibility status
        self.invincibility_timer = 0  # Time since becoming invincible
        self.blink_timer = 0      # Timer for blinking effect
        self.blink_state = True   # Current blink state
        self.multiplier = 1.0     # Score multiplier
        self.vision_blur = False  # Vision blur effect
        self.vision_timer = 0     # Vision effect timer

        # Hitbox-related attributes
        self.original_size = (self.width, self.height)  # Store original size
        self.hitbox_factor = 1.0  # Hitbox size multiplier
        self.big_hitbox_timer = 0  # Hitbox effect timer

        # Target-related attributes
        self.target_x = None      # Target X position
        self.target_y = None      # Target Y position

        # Artifact-related attributes
        self.artifacts = {}       # Dictionary for cooldowns
        self.artifact_objects = []  # List for actual artifact objects
        self.active_artifacts = []
        self.active_orbs = []     # List of active orb effects [name, duration]

        # Window references
        self.window = None       # Reference to game window
        self.parent_view = None  # Reference to parent view

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

        # Apply rendering optimizations
        self.optimize_rendering()

    @property
    def coins(self):
        """
        Get the player's coin count from game state

        Returns:
            int: Number of coins
        """
        from scripts.mechanics.game_state import game_state
        return game_state.coins

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

    def optimize_rendering(self):
        """Apply rendering optimizations"""
        # Set texture filtering to nearest for pixel art
        if hasattr(self, 'texture') and self.texture:
            self.texture.gl_filter = arcade.gl.NEAREST, arcade.gl.NEAREST

        # Preload and cache textures
        self._load_textures()

    def update(self, delta_time):
        """
        Update player state

        Args:
            delta_time: Time since last update in seconds
        """
        # Update dash cooldown (increment timer)
        if hasattr(self, 'dash_timer') and self.dash_timer < self.cooldown * self.cooldown_factor:
            self.dash_timer += delta_time

        # Update orb effects
        for orb in self.active_orbs:
            orb[1] -= delta_time
        self.active_orbs = [orb for orb in self.active_orbs if orb[1] > 0]

        # Update vision blur
        if hasattr(self, 'vision_blur') and self.vision_blur:
            if hasattr(self, 'vision_timer'):
                self.vision_timer -= delta_time
                if self.vision_timer <= 0:
                    self.vision_blur = False

        # Update artifact cooldowns
        for artifact_name in list(self.artifacts.keys()):
            if self.artifacts[artifact_name] > 0:
                self.artifacts[artifact_name] -= delta_time

        # Update hitbox
        if hasattr(self, 'big_hitbox_timer') and self.big_hitbox_timer > 0:
            self.big_hitbox_timer -= delta_time

            # Apply hitbox effect
            if hasattr(self, 'hitbox_factor') and hasattr(self, 'original_size') and self.original_size:
                # Calculate new size
                new_width = self.original_size[0] * self.hitbox_factor
                new_height = self.original_size[1] * self.hitbox_factor

                # Apply new size
                self.width = new_width
                self.height = new_height

                # Reset hitbox when timer expires
                if self.big_hitbox_timer <= 0:
                    self.width = self.original_size[0]
                    self.height = self.original_size[1]
                    self.hitbox_factor = 1.0

        # Update invincibility
        if hasattr(self, 'invincible') and self.invincible:
            if hasattr(self, 'invincibility_timer'):
                self.invincibility_timer += delta_time
                if hasattr(self, 'blink_timer'):
                    self.blink_timer += delta_time
                    if self.blink_timer >= 0.1:
                        if hasattr(self, 'blink_state'):
                            self.blink_state = not self.blink_state
                        self.blink_timer = 0
                if self.invincibility_timer >= 1.0:
                    self.invincible = False
                    if hasattr(self, 'blink_state'):
                        self.blink_state = True

        # Handle target-based movement (from right-click)
        if hasattr(self, 'target_x') and self.target_x is not None and hasattr(self, 'target_y') and self.target_y is not None:
            dx = self.target_x - self.center_x
            dy = self.target_y - self.center_y
            dist = math.sqrt(dx**2 + dy**2)

            if dist < 5:  # Close enough to target
                self.change_x = 0
                self.change_y = 0
                self.target_x = None
                self.target_y = None
            else:
                # Normalize direction
                direction_x = dx / dist
                direction_y = dy / dist

                # Apply inverse movement if active
                if hasattr(self, 'inverse_move') and self.inverse_move:
                    direction_x = -direction_x
                    direction_y = -direction_y

                # Calculate speed
                base_speed = 1.6  # Reduced base speed for target movement
                if hasattr(self, 'speed_bonus'):
                    base_speed *= self.speed_bonus

                # Apply delta time to make movement frame-rate independent
                speed = base_speed * 60 * delta_time  # 60 is target FPS

                # Set movement velocity
                self.change_x = direction_x * speed
                self.change_y = direction_y * speed

                # Update position
                self.center_x += self.change_x
                self.center_y += self.change_y

        # Call parent update method
        super().update()

    def update_orb_status(self, delta_time):
        """Update active orb effects"""
        # Update orb durations
        for orb in self.active_orbs:
            orb[1] -= delta_time

        # Remove expired orbs
        self.active_orbs = [orb for orb in self.active_orbs if orb[1] > 0]

    def update_appearance(self):
        """Update player appearance after skin change"""
        self._load_textures()

    def try_dash(self):
        """Attempt to perform a dash if cooldown allows"""
        # Calculate effective cooldown
        effective_cooldown = self.cooldown * self.cooldown_factor

        # Check if dash is available
        if self.dash_timer >= effective_cooldown:
            self.perform_dash()
            self.dash_timer = 0  # Reset cooldown timer

            # Update artifacts dictionary if it exists
            if hasattr(self, 'artifacts') and 'Dash' in self.artifacts:
                self.artifacts['Dash'] = effective_cooldown  # Set to full cooldown

            return True
        else:
            remaining = effective_cooldown - self.dash_timer
            print(f"⏱️ Dash on cooldown! ({remaining:.1f}s remaining)")
            return False
    def set_target(self, x, y):
        """
        Set a target position for the player to move towards

        Args:
            x: Target X position
            y: Target Y position
        """
        self.target_x = x
        self.target_y = y

        # Calculate direction to target
        dx = x - self.center_x
        dy = y - self.center_y
        distance = math.sqrt(dx**2 + dy**2)

        if distance > 0:
            # Normalize direction
            self.last_move_direction = (dx / distance, dy / distance)

    def move_towards_mouse(self, view, delta_time):
        """
        Move the player towards the mouse position

        Args:
            view: The game view
            delta_time: Time since last update in seconds
        """
        if not hasattr(view, 'mouse_x') or not hasattr(view, 'mouse_y'):
            return

        # Get mouse position
        mouse_x = view.mouse_x
        mouse_y = view.mouse_y

        # Calculate direction to mouse
        dx = mouse_x - self.center_x
        dy = mouse_y - self.center_y

        # Calculate distance to mouse
        distance = math.sqrt(dx**2 + dy**2)

        # Only move if we're far enough from the mouse
        if distance > 5:
            # Normalize the direction
            direction_x = dx / distance
            direction_y = dy / distance

            # Apply inverse movement if active
            if hasattr(self, 'inverse_move') and self.inverse_move:
                direction_x = -direction_x
                direction_y = -direction_y

            # Calculate speed based on movement mode
            base_speed = 2.0  # Reduced base speed for mouse movement

            # Apply speed bonus from orbs
            if hasattr(self, 'speed_bonus'):
                base_speed *= self.speed_bonus

            # Apply delta time to make movement frame-rate independent
            speed = base_speed * 60 * delta_time  # 60 is target FPS

            # Set movement velocity
            self.change_x = direction_x * speed
            self.change_y = direction_y * speed

            # Update position
            self.center_x += self.change_x
            self.center_y += self.change_y

            # Store last move direction
            self.last_move_direction = (direction_x, direction_y)
        else:
            # Stop moving if close to target
            self.change_x = 0
            self.change_y = 0

    def perform_dash(self):
        """Perform a dash in the current movement direction"""
        # Get dash direction
        if hasattr(self, 'last_move_direction') and self.last_move_direction:
            direction_x, direction_y = self.last_move_direction
        else:
            # Default to up if no direction
            direction_x, direction_y = 0, 1

        # Calculate dash distance
        dash_distance = 100  # DASH_DISTANCE

        # Apply dash movement
        self.center_x += direction_x * dash_distance
        self.center_y += direction_y * dash_distance

        # Create dash effect
        self.create_dash_effect(direction_x, direction_y)

        # Set invincibility
        self.invincible = True
        self.invincibility_timer = 0
        self.dash_timer = 0

        print("⚡ Dash used!")
        
    def create_dash_effect(self, direction_x, direction_y):
        """
        Create a visual effect for the dash

        Args:
            direction_x: X direction of dash
            direction_y: Y direction of dash
        """
        # This is a simple implementation - you can enhance it later
        # For now, we'll just print a message
        print(f"Dash effect in direction ({direction_x:.2f}, {direction_y:.2f})")

        # In a full implementation, you might create particle effects here
        # For example:
        # for i in range(5):
        #     particle = DashParticle(self.center_x, self.center_y, direction_x, direction_y)
        #     self.game_view.particle_list.append(particle)

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

    def draw_artifacts(self):
        """Draw artifact slots and cooldowns"""
        start_x = 30
        y = 50
        font = "Kenney Pixel"
        font_size = 13
        bar_width = 50
        bar_height = 6
        bar_offset = -10

        for idx, artifact_name in enumerate(self.artifacts):
            x = start_x + 70 * idx
            text = artifact_name

            # Get cooldown value and max cooldown
            cooldown_value = self.artifacts[artifact_name]

            # For dash, use the effective cooldown
            if artifact_name == 'Dash':
                max_cooldown = self.cooldown * self.cooldown_factor
                # Invert the ratio for dash (0 = just used, max = ready)
                cooldown_ratio = max(0, min(1.0, self.dash_timer / max_cooldown))
            else:
                max_cooldown = 15.0  # Default max cooldown
                # For other artifacts, higher value = more cooldown
                cooldown_ratio = max(0, min(1.0, 1.0 - (cooldown_value / max_cooldown)))

            # Determine if artifact is ready
            ready = cooldown_ratio >= 1.0
            text_color = arcade.color.YELLOW if ready else arcade.color.DARK_GRAY

            # Draw artifact name
            arcade.draw_text(
                text,
                x,
                y,
                text_color,
                font_size=font_size,
                font_name=font,
                anchor_x="left"
            )

            # Draw cooldown bar
            fill_width = bar_width * cooldown_ratio

            # Background bar
            arcade.draw_rectangle_filled(
                x + bar_width / 2,
                y + bar_offset,
                bar_width,
                bar_height,
                arcade.color.DARK_GRAY
            )

            # Yellow fill indicating time until ready
            arcade.draw_rectangle_filled(
                x + fill_width / 2,
                y + bar_offset,
                fill_width,
                bar_height,
                arcade.color.YELLOW
            )
            
    def draw_orb_status(self, screen_width=800, screen_height=600):
        """Draw active orb effects"""
        x = screen_width - 220
        y = screen_height - 30
        line_height = 20
        i = 0

        if hasattr(self, 'shield') and self.shield:
            arcade.draw_text("🛡️ Shield Active", x, y - i * line_height, arcade.color.LIGHT_GREEN, 14)
            i += 1

        if hasattr(self, 'speed_bonus') and self.speed_bonus > 1.0:
            percent = int((self.speed_bonus - 1) * 100)
            arcade.draw_text(f"⚡ Speed +{percent}%", x, y - i * line_height, arcade.color.LIGHT_BLUE, 14)
            i += 1

        if hasattr(self, 'cooldown_factor') and self.cooldown_factor < 1.0:
            arcade.draw_text(f"⏱️ Cooldown x{self.cooldown_factor}", x, y - i * line_height, arcade.color.ORCHID, 14)
            i += 1

        for orb in self.active_orbs:
            label, time_left = orb
            arcade.draw_text(f"{label} ({int(time_left)}s)", x, y - i * line_height, arcade.color.LIGHT_YELLOW, 14)
            i += 1

    def apply_orb_effect(self, effect_type, duration, value):
        """
        Apply an orb effect to the player

        Args:
            effect_type: Type of effect (speed, cooldown, multiplier, etc.)
            duration: Duration of effect in seconds
            value: Effect value (multiplier or boolean)
        """
        # Add to active orbs list
        effect_name = ""

        if effect_type == "speed":
            self.speed_bonus = value
            effect_name = f"Speed x{value}"
        elif effect_type == "cooldown":
            self.cooldown_factor = value
            effect_name = f"Cooldown x{value}"
        elif effect_type == "multiplier":
            self.multiplier = value
            effect_name = f"Score x{value}"
        elif effect_type == "vision":
            self.vision_blur = value
            self.vision_timer = duration
            effect_name = "Vision Blur" if value else "Vision Enhanced"
        elif effect_type == "hitbox":
            # Store original size if not already stored
            if not hasattr(self, "original_size") or self.original_size is None:
                self.original_size = (self.width, self.height)

            # Don't modify hitbox directly, just store the timer and factor
            self.hitbox_factor = value
            self.big_hitbox_timer = duration

            effect_name = f"Hitbox x{value}"

        # Add to active orbs with duration
        if effect_name:
            # Remove any existing effect of the same type
            self.active_orbs = [orb for orb in self.active_orbs if effect_type not in orb[0].lower()]
            self.active_orbs.append([effect_name, duration])

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

    def add_artifact(self, artifact_name, cooldown, artifact_object=None):
        """
        Add or reset cooldown for an artifact

        Args:
            artifact_name: Name of the artifact
            cooldown: Cooldown time in seconds
            artifact_object: Optional artifact object to store
        """
        self.artifacts[artifact_name] = cooldown
        if artifact_object and artifact_object not in self.artifact_objects:
            self.artifact_objects.append(artifact_object)
        event_manager.publish("artifact_added", artifact_name)

    def _on_artifact_collected(self, artifact_data):
        """Handle artifact collection event"""
        if isinstance(artifact_data, dict) and "name" in artifact_data and "cooldown" in artifact_data:
            self.add_artifact(artifact_data["name"], artifact_data["cooldown"])

    def _on_coin_collected(self, amount):
        """Handle coin collection event"""
        game_state.add_coins(amount)
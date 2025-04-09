import arcade
import math
import random
from src.core.constants import PLAYER_SPEED, PLAYER_DASH_DISTANCE, PLAYER_DASH_COOLDOWN
from src.skins.skin_manager import skin_manager
from src.core.constants import PLAYER_DASH_SPEED
from src.core.scaling import get_scale
from src.entities.player.status_effects import StatusEffect
from src.entities.player.status_effects import StatusEffectManager

class Player(arcade.Sprite):
    """Player character class"""

    def __init__(self, x=0, y=0):
        """Initialize the player."""
        super().__init__()

        # Set position
        self.center_x = x
        self.center_y = y

        # Initialize target position
        self.target_x = None
        self.target_y = None
        self.target_speed_multiplier = 1.0

        # Initialize health and hearts
        self.health = 3
        self.max_health = 3
        self.current_hearts = 3
        self.max_hearts = 3
        self.gold_hearts = 0
        self.golden_overhearts = 0  # Overhearts that are drawn on top of the normal ones
        self.max_heart_slots = 3    # how many gray hearts can be shown
        
        # Heart-related attributes
        self.heart_textures = None  # Will be set by game_view
        self.max_slots = 9  # Maximum heart slots

        # Heart positioning
        self.heart_start_x = 50
        self.heart_y = 50
        self.heart_spacing = 40
        self.heart_width = 30
        self.heart_height = 30

        # Initialize invulnerability
        self.invulnerable = False
        self.invulnerable_timer = 0

        # Initialize invincibility (seems to be used interchangeably with invulnerable)
        self.invincible = False
        self.invincibility_timer = 0
        self.blink_timer = 0

        # Debug what textures are available
        print(f"🔍 Available textures in skin manager: {list(skin_manager.textures.keys())}")

        # Try to get the player texture
        player_texture = skin_manager.get_texture("player", "player")
        if player_texture:
            self.texture = player_texture
            print(f"✅ Successfully set player texture")
        else:
            # Fallback to a simple shape if texture can't be loaded
            self.texture = arcade.make_circle_texture(64, arcade.color.WHITE)
            print("⚠️ Using fallback player texture (white circle)")
        
        # Set scale using centralized system
        self.scale = get_scale('player')
        print(f"🔍 Setting player scale to: {self.scale}")
        
        # Initialize movement
        self.change_x = 0
        self.change_y = 0
        self.speed = PLAYER_SPEED  # Pixels per second
        self.base_speed = PLAYER_SPEED
        self.speed_bonus = 0  # Default speed bonus (0 = no bonus)
        self.speed_multiplier = 1.0
        self.speed_buff_timer = 0.0
        self.inverse_move = False
        self.move_threshold = 5  # Distance at which we consider "arrived"
        self.is_moving = False

        # Initialize dash
        self.can_dash = True
        self.dash_cooldown = 0.0
        self.base_dash_cooldown = PLAYER_DASH_COOLDOWN
        self.dash_speed = PLAYER_DASH_SPEED
        self.dash_duration = 0.15
        self.dash_timer = 0.0
        self.dashing = False
        self.is_dashing = False  # Alternative flag for dashing state
        self.dash_direction_x = 0
        self.dash_direction_y = 0

        # Initialize shield
        self.shield_active = False
        self.has_shield = False
        self.shield_timer = 0.0
        self.shield = 0

        # Initialize score
        self.score = 0
        self.multiplier = 1.0
        self.score_multiplier = 1.0

        # Player currency
        self.coins = 0

        # Player artifacts
        self.artifacts = []
        self.artifact_slots = []
        self.max_slots = self.max_health  # Number of artifact slots tied to max health
        self.artifact_cooldowns = {}
        self.active_artifacts = {}

        # Status effects
        self.vision_blurred = False
        self.vision_blur_timer = 0.0
        self.hitbox_multiplier = 1.0
        self.hitbox_timer = 0.0

        # Create StatusEffectManager with self
        self.status_effects = StatusEffectManager(self)

        # Pickup messages
        self.pickup_texts = []

        # Parent view reference
        self.parent_view = None
        self.window = None

        # Dash effect
        self.dash_particles = []

        # Collision radius for more accurate collision detection
        self.collision_radius = 10  # Adjust as needed

        # Load textures
        self._load_textures()

    def _load_textures(self):
        """Load player textures."""
        # Heart textures
        self.heart_textures = {
            "red": skin_manager.get_texture("ui", "heart_red"),
            "gray": skin_manager.get_texture("ui", "heart_gray"),
            "gold": skin_manager.get_texture("ui", "heart_gold")
        }
        
        print("❤️ Heart textures loaded:")
        for key, tex in self.heart_textures.items():
            print(f" - {key}: {'✅' if tex else '❌'}")

    def update(self, delta_time=1/60):
        """Update player movement"""
        # Handle other updates (status effects, etc.)
        if hasattr(self, 'status_effects'):
            self.status_effects.update(delta_time)

        # Handle invulnerability if it exists
        if hasattr(self, 'invulnerable') and self.invulnerable:
            if not hasattr(self, 'invulnerable_timer'):
                self.invulnerable_timer = 0

            self.invulnerable_timer -= delta_time
            if self.invulnerable_timer <= 0:
                self.invulnerable = False
                self.invulnerable_timer = 0
                self.alpha = 255  # Fully visible
            else:
                # Flash while invulnerable
                if int(self.invulnerable_timer * 10) % 2 == 0:
                    self.alpha = 128  # Semi-transparent
                else:
                    self.alpha = 255  # Fully visible

        # Set base speed for smooth movement
        self.base_speed = PLAYER_SPEED

        # If we have a target, move toward it
        if self.target_x is not None and self.target_y is not None:
            dx = self.target_x - self.center_x
            dy = self.target_y - self.center_y
            distance = math.hypot(dx, dy)
            
            if distance > 1:
                direction_x = dx / distance
                direction_y = dy / distance
                move_speed = self.base_speed * self.speed_multiplier * self.target_speed_multiplier
                self.center_x += direction_x * move_speed * delta_time
                self.center_y += direction_y * move_speed * delta_time
                self.is_moving = True
                
                # Set change_x and change_y for animation purposes
                self.change_x = direction_x * move_speed
                self.change_y = direction_y * move_speed
                
                # Log movement occasionally
                if random.random() < 0.05:  # 5% chance to log
                    print(f"🏃 Moving toward ({self.target_x}, {self.target_y}) with velocity ({self.change_x:.2f}, {self.change_y:.2f})")
            else:
                # We've reached the target
                self.change_x = 0
                self.change_y = 0
                self.is_moving = False
                print(f"✅ Arrived at target ({self.target_x}, {self.target_y})")
        else:
            # No target, don't move
            self.change_x = 0
            self.change_y = 0
            self.is_moving = False

        # Keep player on screen
        window = arcade.get_window()
        if self.left < 0:
            self.left = 0
        elif self.right > window.width:
            self.right = window.width

        if self.bottom < 0:
            self.bottom = 0
        elif self.top > window.height:
            self.top = window.height

        # Update animation if it exists
        if hasattr(self, 'update_animation'):
            self.update_animation(delta_time)

    def update_hitbox(self):
        """Update the player's hitbox based on hitbox_multiplier."""
        if hasattr(self, 'hit_box'):
            # Scale the hit box
            self.hit_box = [
                point * self.hitbox_multiplier for point in self.hit_box
            ]

    def update_dash(self, delta_time):
        """Update player dash state"""
        if self.dash_timer > 0:
            # Continue dash
            self.center_x += self.dash_direction_x * self.dash_speed * delta_time
            self.center_y += self.dash_direction_y * self.dash_speed * delta_time
            self.dash_timer -= delta_time

            # Create dash particles
            if random.random() < 0.3:
                self.dash_particles.append({
                    "x": self.center_x - self.dash_direction_x * 20,
                    "y": self.center_y - self.dash_direction_y * 20,
                    "size": random.uniform(3, 8),
                    "life": 0.5
                })
        else:
            # End dash
            self.dashing = False
            self.dash_speed = 0
    def apply_effect(self, effect_type, value, duration, is_percentage=True):
        """Apply an effect to the player."""
        self.status_effects.add_effect(effect_type, duration, {
            "value": value
        })

    def set_target(self, x, y, speed_multiplier=1.0):
        """Set a new movement target"""
        self.target_x = x
        self.target_y = y
        self.target_speed_multiplier = speed_multiplier
        self.is_moving = True

        # Log only when target is set, not every frame
        #print(f"🎯 Set player target to ({x}, {y})")

    def perform_dash(self):
        """Perform a dash in the target direction"""
        if self.dash_cooldown <= 0:
            # Calculate dash direction
            if self.target_x is not None and self.target_y is not None:
                # Dash toward target
                dx = self.target_x - self.center_x
                dy = self.target_y - self.center_y
            else:
                # Dash in movement direction
                dx = self.change_x
                dy = self.change_y

            # Normalize direction
            length = math.sqrt(dx * dx + dy * dy)
            if length > 0:
                self.dash_direction_x = dx / length
                self.dash_direction_y = dy / length
                
                # Start dash
                self.dashing = True
                self.dash_timer = 0.2  # Dash duration in seconds
                self.dash_speed = self.dash_distance / self.dash_timer
                self.dash_cooldown = self.dash_cooldown_max

                # Make player invincible during dash
                self.invincible = True
                self.invincible_timer = self.dash_timer

    def try_dash(self):
        """Try to perform a dash if conditions are met"""
        self.perform_dash()

    def take_damage(self, amount=1):
        """Take damage and check if defeated."""
        # Initialize attributes if they don't exist
        if not hasattr(self, 'invulnerable'):
            self.invulnerable = False
        if not hasattr(self, 'invincible'):
            self.invincible = False
        if not hasattr(self, 'invulnerable_timer'):
            self.invulnerable_timer = 0
        if not hasattr(self, 'has_shield'):
            self.has_shield = False

        # Check if invulnerable or has shield
        if self.invulnerable or self.invincible:
            return False

        # Check if has shield
        if self.has_shield:
            self.has_shield = False
            print("🛡️ Shield absorbed damage!")
            return False

        # Apply damage to health
        if hasattr(self, 'health'):
            self.health -= amount

        # Apply damage to hearts
        if hasattr(self, 'current_hearts'):
            self.current_hearts = max(0, self.current_hearts - amount)

        # Make invulnerable temporarily
        self.invulnerable = True
        self.invincible = True
        self.invulnerable_timer = 1.0  # 1 second of invulnerability

        # Play damage sound
        try:
            from src.audio.sound_manager import sound_manager
            sound_manager.play_sound('player', 'damage')
        except Exception as e:
            print(f"Error playing damage sound: {e}")
            try:
                # Alternative sound manager call
                from src.audio.sound_manager import sound_manager
                sound_manager.play_sound('player_hit')
            except Exception as e2:
                print(f"Error playing alternative damage sound: {e2}")

        # Check if defeated
        if (hasattr(self, 'health') and self.health <= 0) or \
           (hasattr(self, 'current_hearts') and self.current_hearts <= 0):
            if hasattr(self, 'health'):
                self.health = 0
            if hasattr(self, 'current_hearts'):
                self.current_hearts = 0

            # Call on_death if it exists
            if hasattr(self, 'on_death'):
                self.on_death()

            return True

        return False

    def on_death(self):
        """Handle player death"""
        # TODO: Implement death handling
        pass

    def collect_coin(self):
        """Handle coin collection."""
        # Increase score or currency
        if hasattr(self, 'coins'):
            self.coins += 1
        else:
            self.coins = 1

        # Play sound effect if available
        try:
            arcade.play_sound(self.coin_sound)
        except:
            pass

        # Add visual feedback
        #if hasattr(self, 'parent_view') and hasattr(self.parent_view, 'show_pickup_text'):
           # self.parent_view.show_pickup_text("+1 Coin", arcade.color.GREEN)

        return True  # Return True to indicate successful collection

    def apply_speed_bonus(self, multiplier, duration=None):
        """Apply a speed bonus to the player.

        Args:
            multiplier: The speed multiplier to apply
            duration: Optional duration in seconds. If None, bonus is permanent.
        """
        self.speed_bonus = multiplier - 1  # Convert multiplier to bonus

        if duration:
            # Add as a status effect
            self.status_effects.add_effect("speed", duration, {
                "value": multiplier - 1
            })

    def reset_speed_bonus(self):
        """Reset speed bonus to default value."""
        self.speed_bonus = 0

    def apply_buff(self, buff_type, value, duration):
        """Apply a buff to the player.

        Args:
            buff_type: Type of buff (e.g., 'speed', 'health', etc.)
            value: Value of the buff
            duration: Optional duration in seconds
        """
        # Use status effect manager to handle buffs
        self.status_effects.add_effect(buff_type, duration, {
            "value": value
        })

    def apply_orb_effect(self, orb):
        """Apply an orb effect to the player."""
        if hasattr(orb, "apply_effect"):
            orb.apply_effect(self)

    def add_orb_effect(self, orb_type, duration):
        """Add an orb effect to the player."""
        print(f"Player.add_orb_effect called with: {orb_type}, {duration}")

        # Make sure status_effects exists
        if not hasattr(self, 'status_effects'):
            print("Creating status_effects manager")
            from src.entities.player.status_effects import StatusEffectManager
            self.status_effects = StatusEffectManager(self)

        # Add the effect
        success = self.status_effects.add_effect(orb_type, duration)
        print(f"Effect added to player: {success}, active effects: {list(self.status_effects.effects.keys())}")
        return success

    def draw_hearts(self):
        """Draw the player's health as hearts."""
        # Initialize heart textures if not already set
        if not hasattr(self, 'heart_textures') or not self.heart_textures:
            from src.skins.skin_manager import skin_manager
            self.heart_textures = {
                "red": skin_manager.get_texture("ui", "heart_red"),
                "gray": skin_manager.get_texture("ui", "heart_gray"),
                "gold": skin_manager.get_texture("ui", "heart_gold")
            }
        
        #print("❤️ Heart textures:", self.heart_textures)
            
        if not self.heart_textures:
            return  # Skip if textures aren't set

        from src.core.constants import SCREEN_HEIGHT
        
        heart_size = 32
        spacing = 26  # Slightly overlap
        base_x = 35  # Moved more to the right
        base_y = SCREEN_HEIGHT - 40  # Push to top left

        # Ensure current_hearts is not negative
        current_hearts = max(0, int(self.current_hearts))
        
        # Draw hearts for each slot up to max_slots
        for i in range(self.max_slots):
            x = base_x + i * spacing
            
            if i < current_hearts:
                # Red hearts for current health
                if i >= self.max_health:  # Extra hearts (from powerups)
                    texture = self.heart_textures.get("gold")
                else:  # Regular hearts
                    texture = self.heart_textures.get("red")
            else:
                # Gray hearts for empty slots
                texture = self.heart_textures.get("gray")
                
            if texture:
                arcade.draw_texture_rectangle(x, base_y, heart_size, heart_size, texture)

    def draw(self):
        """Draw the player."""
        # Check for invincibility/invulnerability
        is_invulnerable = False

        if hasattr(self, 'invincible') and self.invincible:
            is_invulnerable = True
        elif hasattr(self, 'invulnerable') and self.invulnerable:
            is_invulnerable = True

        # Flash when invulnerable
        if is_invulnerable:
            import time
            if int(time.time() * 10) % 2 == 0:
                self.alpha = 128
            else:
                self.alpha = 255
        else:
            # Ensure full opacity when not invulnerable
            self.alpha = 255

        # Draw the sprite
        super().draw()

        # Draw any additional effects
        if hasattr(self, 'has_shield') and self.has_shield:
            # Draw shield effect
            arcade.draw_circle_outline(
                self.center_x, self.center_y,
                self.width * 0.7,
                arcade.color.BLUE, 3
            )

        # Draw dash particles
        for particle in self.dash_particles:
            arcade.draw_circle_filled(
                particle["x"], particle["y"],
                particle["size"],
                arcade.color.WHITE,
                num_segments=8
            )

    def draw_effects(self, screen_width, screen_height):
        """Draw status effect indicators."""
        if hasattr(self, 'status_effects'):
            self.status_effects.draw_effect_indicators(screen_width, screen_height)
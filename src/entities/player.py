import arcade
import math
import random
from src.core.constants import PLAYER_SPEED, PLAYER_DASH_DISTANCE, PLAYER_DASH_COOLDOWN
from src.skins.skin_manager import skin_manager
from src.core.constants import PLAYER_DASH_SPEED

class Player(arcade.Sprite):
    """Player character class"""

    def __init__(self, x=0, y=0):
        super().__init__()

        # Set up player texture
        self.texture = skin_manager.get_texture('player', 'default')
        self.scale = skin_manager.get_player_scale()
        
        # Set initial position
        self.center_x = x
        self.center_y = y

        # Player movement
        self.change_x = 0
        self.change_y = 0
        self.target_x = None
        self.target_y = None
        self.speed = PLAYER_SPEED
        self.speed_multiplier = 1.0
        self.speed_buff_timer = 0.0
        self.inverse_move = False
        
        # Movement attributes
        self.speed_bonus = 1.0  # Default speed multiplier (1.0 = normal speed)

        # Player dash
        self.can_dash = True
        self.dash_cooldown = 0.0
        self.dash_speed = PLAYER_DASH_SPEED
        self.dash_duration = 0.15
        self.dash_timer = 0.0
        self.dashing = False
        self.dash_direction_x = 0
        self.dash_direction_y = 0

        # Player health
        self.max_health = 3
        self.health = 3
        self.gold_hearts = 0
        self.shield_active = False
        self.shield_timer = 0.0
        self.shield = 0

        # Heart-related attributes
        self.heart_textures = None  # Will be set by game_view
        self.max_slots = 9  # Default value
        self.current_hearts = 3  # Default value

        # Heart positioning
        self.heart_start_x = 50
        self.heart_y = 30
        self.heart_spacing = 40
        self.heart_width = 30
        self.heart_height = 30

        # Player invincibility
        self.invincible = False
        self.invincible_timer = 0

        # Player currency
        self.coins = 0

        # Player score multiplier
        self.multiplier = 1.0
        self.score_multiplier = 1.0

        # Player artifacts
        self.artifacts = []
        self.artifact_slots = []
        self.max_slots = self.max_health  # Number of artifact slots tied to max health
        self.artifact_cooldowns = {}
        self.active_artifacts = {}

        # Active orb effects
        self.active_orbs = []

        # Initialize active effects dictionary
        self.active_effects = {}

        # Status effects
        self.vision_blur = False
        self.vision_blur_timer = 0.0
        self.hitbox_multiplier = 1.0
        self.hitbox_timer = 0.0

        # Pickup messages
        self.pickup_texts = []

        # Parent view reference
        self.parent_view = None
        self.window = None

        # Dash effect
        self.dash_particles = []

    def update(self, delta_time):
        """Update the player.

        Args:
            delta_time: Time since last update.
        """
        # Update dash cooldown
        if not self.can_dash:
            self.dash_cooldown -= delta_time
            if self.dash_cooldown <= 0:
                self.can_dash = True
                self.dash_cooldown = 0

        # Update dash timer
        if self.dashing:
            self.dash_timer -= delta_time
            if self.dash_timer <= 0:
                self.dashing = False
                self.dash_timer = 0
                self.change_x = 0
                self.change_y = 0
        else:
            # Move towards target if set
            if self.target_x is not None and self.target_y is not None:
                # Calculate direction vector
                dx = self.target_x - self.center_x
                dy = self.target_y - self.center_y
                distance = math.sqrt(dx*dx + dy*dy)

                # If we're close enough to the target, stop moving
                if distance < 5:
                    self.change_x = 0
                    self.change_y = 0
                    self.target_x = None
                    self.target_y = None
                else:
                    # Normalize direction vector and scale by speed
                    speed = PLAYER_SPEED * self.speed_bonus
                    dx = dx / distance * speed
                    dy = dy / distance * speed

                    # Apply inverse movement if active
                    if self.inverse_move:
                        dx = -dx
                        dy = -dy

                    self.center_x += dx * delta_time
                    self.center_y += dy * delta_time

        # Update speed buff timer
        if self.speed_buff_timer > 0:
            self.speed_buff_timer -= delta_time
            if self.speed_buff_timer <= 0:
                self.speed_multiplier = 1.0

        # Update invincibility timer
        if self.invincible:
            self.invincible_timer -= delta_time
            if self.invincible_timer <= 0:
                self.invincible = False

        # Update shield timer
        if self.shield_active:
            self.shield_timer -= delta_time
            if self.shield_timer <= 0:
                self.shield_active = False

        # Keep player on screen
        self.center_x = max(0, min(self.center_x, arcade.get_window().width))
        self.center_y = max(0, min(self.center_y, arcade.get_window().height))

        # Update orb effects
        self.update_orb_effects(delta_time)
        
        # Update active effects
        self.update_effects(delta_time)

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

    def update_orb_effects(self, delta_time):
        """Update active orb effects"""
        # Update orb timers and remove expired effects
        updated_orbs = []
        for orb in self.active_orbs:
            orb_type, time_left = orb
            time_left -= delta_time
            if time_left > 0:
                updated_orbs.append((orb_type, time_left))
            else:
                # Remove effect when expired
                self.remove_orb_effect(orb_type)

        self.active_orbs = updated_orbs

    def apply_effect(self, effect_type, value, duration, is_percentage=True):
        """Apply an effect to the player."""
        # Generate a unique key for this effect
        effect_key = f"{effect_type}_{len(self.active_effects)}"

        # Determine color based on effect type
        color = arcade.color.WHITE
        if 'speed' in effect_type:
            color = arcade.color.YELLOW
        elif 'shield' in effect_type:
            color = arcade.color.BLUE
        elif 'mult' in effect_type:
            color = arcade.color.GREEN
        elif 'cooldown' in effect_type:
            color = arcade.color.PURPLE

        # Add the effect to active effects
        self.active_effects[effect_key] = {
            'value': value,
            'duration': duration,
            'color': color,
            'is_percentage': is_percentage
        }

        # Apply the effect
        if 'speed' in effect_type:
            self.speed_multiplier += value / 100 if is_percentage else value
        elif 'shield' in effect_type:
            self.shield += value
        # ... handle other effect types ...

    def update_effects(self, delta_time):
        """Update active effects and remove expired ones."""
        effects_to_remove = []

        for effect_key, effect_data in self.active_effects.items():
            # Reduce duration
            effect_data['duration'] -= delta_time

            # Check if effect has expired
            if effect_data['duration'] <= 0:
                effects_to_remove.append(effect_key)

        # Remove expired effects
        for effect_key in effects_to_remove:
            effect_data = self.active_effects[effect_key]
            effect_type = effect_key.split('_')[0]

            # Revert the effect
            if 'speed' in effect_type:
                self.speed_multiplier -= effect_data['value'] / 100 if effect_data['is_percentage'] else effect_data['value']
            elif 'shield' in effect_type:
                self.shield -= effect_data['value']
            # ... handle other effect types ...

            # Remove from active effects
            del self.active_effects[effect_key]

    def set_target(self, x, y):
        """Set a target position for the player to move towards"""
        self.target_x = x
        self.target_y = y

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

    def take_damage(self, amount=1.0):
        """Handle player taking damage."""
        if self.invincible or self.shield_active:
            # If player has a shield, remove it instead of taking damage
            if self.shield_active:
                self.shield_active = False
                self.shield_timer = 0
                return True  # Damage was blocked
            return False  # No damage taken

        # Reduce health
        self.health -= 1
        self.current_hearts = self.health  # Keep current_hearts in sync

        # Make player invincible briefly
        self.invincible = True
        self.invincible_timer = 1.0

        # Return whether player is still alive
        return self.health > 0

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
        if hasattr(self, 'parent_view') and hasattr(self.parent_view, 'add_pickup_text'):
            self.parent_view.add_pickup_text("Coin collected!", self.center_x, self.center_y)

        return True  # Return True to indicate successful collection

    def apply_speed_bonus(self, multiplier, duration=None):
        """Apply a speed bonus to the player.

        Args:
            multiplier: The speed multiplier to apply
            duration: Optional duration in seconds. If None, bonus is permanent.
        """
        self.speed_bonus = multiplier

        if duration:
            # Schedule removal of the bonus after duration
            arcade.schedule(lambda dt: self.reset_speed_bonus(), duration)

    def reset_speed_bonus(self):
        """Reset speed bonus to default value."""
        self.speed_bonus = 1.0

    def apply_buff(self, buff_type, value, duration=None):
        """Apply a buff to the player.

        Args:
            buff_type: Type of buff (e.g., 'speed', 'health', etc.)
            value: Value of the buff
            duration: Optional duration in seconds
        """
        if buff_type == 'speed':
            self.apply_speed_bonus(value, duration)
        elif buff_type == 'health':
            self.health += value
            self.current_hearts = self.health
        elif buff_type == 'shield':
            self.shield_active = True
            if duration:
                self.shield_timer = duration
        elif buff_type == 'invincibility':
            self.invincible = True
            if duration:
                self.invincible_timer = duration
        elif buff_type == 'score_multiplier':
            self.score_multiplier = value
            if duration:
                # Reset after duration
                arcade.schedule(lambda dt: setattr(self, 'score_multiplier', 1.0), duration)

    def add_orb_effect(self, orb_type, duration):
        """Add an orb effect to the player"""
        # Check if this effect already exists
        for i, (existing_type, time_left) in enumerate(self.active_orbs):
            if existing_type == orb_type:
                # Replace with longer duration
                self.active_orbs[i] = (orb_type, max(time_left, duration))
                return

        # Add new effect
        self.active_orbs.append((orb_type, duration))

        # Apply effect
        if orb_type.startswith("speed_"):
            speed_bonus = int(orb_type.split("_")[1]) / 100
            self.speed_bonus += speed_bonus
        elif orb_type.startswith("mult_"):
            mult_bonus = float(orb_type.split("_")[1].replace("_", "."))
            self.multiplier *= mult_bonus
        elif orb_type == "shield":
            self.shield_active = True
        elif orb_type == "slow":
            self.speed_bonus *= 0.5
        elif orb_type == "mult_down_0_5":
            self.multiplier *= 0.5
        elif orb_type == "mult_down_0_25":
            self.multiplier *= 0.25
        elif orb_type == "vision":
            # TODO: Implement vision effect
            pass
        elif orb_type == "hitbox":
            # TODO: Implement hitbox effect
            pass

    def remove_orb_effect(self, orb_type):
        """Remove an orb effect from the player"""
        if orb_type.startswith("speed_"):
            speed_bonus = int(orb_type.split("_")[1]) / 100
            self.speed_bonus -= speed_bonus
        elif orb_type.startswith("mult_"):
            mult_bonus = float(orb_type.split("_")[1].replace("_", "."))
            self.multiplier /= mult_bonus
        elif orb_type == "shield":
            self.shield_active = False
        elif orb_type == "slow":
            self.speed_bonus *= 2.0
        elif orb_type == "mult_down_0_5":
            self.multiplier /= 0.5
        elif orb_type == "mult_down_0_25":
            self.multiplier /= 0.25
        elif orb_type == "vision":
            # TODO: Remove vision effect
            pass
        elif orb_type == "hitbox":
            # TODO: Remove hitbox effect
            pass

    def draw_hearts(self):
        """Draw the player's health as hearts."""
        if not self.heart_textures:
            return  # Skip if textures aren't set

        heart_scale = 0.035  # Adjust as needed

        for i in range(self.max_slots):
            # Determine which heart texture to use
            if i < self.health:  # Use health directly
                if i >= self.max_health:  # Extra hearts (from powerups)
                    texture = self.heart_textures.get("gold")
                else:  # Regular hearts
                    texture = self.heart_textures.get("red")
            else:  # Empty heart slots
                texture = self.heart_textures.get("gray")

            if texture:
                # Draw the heart
                heart_width = texture.width * heart_scale
                heart_height = texture.height * heart_scale
                x = self.heart_start_x + i * self.heart_spacing
                y = self.heart_y
                arcade.draw_texture_rectangle(x, y, heart_width, heart_height, texture)

    def draw(self):
        """Draw the player and effects"""
        # Draw player with alpha if invincible
        alpha = 128 if self.invincible else 255
        self.alpha = alpha
        super().draw()

        # Draw shield if active
        if self.shield_active:
            arcade.draw_circle_outline(
                self.center_x, self.center_y,
                self.width * 0.7,
                arcade.color.LIGHT_BLUE,
                2,
                num_segments=20
            )

        # Draw dash particles
        for particle in self.dash_particles:
            arcade.draw_circle_filled(
                particle["x"], particle["y"],
                particle["size"],
                arcade.color.WHITE,
                num_segments=8
            )
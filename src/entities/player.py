import arcade
import math
from src.core.resource_manager import resource_path
from src.core.constants import PLAYER_SPEED, DASH_DISTANCE, DASH_COOLDOWN
from src.skins.skin_manager import skin_manager

# Global sound variables
damage_sound = None

class Player(arcade.Sprite):
    def __init__(self, x, y, parent_view=None):
        super().__init__()

        global damage_sound
        if damage_sound is None:
            try:
                damage_sound = arcade.load_sound(resource_path("assets/audio/damage.wav"))
            except Exception as e:
                print("Failed to load damage sound:", e)
                damage_sound = None

        self.center_x = x
        self.center_y = y
        self.parent_view = parent_view
        self.target_x = x
        self.target_y = y
        self.can_dash = True
        self.dash_timer = 0
        self.dash_cooldown = DASH_COOLDOWN
        self.invincible = False
        self.invincibility_timer = 0
        self.blink_state = True
        self.max_slots = 3
        self.current_hearts = 3.0
        self.gold_hearts = 0
        self.speed_bonus = 1.0
        self.multiplier = 1.0
        self.shield = False
        self.mult_timer = 0
        self.cooldown_factor = 1.0
        self.cooldown = 1.0
        self.artifacts = []
        self.active_orbs = []  # Will be a list of lists, not tuples
        self.vision_blur = False
        self.vision_timer = 0.0
        self.inverse_move = False
        self.window = None
        self.artifact_cooldowns = {}
        self.pickup_texts = []
        self.coins = 0

        # New attributes to support upgrades
        self.orb_spawn_chance = 0
        self.coin_spawn_chance = 0
        self.damage_negate_chance = 0
        self.has_shield = False
        self.second_chance = False
        self.score_multiplier = 1
        self.base_speed = PLAYER_SPEED

        # Set the scale
        self.scale = 0.035

        # Load textures
        self.update_texture()

    def update_texture(self):
        """Update the texture based on current skin settings"""
        # Get player texture
        texture = skin_manager.get_texture("player", "default")
        if texture:
            self.texture = texture
        else:
            # Create a default texture if skin texture not found
            self.texture = arcade.make_soft_square_texture(30, (255, 255, 255, 255), 255, 10)

        # Load heart textures
        self.heart_textures = {
            "gray": skin_manager.get_texture("hearts", "gray"),
            "red": skin_manager.get_texture("hearts", "red"),
            "gold": skin_manager.get_texture("hearts", "gold"),
        }

        # Fallback for heart textures
        if self.heart_textures["gray"] is None:
            self.heart_textures["gray"] = arcade.load_texture(resource_path("assets/ui/heart_gray.png"))
        if self.heart_textures["red"] is None:
            self.heart_textures["red"] = arcade.load_texture(resource_path("assets/ui/heart_red.png"))
        if self.heart_textures["gold"] is None:
            self.heart_textures["gold"] = arcade.load_texture(resource_path("assets/ui/heart_gold.png"))

    def set_target(self, x, y):
        if self.inverse_move:
            dx = x - self.center_x
            dy = y - self.center_y
            self.target_x = self.center_x - dx
            self.target_y = self.center_y - dy
        else:
            self.target_x = x
            self.target_y = y

    def update(self, delta_time: float = 1 / 60):
        # Update dash timer
        if self.dash_timer < self.dash_cooldown:
            self.dash_timer += delta_time * self.cooldown_factor

        if self.mult_timer > 0:
            self.mult_timer -= delta_time
            if self.mult_timer <= 0:
                self.multiplier = 1.0

        # Update active orbs - using lists instead of tuples
        for orb in self.active_orbs:
            orb[1] -= delta_time
        self.active_orbs = [orb for orb in self.active_orbs if orb[1] > 0]

        if self.vision_blur:
            self.vision_timer -= delta_time
            if self.vision_timer <= 0:
                self.vision_blur = False

        # Update artifact cooldowns
        for artifact in self.artifacts:
            if hasattr(artifact, "cooldown_timer") and artifact.cooldown_timer < artifact.cooldown:
                artifact.cooldown_timer += delta_time

        # Move towards target
        if self.target_x is not None and self.target_y is not None:
            dx = self.target_x - self.center_x
            dy = self.target_y - self.center_y
            dist = math.hypot(dx, dy)
            if dist < 5:
                self.change_x = 0
                self.change_y = 0
                self.target_x = None
                self.target_y = None
            else:
                direction_x = dx / dist
                direction_y = dy / dist
                speed = self.base_speed * self.speed_bonus * delta_time
                self.change_x = direction_x * speed
                self.change_y = direction_y * speed
                self.center_x += self.change_x
                self.center_y += self.change_y

        # Handle invincibility blinking
        if self.invincible:
            self.invincibility_timer += delta_time
            if int(self.invincibility_timer * 10) % 2 == 0:
                self.blink_state = False
            else:
                self.blink_state = True
            if self.invincibility_timer >= 1.0:
                self.invincible = False
                self.invincibility_timer = 0
                self.blink_state = True

        # Handle hitbox size changes
        if hasattr(self, "big_hitbox_timer") and self.big_hitbox_timer > 0:
            self.big_hitbox_timer -= delta_time
            if self.big_hitbox_timer <= 0:
                self.width, self.height = self.original_size
                self.set_hit_box(self.texture.hit_box_points)

    def try_dash(self):
        """Attempt to dash if cooldown is ready"""
        if self.dash_timer >= self.dash_cooldown:
            self.perform_dash()
            self.dash_timer = 0
            return True
        else:
            print(f"? Dash on cooldown. {self.dash_timer:.1f}/{self.dash_cooldown:.1f}s")
            return False

    def perform_dash(self):
        """Perform the dash movement"""
        if self.target_x is None or self.target_y is None:
            # If no target, dash in current direction
            if self.change_x != 0 or self.change_y != 0:
                # Normalize direction
                magnitude = math.sqrt(self.change_x**2 + self.change_y**2)
                direction_x = self.change_x / magnitude
                direction_y = self.change_y / magnitude

                # Apply dash
                self.center_x += direction_x * DASH_DISTANCE
                self.center_y += direction_y * DASH_DISTANCE
            return

        # Dash toward target
        dx = self.target_x - self.center_x
        dy = self.target_y - self.center_y
        dist = math.hypot(dx, dy)

        if dist > 0:
            direction_x = dx / dist
            direction_y = dy / dist
            self.center_x += direction_x * DASH_DISTANCE
            self.center_y += direction_y * DASH_DISTANCE

            # Keep player within screen bounds
            if self.left < 0:
                self.left = 0
            elif self.right > 800:
                self.right = 800

            if self.bottom < 0:
                self.bottom = 0
            elif self.top > 600:
                self.top = 600

    def take_damage(self, amount=1):
        if self.invincible:
            return False

        if self.shield:
            self.shield = False
            return False

        # Check for damage negation chance
        if self.damage_negate_chance > 0:
            import random
            if random.random() < self.damage_negate_chance:
                return False

        self.current_hearts -= amount

        # Play damage sound
        if damage_sound:
            arcade.play_sound(damage_sound)

        # Make player invincible for a short time
        self.invincible = True
        self.invincibility_timer = 0

        return True

    def draw(self):
        # Only draw if not blinking while invincible
        if self.blink_state:
            super().draw()

        # Draw shield if active
        if self.shield:
            arcade.draw_circle_outline(
                self.center_x, self.center_y, 
                self.width * 0.6, 
                arcade.color.BLUE, 2
            )

    def draw_health(self):
        """Draw the player's health hearts."""
        heart_scale = 0.035  # Adjust as needed
        heart_spacing = 40
        start_x = 800 - 30  # Right side of screen
        start_y = 570  # Top of screen

        # Draw empty heart slots
        for i in range(self.max_slots):
            x = start_x - i * heart_spacing
            y = start_y
            arcade.draw_scaled_texture_rectangle(
                x, y, self.heart_textures["gray"], heart_scale
            )

        # Draw filled hearts
        full_hearts = int(self.current_hearts)
        for i in range(full_hearts):
            x = start_x - i * heart_spacing
            y = start_y
            arcade.draw_scaled_texture_rectangle(
                x, y, self.heart_textures["red"], heart_scale
            )

        # Draw partial heart if needed
        fraction = self.current_hearts - full_hearts
        if fraction > 0:
            x = start_x - full_hearts * heart_spacing
            y = start_y
            # Draw partial heart (this is simplified - you might want a better visual)
            arcade.draw_scaled_texture_rectangle(
                x, y, self.heart_textures["red"], heart_scale * fraction
            )

        # Draw gold hearts
        for i in range(self.gold_hearts):
            x = start_x - (self.max_slots + i) * heart_spacing
            y = start_y
            arcade.draw_scaled_texture_rectangle(
                x, y, self.heart_textures["gold"], heart_scale
            )

    def add_orb_effect(self, orb_type, duration):
        """Add an orb effect to the player"""
        # Check if we already have this effect
        for i, orb in enumerate(self.active_orbs):
            if orb[0] == orb_type:
                # Replace with longer duration if new one is longer
                if duration > orb[1]:
                    self.active_orbs[i] = [orb_type, duration]
                return

        # Add new effect
        self.active_orbs.append([orb_type, duration])

        # Apply effect
        if orb_type == "speed":
            self.speed_bonus = 1.5
        elif orb_type == "shield":
            self.shield = True
        elif orb_type == "multiplier":
            self.multiplier = 2.0
        elif orb_type == "cooldown":
            self.cooldown_factor = 2.0
        elif orb_type == "vision":
            self.vision_blur = True
            self.vision_timer = duration
        elif orb_type == "hitbox":
            if not hasattr(self, 'original_size'):
                self.original_size = (self.width, self.height)
            self.width *= 1.5
            self.height *= 1.5
            self.big_hitbox_timer = duration

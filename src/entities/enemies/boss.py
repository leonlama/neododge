import arcade
import random
import math
from src.entities.enemies.enemy import Enemy
from src.core.constants import SCREEN_WIDTH, SCREEN_HEIGHT

class Boss(Enemy):
    """A powerful boss enemy that appears in boss waves."""

    def __init__(self, x, y, boss_type="mini_boss"):
        super().__init__(x, y)

        # Set boss type and properties
        self.boss_type = boss_type
        self._setup_boss_properties()

        # Boss movement
        self.movement_timer = 0
        self.movement_pattern = self._get_movement_pattern()
        self.current_pattern_index = 0
        self.pattern_duration = 3.0

        # Boss attacks
        self.attack_timer = 0
        self.attack_cooldown = 2.0
        self.projectiles = []

        # Visual effects
        self.flash_timer = 0
        self.is_flashing = False

        # Sound effects
        self.spawn_sound = arcade.load_sound("assets/sounds/boss_spawn.wav")
        self.attack_sound = arcade.load_sound("assets/sounds/boss_attack.wav")
        self.death_sound = arcade.load_sound("assets/sounds/boss_death.wav")

        # Play spawn sound
        arcade.play_sound(self.spawn_sound)

    def _setup_boss_properties(self):
        """Set up boss properties based on boss type."""
        if self.boss_type == "mini_boss":
            self.health = 10
            self.max_health = 10
            self.speed = 2.0
            self.damage = 1
            self.scale = 1.5
            self.texture = arcade.load_texture("assets/images/enemies/mini_boss.png")
            self.coin_value = 20

        elif self.boss_type == "mid_boss":
            self.health = 20
            self.max_health = 20
            self.speed = 1.8
            self.damage = 2
            self.scale = 2.0
            self.texture = arcade.load_texture("assets/images/enemies/mid_boss.png")
            self.coin_value = 40

        elif self.boss_type == "final_boss":
            self.health = 30
            self.max_health = 30
            self.speed = 1.5
            self.damage = 3
            self.scale = 2.5
            self.texture = arcade.load_texture("assets/images/enemies/final_boss.png")
            self.coin_value = 80

        elif self.boss_type == "ultra_boss":
            self.health = 50
            self.max_health = 50
            self.speed = 1.2
            self.damage = 4
            self.scale = 3.0
            self.texture = arcade.load_texture("assets/images/enemies/ultra_boss.png")
            self.coin_value = 150

        # Fallback to a colored circle if texture loading fails
        if not hasattr(self, 'texture') or self.texture is None:
            colors = {
                "mini_boss": arcade.color.RED,
                "mid_boss": arcade.color.PURPLE,
                "final_boss": arcade.color.DARK_RED,
                "ultra_boss": arcade.color.BLACK
            }
            color = colors.get(self.boss_type, arcade.color.RED)
            self.texture = arcade.make_circle_texture(int(64 * self.scale), color)

    def _get_movement_pattern(self):
        """Get movement pattern based on boss type."""
        if self.boss_type == "mini_boss":
            return self._chase_pattern
        elif self.boss_type == "mid_boss":
            return self._teleport_pattern
        elif self.boss_type == "final_boss":
            return self._circle_pattern
        elif self.boss_type == "ultra_boss":
            return self._complex_pattern
        return self._chase_pattern

    def update(self, delta_time=1/60):
        """Update boss behavior."""
        super().update()

        # Update movement pattern
        self.movement_timer += delta_time
        if self.movement_timer >= self.pattern_duration:
            self.movement_timer = 0
            self.current_pattern_index = (self.current_pattern_index + 1) % len(self.movement_pattern)

        # Execute current movement pattern
        pattern_func = self.movement_pattern[self.current_pattern_index]
        pattern_func(delta_time)

        # Update attack timer
        self.attack_timer += delta_time
        if self.attack_timer >= self.attack_cooldown:
            self.attack_timer = 0
            self.attack()

        # Update visual effects
        if self.is_flashing:
            self.flash_timer += delta_time
            if self.flash_timer >= 0.1:
                self.flash_timer = 0
                self.is_flashing = False

    def attack(self):
        """Perform boss attack based on boss type."""
        if self.boss_type == "mini_boss":
            self._simple_attack()
        elif self.boss_type == "mid_boss":
            self._spread_attack()
        elif self.boss_type == "final_boss":
            self._circle_attack()
        elif self.boss_type == "ultra_boss":
            self._complex_attack()

        # Play attack sound
        arcade.play_sound(self.attack_sound)

    def _simple_attack(self):
        """Simple straight-line projectile attack."""
        # This would be implemented in the game view to spawn projectiles
        # We'll just signal that the boss is attacking
        self.is_flashing = True

    def _spread_attack(self):
        """Attack that fires projectiles in multiple directions."""
        self.is_flashing = True

    def _circle_attack(self):
        """Attack that fires projectiles in a circle."""
        self.is_flashing = True

    def _complex_attack(self):
        """Complex attack pattern combining multiple attack types."""
        self.is_flashing = True

    def _chase_pattern(self, delta_time):
        """Movement pattern: Chase the player."""
        # This would be implemented to move toward the player
        # For now, we'll just move in a simple pattern
        self.center_x += math.cos(self.movement_timer * 2) * self.speed
        self.center_y += math.sin(self.movement_timer * 2) * self.speed

    def _teleport_pattern(self, delta_time):
        """Movement pattern: Teleport around the screen."""
        # Teleport every 1.5 seconds
        if self.movement_timer % 1.5 < delta_time:
            self.center_x = random.randint(50, SCREEN_WIDTH - 50)
            self.center_y = random.randint(50, SCREEN_HEIGHT - 50)
            self.is_flashing = True

    def _circle_pattern(self, delta_time):
        """Movement pattern: Move in a circle."""
        center_x = SCREEN_WIDTH / 2
        center_y = SCREEN_HEIGHT / 2
        radius = min(SCREEN_WIDTH, SCREEN_HEIGHT) / 4

        self.center_x = center_x + radius * math.cos(self.movement_timer)
        self.center_y = center_y + radius * math.sin(self.movement_timer)

    def _complex_pattern(self, delta_time):
        """Movement pattern: Complex combination of patterns."""
        # Alternate between patterns
        pattern_index = int(self.movement_timer / (self.pattern_duration / 3)) % 3

        if pattern_index == 0:
            self._chase_pattern(delta_time)
        elif pattern_index == 1:
            self._circle_pattern(delta_time)
        else:
            self._teleport_pattern(delta_time)

    def take_damage(self, amount):
        """Handle boss taking damage."""
        super().take_damage(amount)
        self.is_flashing = True

        # Check if boss is defeated
        if self.health <= 0:
            arcade.play_sound(self.death_sound)

    def draw(self):
        """Draw the boss with visual effects."""
        # Flash effect when damaged
        if self.is_flashing:
            # Draw with white tint
            arcade.draw_texture_rectangle(
                self.center_x, self.center_y,
                self.width, self.height,
                self.texture,
                alpha=200
            )
        else:
            super().draw()

        # Draw health bar
        health_width = 80
        health_height = 10
        health_x = self.center_x - health_width / 2
        health_y = self.center_y + self.height / 2 + 10

        # Background
        arcade.draw_rectangle_filled(
            health_x + health_width / 2,
            health_y,
            health_width,
            health_height,
            arcade.color.BLACK
        )

        # Health fill
        health_fill = (self.health / self.max_health) * health_width
        if health_fill > 0:
            arcade.draw_rectangle_filled(
                health_x + health_fill / 2,
                health_y,
                health_fill,
                health_height,
                arcade.color.RED
            )
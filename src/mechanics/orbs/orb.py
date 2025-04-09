import arcade
from src.core.scaling import get_scale

class Orb(arcade.Sprite):
    """Base class for all orbs in the game."""

    # Define orb types and their properties
    ORB_TYPES = {
        "speed": {
            "color": arcade.color.BLUE,
            "duration": 5.0,
            "category": "buff"
        },
        "shield": {
            "color": arcade.color.CYAN,
            "duration": 5.0,
            "category": "buff"
        },
        "invincibility": {
            "color": arcade.color.YELLOW,
            "duration": 3.0,
            "category": "buff"
        },
        "slow": {
            "color": arcade.color.PURPLE,
            "duration": 4.0,
            "category": "debuff"
        },
        "damage": {
            "color": arcade.color.RED,
            "duration": 0,  # Instant effect
            "category": "debuff"
        }
    }

    def __init__(self, x, y, orb_type="speed"):
        super().__init__()

        # Position
        self.center_x = x
        self.center_y = y

        # Properties
        self.orb_type = orb_type
        self.properties = self.ORB_TYPES.get(orb_type, self.ORB_TYPES["speed"])
        self.effect_duration = self.properties["duration"]

        # Set appearance
        self._set_appearance()

        # Set scale
        self.scale = get_scale('orb')

    def _set_appearance(self):
        """Set the orb's appearance based on its type"""
        color = self.properties["color"]
        self.texture = arcade.make_soft_circle_texture(20, color)

    def update(self):
        """Standard update method required by arcade.Sprite"""
        # Call the parent class update method (no delta_time)
        super().update()

        # Any non-time-based updates can go here

    def update_with_time(self, delta_time):
        """Time-based update method for orbs"""
        # Any time-based updates can go here
        # For example, animation, movement patterns, etc.
        pass

    def apply_effect(self, player):
        """Apply orb effect to the player."""
        print(f"Applying {self.orb_type} effect with duration {self.effect_duration}")

        # Add debug to check if player has status_effects
        if hasattr(player, 'status_effects'):
            print(f"Player has status_effects attribute")
            # Try to add the effect
            success = player.status_effects.add_effect(self.orb_type, self.effect_duration)
            print(f"Effect added successfully: {success}")
        else:
            print(f"Player missing status_effects attribute!")
            # Fall back to legacy implementation
            if self.orb_type == "speed":
                player.speed_multiplier = 1.5
                player.speed_boost_timer = self.effect_duration
            elif self.orb_type == "shield":
                player.has_shield = True
                player.shield_timer = self.effect_duration
            elif self.orb_type == "invincibility":
                player.is_invincible = True
                player.invincibility_timer = self.effect_duration
            elif self.orb_type == "slow":
                player.speed_multiplier = 0.5
                player.slow_timer = self.effect_duration
            elif self.orb_type == "damage":
                player.take_damage(1)

    @classmethod
    def get_orb_types_by_category(cls, category):
        """Get all orb types in a specific category."""
        return [orb_type for orb_type, props in cls.ORB_TYPES.items() 
                if props["category"] == category]
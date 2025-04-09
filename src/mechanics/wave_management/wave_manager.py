import random
import time
from src.mechanics.wave_management.wave_generator import WaveGenerator

class WaveManager:
    """Manages the creation and progression of waves in the game."""

    # Wave types with their characteristics
    WAVE_TYPES = {
        "normal": {
            "weight": 70,  # Higher weight = more common
            "enemy_count_multiplier": 1.0,
            "enemy_speed_multiplier": 1.0,
            "enemy_health_multiplier": 1.0,
            "formations": ["random", "circle", "grid", "line", "v_shape"],
            "orb_count_multiplier": 1.0,
            "coin_count_multiplier": 1.0
        },
        "swarm": {
            "weight": 15,
            "enemy_count_multiplier": 2.0,  # Double enemies
            "enemy_speed_multiplier": 0.8,  # Slightly slower
            "enemy_health_multiplier": 0.7,  # Weaker enemies
            "formations": ["random", "circle", "spiral"],
            "orb_count_multiplier": 0.5,
            "coin_count_multiplier": 1.5
        },
        "elite": {
            "weight": 10,
            "enemy_count_multiplier": 0.5,  # Fewer enemies
            "enemy_speed_multiplier": 1.2,  # Faster
            "enemy_health_multiplier": 2.0,  # Much stronger
            "formations": ["v_shape", "line"],
            "orb_count_multiplier": 1.5,
            "coin_count_multiplier": 2.0
        },
        "boss": {
            "weight": 5,
            "enemy_count_multiplier": 0.2,  # Very few enemies
            "enemy_speed_multiplier": 0.9,
            "enemy_health_multiplier": 5.0,  # Very strong
            "formations": ["center"],  # Boss in center
            "orb_count_multiplier": 2.0,
            "coin_count_multiplier": 3.0
        }
    }

    def __init__(self, wave_generator, on_spawn_enemy, analytics=None):
        """Initialize the wave manager.

        Args:
            wave_generator: The wave generator to use for creating waves.
            on_spawn_enemy: Callback function for spawning enemies.
            analytics: Optional analytics object for tracking wave data.
        """
        self.wave_generator = wave_generator
        self.on_spawn_enemy = on_spawn_enemy
        self.wave_analytics = analytics
        self.game_view = None
        self.current_wave = 0
        self.wave_timer = 0
        self.wave_duration = 45  # Default duration
        self.in_wave = False
        self.difficulty = 0.3  # Starting difficulty
        self.difficulty_increment = 0.05  # Increase per wave
        self.spawn_timer = 0
        self.spawn_delay = 1.0
        self.enemies_to_spawn = 0
        self.current_config = None  # Add this line to fix the attribute error

        # Callbacks
        self.on_clear_enemies = None
        self.on_wave_complete = None
        self.callbacks = {}

        # Player data
        self.player_profile = {
            "playstyle": {
                "aggression": 0.5,
                "risk": 0.5
            },
            "skill_level": 0.5
        }
        self.engagement_score = 0.5

        # Wave progression
        self.waves_until_boss = random.randint(8, 12)
        self.wave_history = []

    def _setup_callbacks(self):
        """Set up callbacks based on the game_view."""
        # Check if game_view has the necessary methods
        if hasattr(self.game_view, 'spawn_enemy'):
            self.on_spawn_enemy = self.game_view.spawn_enemy

        if hasattr(self.game_view, 'clear_enemies'):
            self.on_clear_enemies = self.game_view.clear_enemies

        if hasattr(self.game_view, 'on_wave_complete'):
            self.on_wave_complete = self.game_view.on_wave_complete

    def update(self, delta_time):
        """Update the wave manager."""
        if not self.in_wave:
            # If we're not in a wave, start a new one after a delay
            if not hasattr(self, 'wave_break_timer'):
                self.wave_break_timer = 3.0  # 3 second break between waves

            self.wave_break_timer -= delta_time
            if self.wave_break_timer <= 0:
                print("Break between waves finished, starting new wave...")
                self.start_wave()
                delattr(self, 'wave_break_timer')  # Remove the timer attribute
            return

        # Update wave timer
        self.wave_timer += delta_time

        # Check if wave is complete
        if self.current_config and self.wave_timer >= self.current_config["duration"]:
            print(f"Wave {self.current_wave} completed (duration reached)")
            self.end_wave()
            return

        # Update spawn timer
        self.spawn_timer += delta_time

        # Spawn enemies if it's time and there are enemies to spawn
        if self.spawn_timer >= self.spawn_delay and self.enemies_to_spawn > 0:
            print(f"Spawning enemy ({self.enemies_to_spawn} remaining)")
            self.spawn_timer = 0
            self.spawn_enemy()

        # Set targets for enemies if game_view has player and enemies
        if hasattr(self.game_view, 'player') and hasattr(self.game_view, 'enemies'):
            for enemy in self.game_view.enemies:
                if hasattr(enemy, 'set_target') and enemy.target is None:
                    enemy.set_target(self.game_view.player)

    def generate_wave_configuration(self):
        """Generate configuration for the next wave"""
        self.current_wave += 1

        # Determine wave type
        wave_type = self._determine_wave_type()

        # Calculate difficulty
        self.difficulty += self.difficulty_increment

        # Get wave type modifiers
        type_config = self.WAVE_TYPES[wave_type]

        # Base values that scale with difficulty
        base_enemy_count = int(4 + self.difficulty * 2)
        base_enemy_speed = 0.8 + self.difficulty * 0.4
        base_enemy_health = 0.8 + self.difficulty * 0.4
        base_orb_count = int(self.difficulty * 3)
        base_coin_count = int(1 + self.difficulty * 2)

        # Apply wave type multipliers
        enemy_count = max(1, int(base_enemy_count * type_config["enemy_count_multiplier"]))

        # Generate enemy types based on difficulty
        enemy_types = self._generate_enemy_types(enemy_count, wave_type)

        # Select formation
        formation = random.choice(type_config["formations"])

        # Configure wave
        config = {
            "type": wave_type,
            "wave_number": self.current_wave,
            "difficulty": self.difficulty,
            "enemy_count": enemy_count,
            "enemy_types": enemy_types,
            "enemy_speed": base_enemy_speed * type_config["enemy_speed_multiplier"],
            "enemy_health": base_enemy_health * type_config["enemy_health_multiplier"],
            "formation": formation,
            "spawn_delay": max(0.2, 1.0 - self.difficulty * 0.5),  # Faster spawns at higher difficulty
            "duration": self.wave_duration,
            "orb_count": int(base_orb_count * type_config["orb_count_multiplier"]),
            "orb_types": self._generate_orb_distribution(),
            "spawn_artifact": random.random() < 0.1 + self.difficulty * 0.05,  # Chance increases with difficulty
            "coin_count": int(base_coin_count * type_config["coin_count_multiplier"])
        }

        print(f"🌊 Wave {self.current_wave}: {wave_type.upper()} | {enemy_count} enemies | Formation: {formation}")

        return config

    def _determine_wave_type(self):
        """Determine the type of the next wave"""
        # Check if it's time for a boss wave
        if self.current_wave % self.waves_until_boss == 0:
            return "boss"

        # Otherwise, weighted random selection
        weights = [self.WAVE_TYPES[t]["weight"] for t in self.WAVE_TYPES]
        wave_types = list(self.WAVE_TYPES.keys())

        # Adjust weights based on wave history to avoid repetition
        if self.wave_history:
            last_wave_type = self.wave_history[-1]["type"]
            # Reduce weight of the last wave type
            if last_wave_type in wave_types:
                idx = wave_types.index(last_wave_type)
                weights[idx] *= 0.5  # 50% less likely to repeat

        return random.choices(wave_types, weights=weights)[0]

    def _generate_enemy_types(self, count, wave_type):
        """Generate a list of enemy types for the wave"""
        enemy_pool = []

        # Basic enemies always available
        enemy_pool.extend(["wander"] * 3)
        enemy_pool.extend(["chaser"] * 2)

        # Add more advanced enemies as difficulty increases
        if self.difficulty > 0.4:
            enemy_pool.extend(["shooter"] * int(self.difficulty * 3))

        if self.difficulty > 0.6:
            enemy_pool.extend(["tank"] * int(self.difficulty * 2))

        if self.difficulty > 0.8:
            enemy_pool.extend(["bomber"] * int(self.difficulty))

        # Special handling for boss waves
        if wave_type == "boss":
            return ["boss"] + random.choices(enemy_pool, k=count-1)

        # For elite waves, ensure at least one elite enemy
        if wave_type == "elite" and self.difficulty > 0.5:
            elite_types = ["elite_chaser", "elite_shooter"]
            return random.choices(elite_types, k=1) + random.choices(enemy_pool, k=count-1)

        # Otherwise random selection
        return random.choices(enemy_pool, k=count)

    def _generate_orb_distribution(self):
        """Generate distribution of orb types"""
        # As difficulty increases, more debuffs
        buff_weight = max(0.5, 0.9 - self.difficulty * 0.3)
        debuff_weight = 1.0 - buff_weight

        return {"buff": buff_weight, "debuff": debuff_weight}

    def start_wave(self):
        """Start a new wave."""
        if self.in_wave:
            print("Already in a wave, can't start a new one")
            return

        self.in_wave = True
        self.wave_timer = 0

        # Generate wave configuration
        config = self.generate_wave_configuration()
        self.current_config = config  # Store current config

        # Store in history
        self.wave_history.append(config)

        # Set wave parameters
        self.wave_duration = config["duration"]
        self.spawn_delay = config["spawn_delay"]
        self.enemies_to_spawn = config["enemy_count"]
        
        # Set up coin spawning parameters
        self.coins_remaining = config['coin_count']
        self.coin_spawn_interval = 1
        self.coin_spawn_timer = 0

        # Reset timers
        self.spawn_timer = 0

        # Spawn orbs for this wave
        if hasattr(self, 'game_view') and config['orb_count'] > 0:
            try:
                self.game_view.spawn_orbs(
                    count=config['orb_count'],
                    orb_types=config['orb_types']
                )
            except Exception as e:
                print(f"Error spawning orbs: {e}")

        # Spawn coins for this wave
        if hasattr(self, 'game_view') and config['coin_count'] > 0:
            try:
                if hasattr(self.game_view, 'spawn_coins'):
                    self.game_view.spawn_coins(config['coin_count'])
                elif hasattr(self.game_view, 'spawn_coin'):
                    for _ in range(min(5, config['coin_count'])):  # Spawn up to 5 coins initially
                        self.game_view.spawn_coin()
                else:
                    print("Warning: Game view doesn't have spawn_coin or spawn_coins method")
            except Exception as e:
                print(f"Error spawning coins: {e}")

        # Display wave message if available
        if hasattr(self.game_view, 'show_wave_message'):
            self.game_view.show_wave_message(f"Wave {self.current_wave}: {config['type'].capitalize()}")

        # Spawn artifact if configured
        if hasattr(self, 'game_view') and config.get('spawn_artifact', False):
            try:
                if hasattr(self.game_view, 'spawn_artifact'):
                    self.game_view.spawn_artifact()
                else:
                    print("Warning: Game view doesn't have spawn_artifact method")
            except Exception as e:
                print(f"Error spawning artifact: {e}")

        # Call the start wave callback
        if hasattr(self, 'on_wave_start'):
            self.on_wave_start(self.current_wave)

        print(f"Starting Wave {self.current_wave}")

        return config

    def end_wave(self):
        """End the current wave"""
        if not self.in_wave:
            print("Not in a wave, can't end it")
            return

        self.in_wave = False

        # Call the end wave callback
        if hasattr(self, 'game_view') and hasattr(self.game_view, 'on_wave_end'):
            self.game_view.on_wave_end(self.current_wave)

        print(f"Ended Wave {self.current_wave}")

        # Set up a timer for the break between waves
        self.wave_break_timer = 5.0  # 5 second break

        # Clear any remaining enemies
        if hasattr(self, 'game_view') and hasattr(self.game_view, 'clear_enemies'):
            self.game_view.clear_enemies()

        # Maybe spawn a reward
        if hasattr(self, 'game_view') and hasattr(self.game_view, 'spawn_wave_reward'):
            self.game_view.spawn_wave_reward(self.current_wave)

    def spawn_enemy(self):
        """Spawn an enemy from the current wave."""
        if self.enemies_to_spawn <= 0:
            return

        # Get current wave config
        current_config = self.wave_history[-1] if self.wave_history else None
        if not current_config:
            return

        # Get enemy type for this spawn
        enemy_index = current_config["enemy_count"] - self.enemies_to_spawn
        enemy_type = current_config["enemy_types"][min(enemy_index, len(current_config["enemy_types"]) - 1)]

        print(f"Spawning enemy of type: {enemy_type}")

        # Generate formation if not already done
        if not hasattr(self, 'spawn_positions') or not self.spawn_positions:
            self._generate_formation(current_config["formation"], current_config["enemy_count"])

        # Get position from formation
        position = None
        if hasattr(self, 'spawn_positions') and self.spawn_positions:
            if enemy_index < len(self.spawn_positions):
                position = self.spawn_positions[enemy_index]
            else:
                # Fallback: generate a random position
                screen_width, screen_height = self.game_view.get_screen_dimensions() if hasattr(self.game_view, 'get_screen_dimensions') else (800, 600)
                position = (
                    random.randint(50, screen_width - 50),
                    random.randint(50, screen_height - 50)
                )
        else:
            # Fallback: generate a random position
            screen_width, screen_height = self.game_view.get_screen_dimensions() if hasattr(self.game_view, 'get_screen_dimensions') else (800, 600)
            position = (
                random.randint(50, screen_width - 50),
                random.randint(50, screen_height - 50)
            )

        # Get enemy modifiers
        speed = current_config.get("enemy_speed", 1.0)
        health = current_config.get("enemy_health", 1.0)

        # Spawn the enemy
        print(f"Calling on_spawn_enemy with: {enemy_type}, {position}")
        if self.on_spawn_enemy:
            self.on_spawn_enemy(
                enemy_type=enemy_type,
                position=position,
                speed=speed,
                health=health
            )

        # Decrement enemies to spawn
        self.enemies_to_spawn -= 1

    def _generate_formation(self, formation_type, enemy_count):
        """Generate spawn positions based on the formation type."""
        screen_width, screen_height = 800, 600  # Default values

        if hasattr(self.game_view, 'get_screen_dimensions'):
            screen_width, screen_height = self.game_view.get_screen_dimensions()

        self.spawn_positions = self.wave_generator.formation_generator.generate_formation(
            formation_type,
            enemy_count,
            screen_width,
            screen_height
        )

    def set_player_profile(self, profile):
        """Set the player profile for wave generation."""
        self.player_profile = profile

    def set_engagement_score(self, score):
        """Set the engagement score for wave generation."""
        self.engagement_score = score
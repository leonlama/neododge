import arcade
import random
from typing import Optional, List, Dict

class GameController:
    """Controller for managing game logic."""

    def __init__(self, game_view, screen_width, screen_height):
        """Initialize the game controller.

        Args:
            game_view: The game view that this controller is associated with.
            screen_width: Width of the game screen.
            screen_height: Height of the game screen.
        """
        self.game_view = game_view
        self.player = game_view.player
        self.screen_width = screen_width
        self.screen_height = screen_height

        # Initialize references to sprite lists from game_view
        self.enemies = getattr(game_view, 'enemies', arcade.SpriteList())
        self.orbs = getattr(game_view, 'orbs', arcade.SpriteList())
        self.coins = getattr(game_view, 'coins', arcade.SpriteList())
        self.artifacts = getattr(game_view, 'artifacts', arcade.SpriteList())

        # Initialize game state variables
        self.rest_period = False
        self.wave_timer = 0
        self.wave_duration = getattr(game_view, 'wave_duration', 20.0)
        self.shop_shown = False
        self.waves_completed = 0
        self.shop_frequency = 5  # Show shop every 5 waves

    def should_show_shop(self):
        """Determine if the shop should be shown.

        Returns:
            bool: True if the shop should be shown, False otherwise.
        """
        # Check if we've completed enough waves to show the shop
        wave_manager = getattr(self.game_view, 'wave_manager', None)
        current_wave = getattr(wave_manager, 'wave', 1) if wave_manager else 1

        # Show shop if:
        # 1. We've completed a wave (rest period is active)
        # 2. We haven't shown the shop yet for this wave
        # 3. The current wave is divisible by the shop frequency
        if (self.rest_period and 
            not self.shop_shown and 
            current_wave > 0 and 
            current_wave % self.shop_frequency == 0):
            self.shop_shown = True
            return True

        return False

    def reset_shop_flag(self):
        """Reset the shop shown flag."""
        self.shop_shown = False

    def get_wave_info(self):
        """Get information about the current wave.

        Returns:
            dict: A dictionary containing wave information.
        """
        wave_manager = getattr(self.game_view, 'wave_manager', None)
        current_wave = getattr(wave_manager, 'wave', 1) if wave_manager else 1

        # Calculate time remaining in wave
        time_elapsed = getattr(self.game_view, 'level_timer', 0)
        wave_duration = getattr(self.game_view, 'wave_duration', 20.0)
        time_remaining = max(0, wave_duration - (time_elapsed % wave_duration))

        # Get enemy count
        enemy_count = len(self.enemies) if self.enemies is not None else 0

        # Determine wave status
        if self.rest_period:
            status = "rest"
        else:
            status = "active"

        return {
            "wave": current_wave,
            "status": status,
            "time_remaining": time_remaining,
            "enemy_count": enemy_count,
            "rest_period": self.rest_period,
            "wave_timer": self.wave_timer
        }

    def update(self, delta_time):
        """Update game state.

        Args:
            delta_time: Time since last update.
        """
        # Update references to sprite lists (in case they've changed)
        self.enemies = getattr(self.game_view, 'enemies', arcade.SpriteList())
        self.orbs = getattr(self.game_view, 'orbs', arcade.SpriteList())
        self.coins = getattr(self.game_view, 'coins', arcade.SpriteList())
        self.artifacts = getattr(self.game_view, 'artifacts', arcade.SpriteList())

        # Update player
        if self.player:
            self.player.update()

        # Update enemies
        if self.enemies is not None:
            for enemy in self.enemies:
                try:
                    # Call update without delta_time
                    enemy.update()
                except Exception as e:
                    print(f"Error updating enemy: {e}")
                    # Basic fallback update
                    if hasattr(enemy, 'change_x'):
                        enemy.center_x += getattr(enemy, 'change_x', 0)
                    if hasattr(enemy, 'change_y'):
                        enemy.center_y += getattr(enemy, 'change_y', 0)

        # Update orbs
        if self.orbs is not None:
            for orb in self.orbs:
                if hasattr(orb, 'update'):
                    orb.update()  # Call the standard update method (no delta_time)
                    orb.update_with_time(delta_time)  # Call the time-based update method

        # Update coins
        if self.coins is not None:
            for coin in self.coins:
                if hasattr(coin, 'update'):
                    coin.update()

        # Update artifacts
        if self.artifacts is not None:
            for artifact in self.artifacts:
                if hasattr(artifact, 'update'):
                    artifact.update(delta_time)

        # Update dash artifact
        dash_artifact = getattr(self.game_view, 'dash_artifact', None)
        if dash_artifact:
            if hasattr(dash_artifact, 'update'):
                dash_artifact.update(delta_time)

        # Update wave manager
        wave_manager = getattr(self.game_view, 'wave_manager', None)
        if wave_manager and hasattr(wave_manager, 'update'):
            wave_manager.update(delta_time)

        # Check for collisions
        if hasattr(self.game_view, 'check_collisions'):
            self.game_view.check_collisions()

        # Update level timer
        if hasattr(self.game_view, 'level_timer'):
            self.game_view.level_timer += delta_time

        # Update wave message alpha
        if hasattr(self.game_view, 'wave_message_alpha'):
            if self.game_view.wave_message_alpha > 0:
                self.game_view.wave_message_alpha -= delta_time
                if self.game_view.wave_message_alpha < 0:
                    self.game_view.wave_message_alpha = 0

        # Handle coin spawning
        if hasattr(self.game_view, 'coins_to_spawn') and self.game_view.coins_to_spawn > 0:
            if hasattr(self.game_view, 'coin_spawn_timer'):
                self.game_view.coin_spawn_timer -= delta_time
                if self.game_view.coin_spawn_timer <= 0:
                    # Spawn a coin at a random position
                    x = random.randint(50, self.screen_width - 50)
                    y = random.randint(50, self.screen_height - 50)

                    # Create the coin
                    try:
                        from src.mechanics.coins.coin import Coin
                        coin = Coin(x, y)

                        # Only add to game_view.coins to avoid duplication
                        if hasattr(self.game_view, 'coins'):
                            self.game_view.coins.append(coin)
                    except ImportError:
                        try:
                            from src.mechanics.coins.coin import Coin
                            coin = Coin(x, y)

                            # Only add to game_view.coins to avoid duplication
                            if hasattr(self.game_view, 'coins'):
                                self.game_view.coins.append(coin)
                        except ImportError:
                            print("Error: Could not import Coin class")

                    # Update spawn counter and timer
                    self.game_view.coins_to_spawn -= 1
                    self.game_view.coin_spawn_timer = random.uniform(3, 7)
                    print(f"🪙 Spawned a coin! Remaining: {self.game_view.coins_to_spawn}")

        # Handle orb spawning
        if hasattr(self.game_view, 'orb_spawn_timer'):
            self.game_view.orb_spawn_timer -= delta_time
            if self.game_view.orb_spawn_timer <= 0:
                # Spawn an orb at a random position
                x = random.randint(50, self.screen_width - 50)
                y = random.randint(50, self.screen_height - 50)

                # Create a random orb
                try:
                    orb_type = random.choice(["buff", "debuff"])
                    if orb_type == "buff":
                        try:
                            from src.mechanics.orbs.buff_orbs import BuffOrb
                            orb = BuffOrb(x, y)
                        except ImportError:
                            from src.mechanics.orbs.buff_orbs import BuffOrb
                            orb = BuffOrb(x, y)
                    else:
                        try:
                            from src.mechanics.orbs.debuff_orbs import DebuffOrb
                            orb = DebuffOrb(x, y)
                        except ImportError:
                            from src.mechanics.orbs.debuff_orbs import DebuffOrb
                            orb = DebuffOrb(x, y)

                    # Only add to game_view.orbs to avoid duplication
                    if hasattr(self.game_view, 'orbs'):
                        self.game_view.orbs.append(orb)
                except ImportError:
                    print(f"Error: Could not import {orb_type.capitalize()}Orb class")

                # Reset timer
                self.game_view.orb_spawn_timer = random.uniform(4, 8)
                print(f"🔮 Spawned a {orb_type} orb!")

        # Handle artifact spawning
        if hasattr(self.game_view, 'artifact_spawn_timer'):
            self.game_view.artifact_spawn_timer -= delta_time
            if self.game_view.artifact_spawn_timer <= 0 and not getattr(self.game_view, 'dash_artifact', None):
                # Spawn an artifact at a random position
                x = random.randint(50, self.screen_width - 50)
                y = random.randint(50, self.screen_height - 50)

                # Create the artifact
                try:
                    try:
                        from src.mechanics.artifacts import DashArtifact
                        dash_artifact = DashArtifact(x, y)  # Only pass x and y
                    except ImportError:
                        from src.mechanics.artifacts import DashArtifact
                        dash_artifact = DashArtifact(x, y)  # Only pass x and y

                    self.game_view.dash_artifact = dash_artifact

                    # Add to artifacts list if it exists
                    if hasattr(self.game_view, 'artifacts'):
                        self.game_view.artifacts.append(dash_artifact)
                except ImportError:
                    print("Error: Could not import DashArtifact class")
                except Exception as e:
                    print(f"Error creating DashArtifact: {e}")

                # Reset timer
                self.game_view.artifact_spawn_timer = random.uniform(20, 30)
                print("✨ Spawned a dash artifact!")

        # Handle wave completion
        if self.enemies is not None and len(self.enemies) == 0 and not self.rest_period:
            # Wave completed
            self.rest_period = True
            self.wave_timer = 0

            # Update wave message
            if hasattr(self.game_view, 'wave_message'):
                self.game_view.wave_message = f"Wave {getattr(wave_manager, 'wave', 1)} completed!"
            if hasattr(self.game_view, 'wave_message_alpha'):
                self.game_view.wave_message_alpha = 1.0

            # Increment wave
            if wave_manager and hasattr(wave_manager, 'next_wave'):
                wave_manager.next_wave()

        # Handle rest period
        if self.rest_period:
            self.wave_timer += delta_time
            if self.wave_timer >= 3.0:  # 3 seconds rest between waves
                self.rest_period = False

                # Spawn new wave
                if wave_manager and hasattr(wave_manager, 'spawn_enemies'):
                    wave_manager.spawn_enemies(self.enemies, self.screen_width, self.screen_height)

                # Update wave message
                if hasattr(self.game_view, 'wave_message'):
                    self.game_view.wave_message = f"Wave {getattr(wave_manager, 'wave', 1)} started!"
                if hasattr(self.game_view, 'wave_message_alpha'):
                    self.game_view.wave_message_alpha = 1.0
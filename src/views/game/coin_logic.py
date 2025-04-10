import random
import arcade
from src.mechanics.coins.coin import Coin

def spawn_coin(game_view, x=None, y=None, min_distance_from_player=100):
        """
        Spawn a coin at the specified position or a random position.

        Args:
            game_view: The game view instance
            x (float, optional): X-coordinate for the coin. If None, a random position is chosen.
            y (float, optional): Y-coordinate for the coin. If None, a random position is chosen.
            min_distance_from_player (float): Minimum distance from player to spawn the coin.

        Returns:
            bool: True if coin was spawned successfully, False otherwise.
        """
        # If no position specified, choose a random position
        if x is None or y is None:
            margin = 50
            max_attempts = 10  # Limit attempts to find valid position

            for _ in range(max_attempts):
                # Generate random position
                x = random.randint(margin, game_view.window.width - margin)
                y = random.randint(margin, game_view.window.height - margin)

                # Check distance from player
                if hasattr(game_view, 'player'):
                    player_pos = (game_view.player.center_x, game_view.player.center_y)
                    coin_pos = (x, y)
                    distance = ((player_pos[0] - coin_pos[0])**2 + (player_pos[1] - coin_pos[1])**2)**0.5

                    # If too close to player, try again
                    if distance < min_distance_from_player:
                        continue

                # Valid position found
                break

        try:
            # Create the coin sprite
            coin = Coin(x, y)

            # Add to sprite lists
            if not hasattr(game_view, 'coins'):
                game_view.coins = arcade.SpriteList()

            game_view.coins.append(coin)

            # Add to all_sprites if it exists
            if hasattr(game_view, 'all_sprites'):
                game_view.all_sprites.append(coin)

            # Get remaining coins count (without relying on wave_manager.current_config)
            remaining = 0
            if hasattr(game_view, 'wave_manager') and hasattr(game_view.wave_manager, 'current_config'):
                total_coins = game_view.wave_manager.current_config.get('coin_count', 0)
                remaining = total_coins - len(game_view.coins)

            print(f"🪙 Spawned a coin at ({x}, {y})!")
            return True

        except Exception as e:
            print(f"Error spawning coin: {e}")
            return False
        
def spawn_coins(game_view, count):
        """
        Spawn a number of coins over time.

        Args:
            game_view: The game view instance
            count (int): Total number of coins to spawn for this wave
        """
        # Store the count for gradual spawning
        game_view.coins_to_spawn = count

        # Set initial spawn timer
        game_view.coin_spawn_timer = 2.0  # Wait 2 seconds before first spawn

        # Spawn a few coins immediately (max 3)
        initial_spawn_count = min(3, count)
        for _ in range(initial_spawn_count):
            spawn_coin(game_view)
            game_view.coins_to_spawn -= 1  # Reduce the count

        print(f"🪙 Scheduled {game_view.coins_to_spawn} more coins to spawn gradually")

def maybe_spawn_more_coins(game_view):
        """Spawn more coins if needed based on wave configuration."""
        if not hasattr(game_view, 'wave_manager') or not hasattr(game_view, 'coins'):
            return

        # Get current wave config
        current_config = getattr(game_view.wave_manager, 'current_config', None)
        if not current_config:
            return

        # Check if we need to spawn more coins
        target_coin_count = current_config.get('coin_count', 0)
        current_coin_count = len(game_view.coins)

        # Spawn more coins if we're below target and at a random chance
        if current_coin_count < target_coin_count and random.random() < 0.01:  # 1% chance per frame
            spawn_coin(game_view)

def check_coin_collection(game_view):
        """Check if player has collected any coins."""
        if not hasattr(game_view, 'coins') or not game_view.player:
            return

        # Get collisions
        coin_hit_list = arcade.check_for_collision_with_list(game_view.player, game_view.coins)

        # Handle each collision
        for coin in coin_hit_list:
            # Add to score
            coin_value = getattr(coin, 'coin_value', 1)
            game_view.score += coin_value

            # Play sound
            game_view.play_coin_sound()

            # Show message
            if hasattr(game_view, 'add_pickup_text'):
                game_view.add_pickup_text(f"Coin Collected!", coin.center_x, coin.center_y)

            # Remove the coin
            coin.remove_from_sprite_lists()

            # Update analytics
            if hasattr(game_view, 'wave_manager') and hasattr(game_view.wave_manager, 'wave_analytics'):
                game_view.wave_manager.wave_analytics.update_wave_stat(game_view.wave_manager.current_wave, "coins_collected", 1)

def spawn_wave_reward(game_view, wave_number):
        """
        Spawn a reward for completing a wave.

        Args:
            game_view: The game view instance
            wave_number (int): The completed wave number
        """
        # Spawn coins as a reward
        reward_coins = wave_number * 2  # 2 coins per wave number
        for _ in range(reward_coins):
            x = game_view.player.center_x + random.uniform(-100, 100)
            y = game_view.player.center_y + random.uniform(-100, 100)
            spawn_coin(game_view, x, y)

        # Maybe spawn an artifact
        if random.random() < 0.3:  # 30% chance
            game_view.spawn_artifact()

        # Show a message
       # game_view.show_message(f"Wave {wave_number} Complete!")

        print(f"🎁 Spawned wave completion reward: {reward_coins} coins")

def update_coins(game_view, delta_time):
    if not hasattr(game_view, 'coins'):
        return

    game_view.coins.update()
    for coin in game_view.coins:
        # Restore animation handling
        if hasattr(coin, 'update_animation'):
            coin.update_animation(delta_time)
        if hasattr(coin, 'update_with_time'):
            coin.update_with_time(delta_time)
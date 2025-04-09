import pytest
from unittest.mock import MagicMock, patch
import arcade
from src.views.game_view import NeododgeGame as GameView
from src.mechanics.wave_management.wave_manager import WaveManager
from src.mechanics.wave_management.wave_generator import WaveGenerator

def test_wave_management_integration():
    """Test the integration of wave management components."""
    # Create game view
    game_view = GameView()

    # Mock necessary attributes
    game_view.enemies = arcade.SpriteList()
    game_view.all_sprites = arcade.SpriteList()
    game_view.player = MagicMock()

    # Mock enemy class
    with patch('src.entities.enemies.enemy.Enemy') as MockEnemy:
        # Create mock enemy instance
        mock_enemy = MagicMock()
        MockEnemy.return_value = mock_enemy

        # Set up wave manager
        wave_manager = WaveManager()
        wave_manager.game_view = game_view
        wave_manager.on_spawn_enemy = game_view.spawn_enemy
        wave_manager.on_clear_enemies = game_view.clear_enemies

        # Start a wave
        wave_manager.start_wave()

        # Update with enough time to spawn an enemy
        wave_manager.update(wave_manager.spawn_delay + 0.1)

        # Check that an enemy was spawned
        assert len(game_view.enemies) == 1

        # Check that the enemy was set up correctly
        assert game_view.enemies[0] == mock_enemy
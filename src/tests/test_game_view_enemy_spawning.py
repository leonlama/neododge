import pytest
from unittest.mock import MagicMock, patch
import arcade
from src.views.game_view import NeododgeGame as GameView

def test_game_view_spawn_enemy():
    """Test that the game view spawns enemies correctly."""
    # Create game view
    game_view = GameView()

    # Mock necessary attributes
    game_view.enemies = arcade.SpriteList()
    game_view.all_sprites = arcade.SpriteList()

    # Mock enemy class
    with patch('src.entities.enemies.enemy.Enemy') as MockEnemy:
        # Create mock enemy instance
        mock_enemy = MagicMock()
        MockEnemy.return_value = mock_enemy

        # Call spawn_enemy
        game_view.spawn_enemy("basic", (100, 200), 1.5, 2.0)

        # Check that Enemy was called with correct parameters
        MockEnemy.assert_called_once_with(100, 200)

        # Check that enemy was added to sprite lists
        assert len(game_view.enemies) == 1
        assert game_view.enemies[0] == mock_enemy

def test_game_view_setup_wave_manager():
    """Test that the game view sets up the wave manager correctly."""
    # Create game view
    game_view = GameView()

    # Mock necessary attributes
    game_view.enemies = arcade.SpriteList()
    game_view.all_sprites = arcade.SpriteList()

    # Mock WaveManager
    with patch('src.mechanics.wave_management.wave_manager.WaveManager') as MockWaveManager:
        # Create mock wave manager instance
        mock_wave_manager = MagicMock()
        MockWaveManager.return_value = mock_wave_manager

        # Call setup_wave_manager
        game_view.setup_wave_manager()

        # Check that WaveManager was called
        MockWaveManager.assert_called_once()

        # Check that wave manager was set up correctly
        assert game_view.wave_manager == mock_wave_manager
        assert mock_wave_manager.game_view == game_view

        # Check that start_wave was called
        mock_wave_manager.start_wave.assert_called_once()

def test_game_view_update_calls_wave_manager_update():
    """Test that the game view calls the wave manager's update method."""
    # Create game view
    game_view = GameView()

    # Mock necessary attributes
    game_view.enemies = arcade.SpriteList()
    game_view.all_sprites = arcade.SpriteList()
    game_view.player = MagicMock()

    # Create mock wave manager
    game_view.wave_manager = MagicMock()

    # Call update
    game_view.update(1/60)

    # Check that wave manager's update was called
    game_view.wave_manager.update.assert_called_once_with(1/60)
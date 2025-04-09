import pytest
from unittest.mock import MagicMock, patch
import arcade
from src.views.game_view import NeododgeGame as GameView

def ensure_window():
    """Ensure an arcade window exists for testing."""
    try:
        if not arcade.get_window():
            arcade.open_window(800, 600, "Test Window")
    except:
        arcade.open_window(800, 600, "Test Window")

def test_game_view_spawn_enemy():
    """Test that the game view spawns enemies correctly."""
    # Ensure window exists
    ensure_window()
    
    # Create game view
    game_view = GameView()

    # Mock necessary attributes
    game_view.enemies = arcade.SpriteList()
    game_view.all_sprites = arcade.SpriteList()

    # Mock all possible enemy types that might be used
    with patch('src.entities.enemies.chaser.Chaser') as MockChaser, \
         patch('src.entities.enemies.wanderer.Wanderer') as MockWanderer, \
         patch('src.entities.enemies.enemy.Enemy') as MockBasicEnemy:
        
        # Set up the mock for the enemy type we expect to be called
        mock_enemy = MagicMock()
        MockBasicEnemy.return_value = mock_enemy

        # Call spawn_enemy with "basic" type
        game_view.spawn_enemy("basic", (100, 200), 1.5, 2.0)

        # Check that the correct enemy class was called with correct parameters
        MockBasicEnemy.assert_called_once_with(100, 200)
        
        # Check that enemy was added to sprite lists
        assert len(game_view.enemies) == 1
        assert game_view.enemies[0] == mock_enemy

def test_game_view_setup_wave_manager():
    """Test that the game view sets up the wave manager correctly."""
    # Ensure window exists
    ensure_window()
    
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
    # Ensure window exists
    ensure_window()
    
    # Create game view
    game_view = GameView()

    # Mock necessary attributes and dependencies
    game_view.enemies = arcade.SpriteList()
    game_view.all_sprites = arcade.SpriteList()
    game_view.player = MagicMock()
    game_view.player.bullets = arcade.SpriteList()
    game_view.physics_engine = MagicMock()
    game_view.powerup_manager = MagicMock()
    game_view.score_manager = MagicMock()
    game_view.collision_handler = MagicMock()

    # Create mock wave manager with explicit update method
    mock_wave_manager = MagicMock()
    mock_wave_manager.update = MagicMock()
    game_view.wave_manager = mock_wave_manager

    # Call update
    game_view.update(1/60)

    # Check that wave manager's update was called
    game_view.wave_manager.update.assert_called_once_with(1/60)

# Close the test window when done
def teardown_module(module):
    """Close the arcade window after all tests in this module."""
    try:
        arcade.close_window()
    except:
        pass
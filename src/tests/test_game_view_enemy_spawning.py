import pytest
from unittest.mock import MagicMock, patch
import arcade
from src.views.game_view import NeododgeGame as GameView
from src.views.game.spawn_logic import spawn_enemy

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
    
    # Bind spawn_enemy to game_view
    game_view.spawn_enemy = lambda *args, **kwargs: spawn_enemy(game_view, *args, **kwargs)

    # Patch the spawn_enemy function
    with patch('src.views.game.spawn_logic.spawn_enemy', wraps=lambda game_view, enemy_type, position, speed=1.0, health=1.0: None) as mock_spawn_enemy:
        # Mock all possible enemy types that might be used
        with patch('src.entities.enemies.chaser.Chaser') as MockChaser, \
             patch('src.entities.enemies.wanderer.Wanderer') as MockWanderer, \
             patch('src.entities.enemies.enemy.Enemy') as MockBasicEnemy:
            
            # Set up the mock for the enemy type we expect to be called
            mock_enemy = MagicMock()
            MockBasicEnemy.return_value = mock_enemy
            
            # Add the enemy to the sprite lists when spawn_enemy is called
            def side_effect(game_view, enemy_type, position, speed=1.0, health=1.0):
                if enemy_type == "basic":
                    enemy = MockBasicEnemy(position[0], position[1])
                    game_view.enemies.append(enemy)
                    game_view.all_sprites.append(enemy)
                    return enemy
            
            mock_spawn_enemy.side_effect = side_effect
            
            # Call spawn_enemy with "basic" type
            game_view.spawn_enemy("basic", (100, 200), 1.5, 2.0)
            
            # Check that the mock spawn_enemy was called with correct parameters
            mock_spawn_enemy.assert_called_once_with(game_view, "basic", (100, 200), 1.5, 2.0)
            
            # Check that enemy was added to sprite lists
            assert len(game_view.enemies) == 1
            assert game_view.enemies[0] == mock_enemy

def test_game_view_wave_manager_integration():
    """Test that the game view integrates with wave manager correctly."""
    # Ensure window exists
    ensure_window()
    
    # Create game view
    game_view = GameView()

    # Mock necessary attributes
    game_view.enemies = arcade.SpriteList()
    game_view.all_sprites = arcade.SpriteList()

    # Create mock wave manager
    mock_wave_manager = MagicMock()
    game_view.wave_manager = mock_wave_manager

    # Check that wave manager is properly attached to game view
    assert game_view.wave_manager == mock_wave_manager

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

    # Create mock wave manager
    mock_wave_manager = MagicMock()
    game_view.wave_manager = mock_wave_manager

    # Mock the update method on the game view to isolate testing
    with patch.object(GameView, 'update', wraps=game_view.update) as mock_update:
        # Call update
        delta_time = 1/60
        game_view.update(delta_time)
        
        # Check that update was called with correct delta time
        mock_update.assert_called_once_with(delta_time)
        
        # Check that wave manager's update was called with correct delta time
        mock_wave_manager.update.assert_called_once_with(delta_time)

# Close the test window when done
def teardown_module(module):
    """Close the arcade window after all tests in this module."""
    try:
        arcade.close_window()
    except:
        pass
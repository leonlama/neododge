import pytest
from unittest.mock import MagicMock, patch
import arcade
from src.views.game_view import NeododgeGame as GameView
from src.mechanics.wave_management.wave_manager import WaveManager
from src.mechanics.wave_management.wave_generator import WaveGenerator
from src.entities.enemies.chaser import Chaser
from src.entities.enemies.wanderer import Wanderer

def ensure_window():
    """Ensure an arcade window exists for testing."""
    try:
        if not arcade.get_window():
            arcade.open_window(800, 600, "Test Window")
    except:
        arcade.open_window(800, 600, "Test Window")

def test_wave_management_integration():
    """Test the integration of wave management components."""
    # Ensure window exists
    ensure_window()
    
    # Create game view
    game_view = GameView()

    # Mock necessary attributes
    game_view.enemies = arcade.SpriteList()
    game_view.all_sprites = arcade.SpriteList()
    game_view.player = MagicMock()
    game_view.get_screen_dimensions = MagicMock(return_value=(800, 600))

    # Patch all possible enemy types
    with patch('src.entities.enemies.chaser.Chaser') as MockChaser, \
         patch('src.entities.enemies.wanderer.Wanderer') as MockWanderer:
        
        # Create mock enemy instances
        mock_chaser = MagicMock()
        mock_wanderer = MagicMock()
        MockChaser.return_value = mock_chaser
        MockWanderer.return_value = mock_wanderer

        # Set up wave manager with required arguments
        wave_generator = MagicMock()
        on_spawn_enemy = MagicMock()
        wave_manager = WaveManager(wave_generator, on_spawn_enemy)
        
        wave_manager.game_view = game_view
        wave_manager.on_spawn_enemy = game_view.spawn_enemy
        wave_manager.on_clear_enemies = game_view.clear_enemies

        # Start a wave
        wave_manager.start_wave()

        # Update with enough time to spawn an enemy
        wave_manager.update(wave_manager.spawn_delay + 0.1)

        # Check that an enemy was spawned
        assert len(game_view.enemies) == 1

        # Check that the enemy is one of our mocked types
        spawned_enemy = game_view.enemies[0]
        assert spawned_enemy in [mock_chaser, mock_wanderer], "Spawned enemy should be one of our mocked types"
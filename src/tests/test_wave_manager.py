import pytest
from unittest.mock import MagicMock
from src.mechanics.wave_management.wave_manager import WaveManager

class MockGameView:
    """Mock game view for testing."""
    def __init__(self):
        self.enemies_spawned = []
        self.enemies_cleared = False

    def spawn_enemy(self, enemy_type, position, speed=1.0, health=1.0):
        """Mock spawn_enemy method."""
        self.enemies_spawned.append({
            "type": enemy_type,
            "position": position,
            "speed": speed,
            "health": health
        })

    def clear_enemies(self):
        """Mock clear_enemies method."""
        self.enemies_cleared = True

    def get_screen_dimensions(self):
        """Mock get_screen_dimensions method."""
        return 800, 600

def test_wave_manager_initialization():
    """Test that the wave manager initializes correctly."""
    # Create mock game view
    game_view = MockGameView()
    
    # Create mock wave generator
    wave_generator = MagicMock()
    on_spawn_enemy = game_view.spawn_enemy
    
    # Create wave manager
    wave_manager = WaveManager(wave_generator, on_spawn_enemy)
    wave_manager.game_view = game_view

    # Check initial state
    assert wave_manager.current_wave == 0
    assert not wave_manager.in_wave
    assert wave_manager.enemies_to_spawn == 0

def test_wave_manager_start_wave():
    """Test that the wave manager starts a wave correctly."""
    # Create mock game view
    game_view = MockGameView()

    # Create mock wave generator
    wave_generator = MagicMock()
    on_spawn_enemy = game_view.spawn_enemy
    
    # Create wave manager
    wave_manager = WaveManager(wave_generator, on_spawn_enemy)
    wave_manager.game_view = game_view
    wave_manager.on_clear_enemies = game_view.clear_enemies
    
    # Mock wave generator to return a valid config
    wave_generator.generate_next_wave.return_value = {
        "wave_number": 1,
        "type": "normal",
        "duration": 30,
        "enemy_count": 5,
        "spawn_delay": 1.0,
        "enemy_speed": 1.0,
        "enemy_health": 1.0,
        "formation": "random",
        "orb_count": 2,
        "coin_count": 3
    }
    
    # Ensure wave_config is set before starting the wave
    wave_manager.current_config = wave_generator.generate_next_wave()

    # Start a wave
    wave_manager.start_wave()

    # Check state
    assert wave_manager.current_wave == 1
    assert wave_manager.in_wave
    assert wave_manager.enemies_to_spawn > 0
    assert isinstance(wave_manager.current_config, dict)

def test_wave_manager_spawn_enemy():
    """Test that the wave manager spawns enemies correctly."""
    # Create mock game view
    game_view = MockGameView()

    # Create mock wave generator
    wave_generator = MagicMock()
    on_spawn_enemy = game_view.spawn_enemy
    
    # Create wave manager
    wave_manager = WaveManager(wave_generator, on_spawn_enemy)
    wave_manager.game_view = game_view
    wave_manager.on_clear_enemies = game_view.clear_enemies
    
    # Mock wave generator to return a valid config
    wave_generator.generate_next_wave.return_value = {
        "wave_number": 1,
        "type": "normal",
        "duration": 30,
        "enemy_count": 5,
        "spawn_delay": 1.0,
        "enemy_speed": 1.0,
        "enemy_health": 1.0,
        "formation": "random",
        "orb_count": 2,
        "coin_count": 3
    }
    
    # Ensure wave_config is set before starting the wave
    wave_manager.current_config = wave_generator.generate_next_wave()

    # Start a wave
    wave_manager.start_wave()

    # Get initial enemy count
    initial_enemies_to_spawn = wave_manager.enemies_to_spawn

    # Spawn an enemy
    wave_manager.spawn_enemy()

    # Check that an enemy was spawned
    assert len(game_view.enemies_spawned) == 1
    assert wave_manager.enemies_to_spawn == initial_enemies_to_spawn - 1

    # Check enemy properties
    enemy = game_view.enemies_spawned[0]
    assert "type" in enemy
    assert "position" in enemy
    assert "speed" in enemy
    assert "health" in enemy

def test_wave_manager_update():
    """Test that the wave manager updates correctly."""
    # Create mock game view
    game_view = MockGameView()

    # Create mock wave generator
    wave_generator = MagicMock()
    on_spawn_enemy = game_view.spawn_enemy
    
    # Create wave manager
    wave_manager = WaveManager(wave_generator, on_spawn_enemy)
    wave_manager.game_view = game_view
    wave_manager.on_clear_enemies = game_view.clear_enemies
    
    # Mock wave generator to return a valid config
    wave_generator.generate_next_wave.return_value = {
        "wave_number": 1,
        "type": "normal",
        "duration": 30,
        "enemy_count": 5,
        "spawn_delay": 1.0,
        "enemy_speed": 1.0,
        "enemy_health": 1.0,
        "formation": "random",
        "orb_count": 2,
        "coin_count": 3
    }
    
    # Ensure wave_config is set before starting the wave
    wave_manager.current_config = wave_generator.generate_next_wave()

    # Start a wave
    wave_manager.start_wave()

    # Update with enough time to spawn an enemy
    wave_manager.update(wave_manager.spawn_delay + 0.1)

    # Check that an enemy was spawned
    assert len(game_view.enemies_spawned) == 1

    # Update with enough time to end the wave
    wave_manager.update(wave_manager.wave_duration)

    # Check that the wave ended
    assert not wave_manager.in_wave
    assert game_view.enemies_cleared
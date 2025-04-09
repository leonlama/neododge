import pytest
from unittest.mock import MagicMock
from src.mechanics.wave_management.wave_manager import WaveManager
from src.mechanics.wave_management.wave_generator import WaveGenerator

def test_debug_wave_manager():
    """Debug test to print the state of the wave manager."""
    # Create mock game view
    class MockGameView:
        def spawn_enemy(self, enemy_type, position, speed=1.0, health=1.0):
            print(f"Spawning enemy: {enemy_type} at {position} with speed={speed}, health={health}")

        def clear_enemies(self):
            print("Clearing enemies")

        def get_screen_dimensions(self):
            return 800, 600

    # Create mock wave generator
    wave_generator = MagicMock()
    mock_game_view = MockGameView()
    on_spawn_enemy = mock_game_view.spawn_enemy
    
    # Create wave manager with required parameters
    wave_manager = WaveManager(wave_generator, on_spawn_enemy)
    
    # Set up wave manager
    wave_manager.game_view = mock_game_view
    wave_manager.on_clear_enemies = mock_game_view.clear_enemies
    
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

    # Print initial state
    print("\nInitial state:")
    print(f"Wave number: {wave_manager.current_wave}")
    print(f"In wave: {wave_manager.in_wave}")
    print(f"Enemies to spawn: {wave_manager.enemies_to_spawn}")

    # Start a wave
    print("\nStarting wave...")
    wave_manager.start_wave()

    # Print wave state
    print("\nWave state:")
    print(f"Wave number: {wave_manager.current_wave}")
    print(f"In wave: {wave_manager.in_wave}")
    print(f"Enemies to spawn: {wave_manager.enemies_to_spawn}")
    print(f"Wave configuration: {wave_manager.current_config}")

    # Spawn enemies
    print("\nSpawning enemies...")
    for _ in range(wave_manager.enemies_to_spawn):
        wave_manager.spawn_enemy()

    # Print final state
    print("\nFinal state:")
    print(f"Wave number: {wave_manager.current_wave}")
    print(f"In wave: {wave_manager.in_wave}")
    print(f"Enemies to spawn: {wave_manager.enemies_to_spawn}")
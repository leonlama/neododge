import pytest
from src.mechanics.wave_management.wave_manager import WaveManager
from src.mechanics.wave_management.wave_generator import WaveGenerator

def test_debug_wave_manager():
    """Debug test to print the state of the wave manager."""
    # Create wave manager
    wave_manager = WaveManager()

    # Create mock game view
    class MockGameView:
        def spawn_enemy(self, enemy_type, position, speed=1.0, health=1.0):
            print(f"Spawning enemy: {enemy_type} at {position} with speed={speed}, health={health}")

        def clear_enemies(self):
            print("Clearing enemies")

        def get_screen_dimensions(self):
            return 800, 600

    # Set up wave manager
    wave_manager.game_view = MockGameView()
    wave_manager.on_spawn_enemy = wave_manager.game_view.spawn_enemy
    wave_manager.on_clear_enemies = wave_manager.game_view.clear_enemies

    # Print initial state
    print("\nInitial state:")
    print(f"Wave number: {wave_manager.wave_number}")
    print(f"In wave: {wave_manager.in_wave}")
    print(f"Enemies to spawn: {wave_manager.enemies_to_spawn}")

    # Start a wave
    print("\nStarting wave...")
    wave_manager.start_wave()

    # Print wave state
    print("\nWave state:")
    print(f"Wave number: {wave_manager.wave_number}")
    print(f"In wave: {wave_manager.in_wave}")
    print(f"Enemies to spawn: {wave_manager.enemies_to_spawn}")
    print(f"Wave configuration: {wave_manager.current_wave}")

    # Spawn enemies
    print("\nSpawning enemies...")
    for _ in range(wave_manager.enemies_to_spawn):
        wave_manager.spawn_enemy()

    # Print final state
    print("\nFinal state:")
    print(f"Wave number: {wave_manager.wave_number}")
    print(f"In wave: {wave_manager.in_wave}")
    print(f"Enemies to spawn: {wave_manager.enemies_to_spawn}")
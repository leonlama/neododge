import pytest
from src.mechanics.wave_management.wave_manager import WaveManager
from src.mechanics.wave_management.wave_generator import WaveGenerator
from src.mechanics.wave_management.difficulty_adjuster import DifficultyAdjuster

class TestWaveManager:
    def test_wave_progression(self):
        """Test that waves progress correctly."""
        manager = WaveManager()

        # Test initial state
        assert manager.wave_number == 0
        assert not manager.in_wave

        # Test starting a wave
        manager.start_wave()
        assert manager.wave_number == 1
        assert manager.in_wave

        # Test ending a wave
        manager.end_wave()
        assert not manager.in_wave

        # Test starting another wave
        manager.start_wave()
        assert manager.wave_number == 2

    def test_enemy_spawning(self):
        """Test that enemies spawn correctly."""
        manager = WaveManager()

        # Mock spawn_enemy callback
        spawned_enemies = []
        manager.on_spawn_enemy = lambda enemy_type, position, speed, health: spawned_enemies.append(enemy_type)

        # Start wave and manually trigger spawns
        manager.start_wave()
        initial_count = manager.enemies_to_spawn

        for _ in range(initial_count):
            manager.spawn_enemy()

        assert manager.enemies_to_spawn == 0
        assert len(spawned_enemies) == initial_count
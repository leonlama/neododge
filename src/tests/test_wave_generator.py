import pytest
from src.mechanics.wave_management.wave_generator import WaveGenerator

def test_wave_generator_creates_valid_wave():
    """Test that the wave generator creates a valid wave configuration."""
    # Create wave generator
    wave_generator = WaveGenerator()

    # Generate a wave
    wave = wave_generator.create_wave(1)

    # Check wave structure
    assert isinstance(wave, dict)
    assert "type" in wave
    assert "wave_number" in wave
    assert "enemy_count" in wave
    assert "enemy_types" in wave
    assert "spawn_delay" in wave
    assert "duration" in wave

    # Check enemy types
    assert isinstance(wave["enemy_types"], list)
    assert len(wave["enemy_types"]) == wave["enemy_count"]

    # Check that all enemy types are valid
    valid_types = ["basic", "wander", "chaser", "shooter"]
    for enemy_type in wave["enemy_types"]:
        assert enemy_type in valid_types

def test_wave_generator_creates_different_waves():
    """Test that the wave generator creates different waves for different wave numbers."""
    # Create wave generator
    wave_generator = WaveGenerator()

    # Generate two waves
    wave1 = wave_generator.create_wave(1)
    wave2 = wave_generator.create_wave(5)

    # Check that they're different
    assert wave1["wave_number"] != wave2["wave_number"]
    assert wave1["enemy_count"] != wave2["enemy_count"] or wave1["enemy_types"] != wave2["enemy_types"]

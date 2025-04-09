import pytest
from src.mechanics.wave_management.wave_generator import WaveGenerator

def generate_mock_profile(aggression=0.5, risk=0.5, skill=0.5):
    """Generate a mock player profile with customizable parameters."""
    return {
        "playstyle": {
            "aggression": aggression,
            "risk": risk
        },
        "skill_level": skill
    }

def test_wave_generator_creates_normal_wave():
    wave_generator = WaveGenerator()
    
    # Mock player profile and engagement score
    player_profile = generate_mock_profile()
    engagement_score = 0.5
    
    # Test normal wave (wave 1)
    wave = wave_generator.create_wave(1, player_profile, engagement_score)
    
    # Verify structure
    assert wave["type"] == "normal"
    assert "enemy_count" in wave  # Changed from "enemies"
    assert wave["enemy_count"] > 0
    assert "enemy_speed" in wave
    assert "enemy_types" in wave

def test_wave_generator_creates_rest_wave():
    wave_generator = WaveGenerator()
    
    # Rest waves occur every 6 waves
    player_profile = generate_mock_profile(aggression=0.3, risk=0.7)
    engagement_score = 0.5
    
    wave = wave_generator.create_wave(6, player_profile, engagement_score)
    
    assert wave["type"] == "rest"
    assert wave["enemy_count"] == 2
    assert wave["enemy_types"] == ["wander", "wander"]
    assert "enemy_speed" in wave
    assert "spawn_delay" in wave
    assert "duration" in wave
    assert "message" in wave

def test_wave_generator_creates_boss_wave():
    wave_generator = WaveGenerator()
    
    # Boss waves occur every 10 waves
    player_profile = generate_mock_profile(aggression=0.9, skill=0.3)
    engagement_score = 0.5
    
    wave = wave_generator.create_wave(10, player_profile, engagement_score)
    
    assert wave["type"] == "boss"
    assert wave["enemy_count"] == 1
    assert wave["enemy_types"] == ["boss"]
    assert "enemy_speed" in wave
    assert "spawn_delay" in wave
    assert "duration" in wave
    assert "message" in wave

def test_wave_generator_creates_swarm_wave():
    wave_generator = WaveGenerator()
    
    # Swarm waves occur every 7 waves
    player_profile = generate_mock_profile(risk=0.8, skill=0.7)
    engagement_score = 0.5
    
    wave = wave_generator.create_wave(7, player_profile, engagement_score)
    
    assert wave["type"] == "swarm"
    assert wave["enemy_count"] > 0
    assert "enemy_types" in wave
    assert "enemy_speed" in wave
    assert "spawn_delay" in wave
    assert "duration" in wave
    assert "message" in wave

def test_weighted_choice():
    wave_generator = WaveGenerator()
    
    # Test with equal weights
    weights = {"a": 0.5, "b": 0.5}
    results = {}
    
    # Run multiple times to account for randomness
    for _ in range(1000):
        choice = wave_generator._weighted_choice(weights)
        results[choice] = results.get(choice, 0) + 1
    
    # Both should be roughly equal (allowing for some variance)
    assert 400 < results.get("a", 0) < 600
    assert 400 < results.get("b", 0) < 600
    
    # Test with unequal weights
    weights = {"a": 0.8, "b": 0.2}
    results = {}
    
    for _ in range(1000):
        choice = wave_generator._weighted_choice(weights)
        results[choice] = results.get(choice, 0) + 1
    
    # "a" should be chosen roughly 4 times as often as "b"
    assert 700 < results.get("a", 0) < 900
    assert 100 < results.get("b", 0) < 300

def test_calculate_coins():
    wave_generator = WaveGenerator()
    
    # Test with different wave numbers and difficulties
    coins_wave1 = wave_generator._calculate_coins(1, 0.5)
    assert 3 <= coins_wave1 <= 5  # Base 3 + difficulty bonus (0.5 * 5 = 2.5 -> 2)
    
    coins_wave10 = wave_generator._calculate_coins(10, 1.0)
    assert 6 <= coins_wave10 <= 11  # Base 3 + (10 // 3 = 3) + difficulty bonus (1.0 * 5 = 5)
    
    # Higher difficulty should give more coins on average
    total_low_diff = sum(wave_generator._calculate_coins(5, 0.2) for _ in range(100))
    total_high_diff = sum(wave_generator._calculate_coins(5, 0.8) for _ in range(100))
    assert total_low_diff < total_high_diff

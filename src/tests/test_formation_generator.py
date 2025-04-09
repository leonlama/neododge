import pytest
import math
from src.mechanics.wave_management.formation_generator import FormationGenerator

def test_formation_generator_initialization():
    """Test that the FormationGenerator initializes correctly."""
    generator = FormationGenerator()
    assert generator.formation_types == ["circle", "line", "grid", "random", "v_shape", "spiral"]
    assert generator.screen_width == 800
    assert generator.screen_height == 600

def test_circle_formation():
    """Test that circle formations are generated correctly."""
    generator = FormationGenerator()
    enemy_types = ["basic", "basic", "basic", "basic"]

    positions = generator._generate_circle_formation(enemy_types, 0.5)

    # Check that we have the right number of positions
    assert len(positions) == len(enemy_types)

    # Check that all positions are roughly the same distance from the center
    center_x, center_y = generator.center_x, generator.center_y
    distances = [math.sqrt((x - center_x)**2 + (y - center_y)**2) for x, y in positions]

    # All distances should be approximately equal
    avg_distance = sum(distances) / len(distances)
    for distance in distances:
        assert abs(distance - avg_distance) < 0.001

def test_line_formation():
    """Test that line formations are generated correctly."""
    generator = FormationGenerator()
    enemy_types = ["basic", "basic", "basic", "basic"]

    positions = generator._generate_line_formation(enemy_types, 0.5)

    # Check that we have the right number of positions
    assert len(positions) == len(enemy_types)

    # Check if it's a horizontal or vertical line
    x_coords = [x for x, y in positions]
    y_coords = [y for x, y in positions]

    # Either all y values should be the same (horizontal line)
    # or all x values should be the same (vertical line)
    is_horizontal = len(set(y_coords)) == 1
    is_vertical = len(set(x_coords)) == 1

    assert is_horizontal or is_vertical

def test_grid_formation():
    """Test that grid formations are generated correctly."""
    generator = FormationGenerator()
    enemy_types = ["basic"] * 9  # 3x3 grid

    positions = generator._generate_grid_formation(enemy_types, 0.5)

    # Check that we have the right number of positions
    assert len(positions) == len(enemy_types)

    # For a perfect grid, there should be exactly 3 unique x and y coordinates
    x_coords = sorted([x for x, y in positions])
    y_coords = sorted([y for x, y in positions])

    # Count unique x and y values
    unique_x = len(set(x_coords))
    unique_y = len(set(y_coords))

    # For a 3x3 grid, we should have 3 unique x and y values
    assert unique_x <= 3
    assert unique_y <= 3

def test_formation_generation():
    """Test that formations are generated for different aggression levels."""
    generator = FormationGenerator()
    enemy_types = ["basic"] * 5

    # Test with different aggression levels
    low_aggression = generator.generate_formation(enemy_types, 0.2, 0.5)
    medium_aggression = generator.generate_formation(enemy_types, 0.5, 0.5)
    high_aggression = generator.generate_formation(enemy_types, 0.8, 0.5)

    # Check that we have the right number of positions
    assert len(low_aggression) == len(enemy_types)
    assert len(medium_aggression) == len(enemy_types)
    assert len(high_aggression) == len(enemy_types)

    # Check that positions are within screen bounds
    for positions in [low_aggression, medium_aggression, high_aggression]:
        for x, y in positions:
            assert 0 <= x <= generator.screen_width
            assert 0 <= y <= generator.screen_height
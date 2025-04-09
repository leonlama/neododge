import pytest
import math
from src.mechanics.wave_management.formation_generator import FormationGenerator

def test_formation_generator_initialization():
    """Test that the FormationGenerator initializes correctly."""
    generator = FormationGenerator()
    expected_formations = ["circle", "line", "grid", "random", "v_shape", "spiral"]
    # Check that all expected formation types are in the keys
    for formation in expected_formations:
        assert formation in generator.formation_types

def test_circle_formation():
    """Test that circle formations are generated correctly."""
    generator = FormationGenerator()
    enemy_types = ["basic", "basic", "basic", "basic"]
    screen_width = 800
    screen_height = 600

    positions = generator._generate_circle_formation(enemy_types, screen_width, screen_height)

    # Check that we have the right number of positions
    assert len(positions) == len(enemy_types)

    # Check that positions form a circle
    center_x, center_y = screen_width / 2, screen_height / 2
    radius = min(screen_width, screen_height) / 3

    for i, (x, y, enemy_type) in enumerate(positions):
        # Calculate expected position
        angle = 2 * math.pi * i / len(enemy_types)
        expected_x = center_x + radius * math.cos(angle)
        expected_y = center_y + radius * math.sin(angle)

        # Check position with some tolerance
        assert abs(x - expected_x) < 0.001
        assert abs(y - expected_y) < 0.001
        assert enemy_type == "basic"

def test_line_formation():
    """Test that line formations are generated correctly."""
    generator = FormationGenerator()
    enemy_types = ["basic", "basic", "basic", "basic"]
    screen_width = 800
    screen_height = 600

    positions = generator._generate_line_formation(enemy_types, screen_width, screen_height)

    # Check that we have the right number of positions
    assert len(positions) == len(enemy_types)

    # Check that y-coordinates are the same (horizontal line)
    y_values = [pos[1] for pos in positions]
    assert all(y == y_values[0] for y in y_values)

    # Check that x-coordinates are evenly spaced
    x_values = [pos[0] for pos in positions]
    for i in range(1, len(x_values)):
        assert abs((x_values[i] - x_values[i-1]) - (x_values[1] - x_values[0])) < 0.001

def test_grid_formation():
    """Test that grid formations are generated correctly."""
    generator = FormationGenerator()
    enemy_types = ["basic"] * 9  # 3x3 grid
    screen_width = 800
    screen_height = 600

    positions = generator._generate_grid_formation(enemy_types, screen_width, screen_height)

    # Check that we have the right number of positions
    assert len(positions) == len(enemy_types)

    # Extract x and y coordinates
    x_coords = [pos[0] for pos in positions]
    y_coords = [pos[1] for pos in positions]

    # Count unique x and y coordinates (should be 3 each for a 3x3 grid)
    unique_x = len(set([round(x, 2) for x in x_coords]))
    unique_y = len(set([round(y, 2) for y in y_coords]))

    # For a perfect 3x3 grid, we should have 3 unique x and y values
    assert unique_x <= 3
    assert unique_y <= 3

def test_formation_generation():
    """Test that formations are generated for different aggression levels."""
    generator = FormationGenerator()
    enemy_types = ["basic"] * 5
    screen_width = 800
    screen_height = 600

    # Test with different aggression levels
    low_aggression = generator.generate_formation(enemy_types, 0.2, screen_width, screen_height)
    high_aggression = generator.generate_formation(enemy_types, 0.8, screen_width, screen_height)

    # Check that we have the right number of positions
    assert len(low_aggression) == len(enemy_types)
    assert len(high_aggression) == len(enemy_types)
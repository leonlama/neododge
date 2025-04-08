import random
import math

class FormationGenerator:
    """Generates enemy formations for waves."""

    def __init__(self):
        self.formation_types = ["circle", "line", "grid", "random"]

    def generate_formation(self, enemy_types, player_style, difficulty):
        """Generate positions for enemies based on formation type."""
        formation_type = random.choice(self.formation_types)

        if formation_type == "circle":
            return self._generate_circle_formation(enemy_types)
        elif formation_type == "line":
            return self._generate_line_formation(enemy_types)
        elif formation_type == "grid":
            return self._generate_grid_formation(enemy_types)
        else:  # random formation
            return self._generate_random_formation(enemy_types)

    def _generate_circle_formation(self, enemy_types):
        """Generate a circle formation around the center of the screen"""
        positions = []
        center_x, center_y = 400, 300  # Assuming screen center
        radius = 200  # Fixed radius for simplicity
        count = len(enemy_types)

        for i in range(count):
            angle = (i / count) * 2 * math.pi
            x = center_x + radius * math.cos(angle)
            y = center_y + radius * math.sin(angle)
            positions.append((x, y))

        return positions

    def _generate_line_formation(self, enemy_types):
        """Generate a horizontal line formation"""
        positions = []
        count = len(enemy_types)
        
        # Horizontal line
        y = 150  # Fixed y position
        spacing = 700 / (count + 1)
        for i in range(count):
            x = 50 + spacing * (i + 1)
            positions.append((x, y))

        return positions

    def _generate_grid_formation(self, enemy_types):
        """Generate a grid formation"""
        positions = []
        count = len(enemy_types)

        # Calculate grid dimensions
        grid_size = math.ceil(math.sqrt(count))
        spacing = 80  # Fixed spacing

        start_x = 400 - (grid_size * spacing / 2)
        start_y = 300 - (grid_size * spacing / 2)

        for i in range(count):
            row = i // grid_size
            col = i % grid_size
            x = start_x + (col * spacing)
            y = start_y + (row * spacing)
            positions.append((x, y))

        return positions

    def _generate_random_formation(self, enemy_types):
        """Generate random positions within screen bounds"""
        positions = []
        count = len(enemy_types)

        for _ in range(count):
            x = random.randint(100, 700)
            y = random.randint(100, 500)
            positions.append((x, y))

        return positions
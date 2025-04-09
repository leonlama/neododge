import random
import math

class FormationGenerator:
    """Generates enemy formations for different wave types."""

    def __init__(self):
        self.formation_types = {
            "circle": self._generate_circle_formation,
            "line": self._generate_line_formation,
            "random": self._generate_random_formation,
            "grid": self._generate_grid_formation,
            "v_shape": self._generate_v_formation,
            "spiral": self._generate_spiral_formation
        }

    def generate_formation(self, enemy_types, aggression, screen_width, screen_height):
        """Generate positions for enemies in a specific formation based on aggression level."""
        # Choose formation type based on aggression
        if aggression < 0.3:
            # Less aggressive formations for low aggression
            formation_type = random.choice(["circle", "grid", "random"])
        elif aggression < 0.7:
            # Balanced formations for medium aggression
            formation_type = random.choice(["line", "v_shape", "random"])
        else:
            # More aggressive formations for high aggression
            formation_type = random.choice(["spiral", "v_shape", "line"])

        if formation_type in self.formation_types:
            return self.formation_types[formation_type](enemy_types, screen_width, screen_height)
        return self._generate_random_formation(enemy_types, screen_width, screen_height)

    def _generate_circle_formation(self, enemy_types, screen_width, screen_height):
        """Generate enemies in a circle formation."""
        positions = []
        center_x, center_y = screen_width / 2, screen_height / 2
        radius = min(screen_width, screen_height) / 3

        for i in range(len(enemy_types)):
            angle = 2 * math.pi * i / len(enemy_types)
            x = center_x + radius * math.cos(angle)
            y = center_y + radius * math.sin(angle)
            positions.append((x, y, enemy_types[i]))

        return positions

    def _generate_line_formation(self, enemy_types, screen_width, screen_height):
        """Generate enemies in a horizontal line formation."""
        positions = []

        # Determine line length based on number of enemies
        line_length = min(screen_width * 0.8, len(enemy_types) * 60)
        start_x = (screen_width - line_length) / 2
        y = screen_height * 0.8  # Position near top of screen

        for i in range(len(enemy_types)):
            x = start_x + (line_length * i / (len(enemy_types) - 1 or 1))
            positions.append((x, y, enemy_types[i]))

        return positions

    def _generate_grid_formation(self, enemy_types, screen_width, screen_height):
        """Generate enemies in a grid formation."""
        positions = []

        # Calculate grid dimensions
        enemy_count = len(enemy_types)
        cols = int(math.sqrt(enemy_count))
        rows = (enemy_count + cols - 1) // cols  # Ceiling division

        # Calculate spacing
        grid_width = min(screen_width * 0.8, cols * 60)
        grid_height = min(screen_height * 0.5, rows * 60)

        start_x = (screen_width - grid_width) / 2
        start_y = (screen_height - grid_height) / 2

        for i in range(enemy_count):
            row = i // cols
            col = i % cols

            x = start_x + (grid_width * col / (cols - 1 or 1))
            y = start_y + (grid_height * row / (rows - 1 or 1))

            positions.append((x, y, enemy_types[i]))

        return positions

    def _generate_random_formation(self, enemy_types, screen_width, screen_height):
        """Generate enemies in random positions."""
        positions = []
        margin = 50  # Keep enemies away from screen edges

        for enemy_type in enemy_types:
            x = random.uniform(margin, screen_width - margin)
            y = random.uniform(margin, screen_height - margin)
            positions.append((x, y, enemy_type))

        return positions

    def _generate_v_formation(self, enemy_types, screen_width, screen_height):
        """Generate enemies in a V formation."""
        positions = []

        center_x = screen_width / 2
        top_y = screen_height * 0.8

        enemy_count = len(enemy_types)
        half_count = enemy_count // 2

        # Calculate V width based on enemy count
        v_width = min(screen_width * 0.7, enemy_count * 40)

        for i in range(enemy_count):
            if i < half_count:
                # Left side of V
                ratio = i / (half_count - 1 or 1)
                x = center_x - (v_width / 2) * ratio
                y = top_y - (top_y * 0.3) * ratio
            else:
                # Right side of V
                ratio = (i - half_count) / (enemy_count - half_count - 1 or 1)
                x = center_x + (v_width / 2) * ratio
                y = top_y - (top_y * 0.3) * ratio

            positions.append((x, y, enemy_types[i]))

        return positions

    def _generate_spiral_formation(self, enemy_types, screen_width, screen_height):
        """Generate enemies in a spiral formation."""
        positions = []

        center_x = screen_width / 2
        center_y = screen_height / 2

        # Spiral parameters
        max_radius = min(screen_width, screen_height) * 0.4
        revolutions = 1.5

        for i in range(len(enemy_types)):
            # Calculate angle and radius for spiral
            angle = revolutions * 2 * math.pi * i / len(enemy_types)
            radius = max_radius * i / len(enemy_types)

            x = center_x + radius * math.cos(angle)
            y = center_y + radius * math.sin(angle)

            positions.append((x, y, enemy_types[i]))

        return positions
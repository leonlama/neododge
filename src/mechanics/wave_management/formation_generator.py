import random
import math

class FormationGenerator:
    """Generates enemy formations for waves."""

    def __init__(self):
        self.formation_types = ["circle", "line", "grid", "random", "v_shape", "spiral"]
        self.screen_width = 800
        self.screen_height = 600
        self.center_x = self.screen_width / 2
        self.center_y = self.screen_height / 2

    def generate_formation(self, enemy_types, aggression, difficulty):
        """Generate positions for enemies based on formation type."""
        # Choose formation type based on aggression and difficulty
        if random.random() < 0.7:
            # Most of the time, choose randomly from all formations
            formation_type = random.choice(self.formation_types)
        else:
            # Sometimes bias toward more aggressive formations for high aggression
            if aggression > 0.7:
                formation_type = random.choice(["v_shape", "spiral", "circle"])
            elif aggression < 0.3:
                formation_type = random.choice(["line", "grid", "random"])
            else:
                formation_type = random.choice(self.formation_types)

        # Generate positions based on formation type
        if formation_type == "circle":
            return self._generate_circle_formation(enemy_types, difficulty)
        elif formation_type == "line":
            return self._generate_line_formation(enemy_types, difficulty)
        elif formation_type == "grid":
            return self._generate_grid_formation(enemy_types, difficulty)
        elif formation_type == "v_shape":
            return self._generate_v_shape_formation(enemy_types, difficulty)
        elif formation_type == "spiral":
            return self._generate_spiral_formation(enemy_types, difficulty)
        else:  # random formation
            return self._generate_random_formation(enemy_types, difficulty)

    def _generate_circle_formation(self, enemy_types, difficulty):
        """Generate a circle formation around the center of the screen"""
        positions = []
        count = len(enemy_types)

        # Radius scales with difficulty
        radius = 150 + (difficulty * 100)  # 150-250 based on difficulty

        for i in range(count):
            angle = (i / count) * 2 * math.pi
            x = self.center_x + radius * math.cos(angle)
            y = self.center_y + radius * math.sin(angle)
            positions.append((x, y))

        return positions

    def _generate_line_formation(self, enemy_types, difficulty):
        """Generate a horizontal line formation"""
        positions = []
        count = len(enemy_types)

        # Line can be horizontal or vertical
        is_horizontal = random.random() > 0.5

        if is_horizontal:
            # Horizontal line
            y = 100 + random.randint(0, 200)  # Vary the y position
            spacing = (self.screen_width - 100) / (count + 1)
            for i in range(count):
                x = 50 + spacing * (i + 1)
                positions.append((x, y))
        else:
            # Vertical line
            x = 100 + random.randint(0, 400)  # Vary the x position
            spacing = (self.screen_height - 100) / (count + 1)
            for i in range(count):
                y = 50 + spacing * (i + 1)
                positions.append((x, y))

        return positions

    def _generate_grid_formation(self, enemy_types, difficulty):
        """Generate a grid formation"""
        positions = []
        count = len(enemy_types)

        # Calculate grid dimensions
        grid_size = math.ceil(math.sqrt(count))

        # Spacing scales with difficulty (tighter grid for higher difficulty)
        spacing = 100 - (difficulty * 30)  # 70-100 based on difficulty

        # Calculate starting position to center the grid
        start_x = self.center_x - (grid_size * spacing / 2)
        start_y = self.center_y - (grid_size * spacing / 2)

        for i in range(count):
            row = i // grid_size
            col = i % grid_size
            x = start_x + (col * spacing)
            y = start_y + (row * spacing)
            positions.append((x, y))

        return positions

    def _generate_v_shape_formation(self, enemy_types, difficulty):
        """Generate a V-shaped formation"""
        positions = []
        count = len(enemy_types)

        # V-shape parameters
        angle = math.pi / 4  # 45 degrees
        length = 300 + (difficulty * 100)  # Length scales with difficulty

        # Calculate positions
        half_count = count // 2

        # Left arm of the V
        for i in range(half_count):
            progress = i / half_count
            x = self.center_x - (progress * length * math.cos(angle))
            y = self.center_y + (progress * length * math.sin(angle))
            positions.append((x, y))

        # Right arm of the V
        for i in range(count - half_count):
            progress = i / (count - half_count)
            x = self.center_x + (progress * length * math.cos(angle))
            y = self.center_y + (progress * length * math.sin(angle))
            positions.append((x, y))

        return positions

    def _generate_spiral_formation(self, enemy_types, difficulty):
        """Generate a spiral formation"""
        positions = []
        count = len(enemy_types)

        # Spiral parameters
        a = 10  # Controls how tightly wound the spiral is
        b = 5 + (difficulty * 5)  # Controls how quickly the spiral expands

        for i in range(count):
            # Parametric equation for a spiral
            t = (i / count) * 4 * math.pi  # 0 to 4π (2 full rotations)
            r = a + b * t
            x = self.center_x + r * math.cos(t)
            y = self.center_y + r * math.sin(t)
            positions.append((x, y))

        return positions

    def _generate_random_formation(self, enemy_types, difficulty):
        """Generate random positions within screen bounds"""
        positions = []
        count = len(enemy_types)

        # Define spawn area (margin from edges)
        margin = 100

        for _ in range(count):
            x = random.randint(margin, self.screen_width - margin)
            y = random.randint(margin, self.screen_height - margin)
            positions.append((x, y))

        return positions
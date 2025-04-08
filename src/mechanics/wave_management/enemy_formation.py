import random
import math

class FormationGenerator:
    def __init__(self):
        self.formation_types = {
            "circle": self._generate_circle_formation,
            "grid": self._generate_grid_formation,
            "random": self._generate_random_formation,
            "line": self._generate_line_formation,
            "arc": self._generate_arc_formation,
            "pincer": self._generate_pincer_formation
        }

    def generate_formation(self, enemy_types, player_style, difficulty):
        """Generate a formation of enemy positions based on player style and difficulty"""
        # Choose formation type based on player style and difficulty
        formation_type = self._select_formation_type(player_style, difficulty)

        # Generate positions using the selected formation type
        positions = self.formation_types[formation_type](
            len(enemy_types),
            player_style,
            difficulty
        )

        return positions

    def _select_formation_type(self, player_style, difficulty):
        """Select an appropriate formation type based on player style"""
        # For aggressive players, use more challenging formations at higher difficulties
        if player_style.get("aggression", 0) > 0.6 and difficulty > 0.5:
            return random.choice(["pincer", "circle", "arc"])

        # For cautious players, use more spread out formations
        elif player_style.get("caution", 0) > 0.6:
            return random.choice(["grid", "line", "random"])

        # For balanced players or low difficulty, use random formations
        else:
            return random.choice(list(self.formation_types.keys()))

    def _generate_circle_formation(self, count, player_style, difficulty):
        """Generate a circle formation around the center of the screen"""
        positions = []
        center_x, center_y = 400, 300  # Assuming screen center
        radius = 200 + (difficulty * 50)  # Adjust radius based on difficulty

        for i in range(count):
            angle = (i / count) * 2 * math.pi
            x = center_x + radius * math.cos(angle)
            y = center_y + radius * math.sin(angle)
            positions.append((x, y))

        return positions

    def _generate_grid_formation(self, count, player_style, difficulty):
        """Generate a grid formation"""
        positions = []

        # Calculate grid dimensions
        grid_size = math.ceil(math.sqrt(count))
        spacing = 80 - (difficulty * 20)  # Closer spacing at higher difficulties

        start_x = 400 - (grid_size * spacing / 2)
        start_y = 300 - (grid_size * spacing / 2)

        for i in range(count):
            row = i // grid_size
            col = i % grid_size
            x = start_x + (col * spacing)
            y = start_y + (row * spacing)
            positions.append((x, y))

        return positions

    def _generate_random_formation(self, count, player_style, difficulty):
        """Generate random positions within screen bounds"""
        positions = []

        for _ in range(count):
            x = random.randint(100, 700)
            y = random.randint(100, 500)
            positions.append((x, y))

        return positions

    def _generate_line_formation(self, count, player_style, difficulty):
        """Generate a horizontal or vertical line formation"""
        positions = []

        # Decide between horizontal or vertical
        if random.random() < 0.5:
            # Horizontal line
            y = random.randint(150, 450)
            spacing = 700 / (count + 1)
            for i in range(count):
                x = 50 + spacing * (i + 1)
                positions.append((x, y))
        else:
            # Vertical line
            x = random.randint(150, 650)
            spacing = 500 / (count + 1)
            for i in range(count):
                y = 50 + spacing * (i + 1)
                positions.append((x, y))

        return positions

    def _generate_arc_formation(self, count, player_style, difficulty):
        """Generate an arc formation"""
        positions = []
        center_x, center_y = 400, -100  # Arc center below the screen
        radius = 500

        # Arc spans about 120 degrees
        start_angle = math.pi * 0.3
        end_angle = math.pi * 0.7

        for i in range(count):
            angle = start_angle + (i / (count - 1 if count > 1 else 1)) * (end_angle - start_angle)
            x = center_x + radius * math.cos(angle)
            y = center_y + radius * math.sin(angle)
            positions.append((x, y))

        return positions

    def _generate_pincer_formation(self, count, player_style, difficulty):
        """Generate a pincer formation to trap the player"""
        positions = []

        # Split enemies into two groups
        left_count = count // 2
        right_count = count - left_count

        # Left side pincer
        for i in range(left_count):
            x = 100
            y = 100 + (400 / (left_count + 1)) * (i + 1)
            positions.append((x, y))

        # Right side pincer
        for i in range(right_count):
            x = 700
            y = 100 + (400 / (right_count + 1)) * (i + 1)
            positions.append((x, y))

        return positions
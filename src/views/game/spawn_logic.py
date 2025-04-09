import random
import arcade

def spawn_enemy(self, enemy_type, position, speed=1.0, health=1.0):
        """Spawn an enemy with the given parameters."""
        print(f"Game view spawning enemy: {enemy_type} at {position} with speed={speed}, health={health}")

        # Extract position components
        if isinstance(position, tuple) and len(position) >= 2:
            x, y = position[0], position[1]
        else:
            print(f"Invalid position format: {position}")
            window = arcade.get_window()
            x, y = random.randint(50, window.width - 50), random.randint(50, window.height - 50)

        # Create enemy based on type
        enemy = None

        try:
            # Use the correct class names
            if enemy_type == "chaser":
                from src.entities.enemies.chaser import Chaser
                enemy = Chaser(x, y)
            elif enemy_type == "wander":
                from src.entities.enemies.wanderer import Wanderer
                enemy = Wanderer(x, y)
            elif enemy_type == "shooter":
                from src.entities.enemies.shooter import Shooter
                enemy = Shooter(x, y)
            elif enemy_type == "boss":
                from src.entities.enemies.boss import Boss
                enemy = Boss(x, y)
        except ImportError as e:
            print(f"Error importing enemy class: {e}")
            # Fall back to a basic enemy implementation
            try:
                # Create a basic enemy sprite
                enemy = arcade.Sprite()
                enemy.center_x = x
                enemy.center_y = y

                # Set appearance based on enemy type
                if enemy_type == "chaser":
                    enemy.texture = arcade.make_circle_texture(30, arcade.color.PURPLE)
                elif enemy_type == "wanderer":
                    enemy.texture = arcade.make_circle_texture(30, arcade.color.ORANGE)
                elif enemy_type == "shooter":
                    enemy.texture = arcade.make_circle_texture(30, arcade.color.BLUE)
                else:
                    enemy.texture = arcade.make_circle_texture(30, arcade.color.RED)

                # Set basic properties
                enemy.scale = 1.0
                enemy.speed = speed
                enemy.health = health
                enemy.enemy_type = enemy_type

                print(f"Created fallback enemy of type: {enemy_type}")
            except Exception as e:
                print(f"Error creating fallback enemy: {e}")
                return
        except Exception as e:
            print(f"Error creating enemy: {e}")
            return

        if enemy:
            # Apply speed and health modifiers
            if hasattr(enemy, 'speed'):
                enemy.speed *= speed
            if hasattr(enemy, 'max_health'):
                enemy.max_health = int(enemy.max_health * health)
                enemy.health = enemy.max_health

            # Add to sprite lists
            print(f"Adding enemy to sprite lists")
            self.enemies.append(enemy)

            # Add to scene if it exists
            if hasattr(self, 'scene') and hasattr(self.scene, 'add_sprite'):
                try:
                    self.scene.add_sprite("enemies", enemy)
                except Exception as e:
                    print(f"Error adding to scene: {e}")

            return enemy

def spawn_artifact(self, x=None, y=None, artifact_type=None):
        """
        Spawn an artifact at the specified position or a random position.

        Args:
            x (float, optional): X-coordinate for the artifact. If None, a random position is chosen.
            y (float, optional): Y-coordinate for the artifact. If None, a random position is chosen.
            artifact_type (str, optional): Type of artifact to spawn. If None, a random type is chosen.

        Returns:
            bool: True if artifact was spawned successfully, False otherwise.
        """
        # Import the artifact class
        try:
            from src.mechanics.artifacts.base import BaseArtifact
            from src.mechanics.artifacts.dash_artifact import DashArtifact
            from src.mechanics.artifacts.bullet_time import BulletTimeArtifact
            # Import other artifact types as needed
        except ImportError as e:
            print(f"Error importing artifact classes: {e}")
            return False

        # If no position specified, choose a random position
        if x is None or y is None:
            margin = 50
            max_attempts = 10  # Limit attempts to find valid position

            for _ in range(max_attempts):
                # Generate random position
                x = random.randint(margin, self.window.width - margin)
                y = random.randint(margin, self.window.height - margin)

                # Check distance from player
                if hasattr(self, 'player'):
                    player_pos = (self.player.center_x, self.player.center_y)
                    artifact_pos = (x, y)
                    distance = ((player_pos[0] - artifact_pos[0])**2 + (player_pos[1] - artifact_pos[1])**2)**0.5

                    # If too close to player, try again
                    if distance < 100:  # Minimum distance
                        continue

                # Valid position found
                break

        # If no artifact type specified, choose a random one
        if artifact_type is None:
            artifact_types = ["dash", "bullet_time"]  # Add more types as needed
            artifact_type = random.choice(artifact_types)

        try:
            # Create the appropriate artifact based on type
            if artifact_type == "dash":
                artifact = DashArtifact(x, y)
            elif artifact_type == "bullet_time":
                artifact = BulletTimeArtifact(x, y)
            else:
                print(f"Unknown artifact type: {artifact_type}")
                return False

            # Add to sprite lists
            if not hasattr(self, 'artifacts'):
                self.artifacts = arcade.SpriteList()

            self.artifacts.append(artifact)

            # Add to all_sprites if it exists
            if hasattr(self, 'all_sprites'):
                self.all_sprites.append(artifact)

            print(f"🔮 Spawned a {artifact_type} artifact at ({x}, {y})!")
            return True

        except Exception as e:
            print(f"Error spawning artifact: {e}")
            return False
        
def clear_enemies(self):
        """Clear all enemies from the screen."""
        self.enemies = arcade.SpriteList()

def spawn_orbs(game_view):
    """Spawns an orb if the orb spawn timer has elapsed."""
    if not hasattr(game_view, 'orb_spawn_timer'):
        return

    game_view.orb_spawn_timer -= 1/60  # assuming called every frame
    if game_view.orb_spawn_timer <= 0:
        width, height = game_view.get_screen_dimensions()
        x = random.randint(50, width - 50)
        y = random.randint(50, height - 50)
        
        # Import the orb generator function
        from src.entities.orbs.orb_pool import get_random_orb
        
        orb = get_random_orb(x, y, context={
            "wave": getattr(game_view.wave_manager, 'current_wave', 1),
            "hp": getattr(game_view.player, 'current_hearts', 3),
            "mult": getattr(game_view.player, 'score_multiplier', 1)
        })

        game_view.orbs.append(orb)
        game_view.orb_spawn_timer = random.uniform(4, 8)
        print("🔮 Spawned an orb!")

def spawn_coin(game_view):
    """Spawns a coin at a random position."""
    pass

# Export the functions
__all__ = [
    "spawn_enemy",
    "clear_enemies",
    "spawn_artifact",
    "spawn_orbs",
    "spawn_coin"
]
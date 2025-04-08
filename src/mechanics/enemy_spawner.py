import random
import arcade
from typing import List
from src.mechanics.wave_manager import WaveManager
from src.core.constants import SCREEN_WIDTH, SCREEN_HEIGHT

class EnemySpawner:
    """Handles spawning enemies with appropriate types and frequencies"""

    def __init__(self, wave_manager: WaveManager, player):
        self.wave_manager = wave_manager
        self.player = player
        self.spawn_timer = 0
        self.special_event = None
        self.special_event_timer = 0

    def update(self, delta_time: float) -> List[arcade.Sprite]:
        """
        Update the enemy spawner and spawn enemies as needed

        Args:
            delta_time: Time since last frame

        Returns:
            List of new enemies to spawn
        """
        new_enemies = []

        # Update special event timer if active
        if self.special_event:
            self.special_event_timer += delta_time
            if self.special_event_timer >= self.special_event["duration"]:
                self.special_event = None
                self.special_event_timer = 0

        # Check if we should spawn an enemy
        should_spawn, self.spawn_timer = self.wave_manager.should_spawn_enemy(
            delta_time, self.spawn_timer
        )

        if should_spawn:
            # Create a new enemy
            new_enemy = self._spawn_enemy()
            if new_enemy:
                new_enemies.append(new_enemy)

                # Spawn an extra enemy during Double Enemies event
                if self.special_event and self.special_event["name"] == "Double Enemies":
                    extra_enemy = self._spawn_enemy()
                    if extra_enemy:
                        new_enemies.append(extra_enemy)

        return new_enemies

    def set_special_event(self, event: dict):
        """Set an active special event"""
        self.special_event = event
        self.special_event_timer = 0

    def _spawn_enemy(self) -> arcade.Sprite:
        """Spawn a single enemy with appropriate type based on current wave"""
        from src.entities.enemy import Enemy

        # Get enemy speed multiplier for current wave
        speed_multiplier = self.wave_manager.get_enemy_speed()

        # Adjust speed for Bullet Speed Up event
        if self.special_event and self.special_event["name"] == "Bullet Speed Up":
            if hasattr(self.special_event, "bullet_speed_multiplier"):
                speed_multiplier *= self.special_event["bullet_speed_multiplier"]

        # Determine enemy type based on wave
        enemy_types = ["basic"]
        if self.wave_manager.current_wave >= 5:
            enemy_types.append("chaser")
        if self.wave_manager.current_wave >= 10:
            enemy_types.append("shooter")
        if self.wave_manager.current_wave >= 20:
            enemy_types.append("elite")

        # Choose a random enemy type
        enemy_type = random.choice(enemy_types)

        # Generate spawn position (off-screen)
        margin = 50
        side = random.choice(["top", "bottom", "left", "right"])

        if side == "top":
            x = random.randint(margin, SCREEN_WIDTH - margin)
            y = SCREEN_HEIGHT + margin
        elif side == "bottom":
            x = random.randint(margin, SCREEN_WIDTH - margin)
            y = -margin
        elif side == "left":
            x = -margin
            y = random.randint(margin, SCREEN_HEIGHT - margin)
        else:  # right
            x = SCREEN_WIDTH + margin
            y = random.randint(margin, SCREEN_HEIGHT - margin)

        # Create the enemy
        enemy = Enemy(x, y, self.player, enemy_type=enemy_type)
        enemy.speed_multiplier = speed_multiplier

        return enemy
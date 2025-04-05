import random
from scripts.enemy import Enemy

class WaveManager:
    def __init__(self, player):
        self.wave = 1
        self.player = player

    def get_enemy_count(self):
        # Scale up enemy count every 5 waves, drop slightly after each 5th
        base = 2 + (self.wave % 5)
        return base + self.wave // 5

    def get_enemy_behaviors(self):
        # Create a list of enemy types (chaser, wander, shooter) with weights
        behaviors = ["chaser"] * 2 + ["wander"] * 2
        if self.wave >= 2:
            behaviors.append("shooter")
        if self.wave >= 5:
            behaviors += ["shooter", "chaser"]

        return random.choices(behaviors, k=self.get_enemy_count())

    def spawn_enemies(self, sprite_list, screen_width, screen_height):
        sprite_list.clear()

        for behavior in self.get_enemy_behaviors():
            x = random.randint(50, screen_width - 50)
            y = random.randint(50, screen_height - 50)
            sprite_list.append(Enemy(x, y, self.player, behavior=behavior))

        print(f"🌊 Wave {self.wave} started with {len(sprite_list)} enemies")

    def next_wave(self):
        self.wave += 1

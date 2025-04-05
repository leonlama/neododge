import random
from scripts.enemy import Enemy

class WaveManager:
    def __init__(self, player):
        self.wave = 1
        self.player = player

    def generate_wave(self, wave_number):
        # Determine difficulty curve
        num_enemies = min(3 + wave_number, 25)
        if wave_number % 6 == 0:
            return {
                "type": "rest",
                "enemies": 2,
                "enemy_types": ["wander"]
            }
        else:
            types = ["chaser", "wander"]
            if wave_number >= 7:
                types.append("shooter")
            return {
                "type": "normal",
                "enemies": num_enemies,
                "enemy_types": random.choices(types, k=num_enemies)
            }

    def spawn_enemies(self, sprite_list, screen_width, screen_height):
        sprite_list.clear()
        wave_info = self.generate_wave(self.wave)

        for behavior in wave_info["enemy_types"]:
            x = random.randint(50, screen_width - 50)
            y = random.randint(50, screen_height - 50)
            sprite_list.append(Enemy(x, y, self.player, behavior=behavior))

        print(f"🌊 Wave {self.wave} ({wave_info['type']}) started with {len(sprite_list)} enemies")

    def next_wave(self):
        self.wave += 1

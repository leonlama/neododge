import random
from scripts.characters.enemy import Enemy
from scripts.mechanics.orbs.buff_orbs import BuffOrb
from scripts.mechanics.orbs.debuff_orbs import DebuffOrb
from scripts.mechanics.artifacts.dash_artifact import DashArtifact
from scripts.mechanics.artifacts.magnet_pulse import MagnetPulseArtifact
from scripts.mechanics.artifacts.slow_field import SlowFieldArtifact
from scripts.mechanics.artifacts.bullet_time import BulletTimeArtifact
from scripts.mechanics.artifacts.clone_dash import CloneDashArtifact

class WaveManager:
    def __init__(self, player):
        self.wave = 1
        self.player = player

    def generate_wave(self, wave_number):
        num_enemies = min(3 + wave_number + wave_number // 3, 25)
        enemy_types = ["chaser", "wander"]
        if wave_number >= 5:
            enemy_types.append("shooter")

        if wave_number % 6 == 0:
            return {
                "type": "rest",
                "enemies": 2,
                "enemy_types": ["wander"],
                "orbs": 0,
                "artifact": False
            }

        if wave_number < 5:
            orb_count = 0
        elif wave_number < 10:
            orb_count = 1
        elif wave_number < 15:
            orb_count = 2
        else:
            orb_count = 3

        spawn_artifact = (wave_number % 5 == 0)

        return {
            "type": "normal",
            "enemies": num_enemies,
            "enemy_types": random.choices(enemy_types, k=num_enemies),
            "orbs": orb_count,
            "artifact": spawn_artifact,
        }

    def spawn_enemies(self, sprite_list, screen_width, screen_height):
        sprite_list.clear()
        wave_info = self.generate_wave(self.wave)

        for behavior in wave_info["enemy_types"]:
            x = random.randint(50, screen_width - 50)
            y = random.randint(50, screen_height - 50)
            sprite_list.append(Enemy(x, y, self.player, behavior=behavior))

        print(f"🌊 Wave {self.wave} ({wave_info['type']}) started with {len(sprite_list)} enemies")
        return wave_info

    def spawn_orbs(self, orb_list, count, screen_width, screen_height):
        for _ in range(count):
            x = random.randint(50, screen_width - 50)
            y = random.randint(50, screen_height - 50)
            orb = random.choices(
                [BuffOrb(x, y), DebuffOrb(x, y)],
                weights=[0.8, 0.2]
            )[0]
            orb_list.append(orb)

    def maybe_spawn_artifact(self, player_artifacts, current_artifact, screen_width, screen_height):
        if current_artifact is not None:
            return None

        all_types = {
            "Dash": DashArtifact,
            "Magnet Pulse": MagnetPulseArtifact,
            "Slow Field": SlowFieldArtifact,
            "Bullet Time": BulletTimeArtifact,
            "Clone Dash": CloneDashArtifact
        }

        available = [name for name in all_types if name not in player_artifacts]
        if not available:
            return None

        name = random.choice(available)
        artifact_class = all_types[name]
        art = artifact_class()
        art.center_x = random.randint(50, screen_width - 50)
        art.center_y = random.randint(50, screen_height - 50)
        art.name = name
        return art

    def next_wave(self):
        self.wave += 1

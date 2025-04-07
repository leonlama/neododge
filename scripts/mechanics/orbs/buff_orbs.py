import arcade

from scripts.utils.constants import MDMA_SKIN_PATH

class BuffOrb(arcade.Sprite):
    def __init__(self, x, y, orb_type="gray"):
        super().__init__()
        self.orb_type = orb_type
        self.age = 0

        color_map = {
            "gray": arcade.color.GRAY,
            "red": arcade.color.RED,
            "gold": arcade.color.GOLD,
            "speed_10": arcade.color.BLUE_BELL,
            "speed_20": arcade.color.BLUE_VIOLET,
            "speed_35": arcade.color.DARK_BLUE,
            "mult_1_5": arcade.color.ORANGE,
            "mult_2": arcade.color.YELLOW_ORANGE,
            "cooldown": arcade.color.PURPLE,
            "shield": arcade.color.LIGHT_GREEN,
        }

        color = color_map.get(orb_type, arcade.color.WHITE)
        self.texture = arcade.make_soft_circle_texture(18, color, outer_alpha=255)

        # Override texture if specific PNGs are available
        if orb_type == "cooldown":
            self.texture = arcade.load_texture(MDMA_SKIN_PATH + "/orbs/cd_telsa.png")
            self.scale = 0.05
        elif orb_type == "shield":
            self.texture = arcade.load_texture(MDMA_SKIN_PATH + "/orbs/shield_tictac.png")
            self.scale = 0.05
        elif orb_type.startswith("speed_"):
            self.texture = arcade.load_texture(MDMA_SKIN_PATH + "/orbs/speed_punisher.png")
            self.scale = 0.05

        self.center_x = x
        self.center_y = y

        self.message = {
            "gray": "🩶 Bonus heart slot gained!",
            "red": "❤️ Heart restored!",
            "gold": "💛 Golden heart gained!",
            "speed_10": "⚡ Speed +10%",
            "speed_20": "⚡ Speed +20%",
            "speed_35": "⚡ Speed +35%",
            "mult_1_5": "💥 Score x1.5 for 30s",
            "mult_2": "💥 Score x2 for 30s",
            "cooldown": "🔁 Cooldown reduced!",
            "shield": "🛡️ Shield acquired!",
        }.get(self.orb_type, "✨ Buff Orb")

    def update(self, delta_time: float = 1 / 60):
        self.age += delta_time

    def apply_effect(self, player):
        if self.orb_type == "gray":
            player.max_slots += 1
            print(self.message)
        elif self.orb_type == "red":
            if player.current_hearts < player.max_slots:
                player.current_hearts += 1
                print(self.message)
            else:
                print("❌ No empty slot for red orb.")
        elif self.orb_type == "gold":
            player.gold_hearts += 1
            print(self.message)
        elif self.orb_type == "speed_10":
            player.speed_bonus += 0.10
            player.active_orbs.append(["⚡ Speed +10%", 45])
            print(self.message)
        elif self.orb_type == "speed_20":
            player.speed_bonus += 0.20
            player.active_orbs.append(["⚡ Speed +20%", 40])
            print(self.message)
        elif self.orb_type == "speed_35":
            player.speed_bonus += 0.35
            player.active_orbs.append(["⚡ Speed +35%", 30])
            print(self.message)
        elif self.orb_type == "mult_1_5":
            player.multiplier = 1.5
            player.mult_timer = 30
            player.active_orbs.append(["Score x1.5", 30])
            print(self.message)
        elif self.orb_type == "mult_2":
            player.multiplier = 2.0
            player.mult_timer = 30
            player.active_orbs.append(["Score x2", 30])
            print(self.message)
        elif self.orb_type == "cooldown":
            self.message = "🔁 Cooldown reduced! (20%)"
            player.cooldown *= 0.8
            print(self.message)
        elif self.orb_type == "shield":
            player.shield = True
            print(self.message)

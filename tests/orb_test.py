import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import arcade
from scripts.mechanics.orbs.orb import Orb
from src.entities.player import Player

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Orb Test – Neododge"

class OrbTest(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
        arcade.set_background_color(arcade.color.BLACK)

        self.player = None
        self.orbs = None
        self.pickup_texts = []

    def setup(self):
        self.player = Player(400, 300)
        self.orbs = arcade.SpriteList()

        # Spawn one of each orb type
        orb_types = [
            "gray", "red", "gold",
            "speed_10", "speed_20", "speed_35",
            "mult_1_5", "mult_2",
            "cooldown", "shield",
            "slow", "bigger_hitbox", "mult_0_5", "mult_0_25", "anti_cd"
        ]

        for i, orb_type in enumerate(orb_types):
            x = 60 + (i % 5) * 150
            y = 500 - (i // 5) * 100
            self.orbs.append(Orb(x, y, orb_type))

    def on_draw(self):
        self.clear()
        self.player.draw()
        self.orbs.draw()

        for text, x, y, _ in self.pickup_texts:
            arcade.draw_text(text, x, y + 20, arcade.color.WHITE, 14, anchor_x="center")

    def on_update(self, delta_time):
        self.player.update(delta_time)
        self.orbs.update()

        for orb in self.orbs:
            if orb.age > 0.5 and arcade.check_for_collision(self.player, orb):
                self.pickup_texts.append([f"Picked up {orb.orb_type}", orb.center_x, orb.center_y, 1.5])
                self.orbs.remove(orb)

        for t in self.pickup_texts:
            t[3] -= delta_time
        self.pickup_texts = [t for t in self.pickup_texts if t[3] > 0]

    def on_mouse_press(self, x, y, button, modifiers):
        if button == arcade.MOUSE_BUTTON_RIGHT:
            self.player.set_target(x, y)

if __name__ == "__main__":
    window = OrbTest()
    window.setup()
    arcade.run()

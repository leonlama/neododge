import arcade
from scripts.player import Player
from scripts.orbs.buff_orbs import BuffOrb
from scripts.orbs.debuff_orbs import DebuffOrb

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

class TestOrbsView(arcade.View):
    def __init__(self):
        super().__init__()
        self.player = None
        self.orbs = arcade.SpriteList()
        self.pickup_texts = []

    def setup(self):
        self.player = Player(100, 300)
        self.player.can_dash = True

        # --- Buff Orbs ---
        self.orbs.append(BuffOrb(200, 500, "golden"))
        self.orbs.append(BuffOrb(300, 500, "bonus_slot"))
        self.orbs.append(BuffOrb(400, 500, "heal"))
        self.orbs.append(BuffOrb(500, 500, "shield"))
        self.orbs.append(BuffOrb(600, 500, "speed_10"))
        self.orbs.append(BuffOrb(700, 500, "speed_20"))

        # --- Debuff Orbs ---
        self.orbs.append(DebuffOrb(200, 300, "cooldown"))
        self.orbs.append(DebuffOrb(300, 300, "inverse"))
        self.orbs.append(DebuffOrb(400, 300, "multiplier_half"))
        self.orbs.append(DebuffOrb(500, 300, "slow"))
        self.orbs.append(DebuffOrb(600, 300, "vision"))

    def on_draw(self):
        self.clear()
        self.player.draw()
        self.orbs.draw()
        self.player.draw_hearts()
        self.player.draw_orb_status()
        self.player.draw_artifacts()

        for text, x, y, _ in self.pickup_texts:
            arcade.draw_text(text, x, y + 20, arcade.color.WHITE, 14, anchor_x="center")

    def on_update(self, delta_time):
        self.player.update(delta_time)
        self.orbs.update()

        for orb in self.orbs:
            if arcade.check_for_collision(self.player, orb):
                orb.apply_effect(self.player)
                self.pickup_texts.append([orb.message, self.player.center_x, self.player.center_y, 1.5])
                self.orbs.remove(orb)

        for t in self.pickup_texts:
            t[3] -= delta_time
        self.pickup_texts = [t for t in self.pickup_texts if t[3] > 0]

    def on_mouse_press(self, x, y, button, modifiers):
        if button == arcade.MOUSE_BUTTON_RIGHT:
            self.player.set_target(x, y)

    def on_key_press(self, symbol, modifiers):
        if symbol == arcade.key.SPACE:
            self.player.try_dash()

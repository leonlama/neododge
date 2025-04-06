import arcade
import random
from scripts.utils.constants import SCREEN_WIDTH, SCREEN_HEIGHT

SHOP_MUSIC_PATH = "assets/audio/shop.mp3"

class ShopView(arcade.View):
    def __init__(self, player, return_view):
        super().__init__()
        self.player = player
        self.return_view = return_view
        self.music = None
        self.items = []
        self.selected_item = None
        self.message = ""

    def on_show(self):
        arcade.set_background_color(arcade.color.BLACK)
        self.music = arcade.load_sound(SHOP_MUSIC_PATH, volume=0.5)
        arcade.play_sound(self.music, looping=True)
        self.generate_shop_items()

    def generate_shop_items(self):
        all_items = [
            # 🔁 Permanent Upgrades (3 tiers)
            {"name": "Agile Reflexes I", "desc": "+2% Move Speed", "cost": 5, "type": "perm", "effect": "speed_2"}, #🌀
            {"name": "Agile Reflexes II", "desc": "+5% Move Speed", "cost": 10, "type": "perm", "effect": "speed_5"}, #🌀
            {"name": "Agile Reflexes III", "desc": "+10% Move Speed", "cost": 15, "type": "perm", "effect": "speed_10"}, #🌀

            {"name": "Vitality Boost I", "desc": "+1 Max HP", "cost": 8, "type": "perm", "effect": "hp_1"}, #❤️
            {"name": "Vitality Boost II", "desc": "+3 Max HP", "cost": 15, "type": "perm", "effect": "hp_3"}, #❤️
            {"name": "Vitality Boost III", "desc": "+5 Max HP", "cost": 25, "type": "perm", "effect": "hp_5"}, #❤️

            {"name": "Orb Affinity I", "desc": "+3% Orb Rate", "cost": 5, "type": "perm", "effect": "orb_3"}, #🎯        
            {"name": "Orb Affinity II", "desc": "+5% Orb Rate", "cost": 10, "type": "perm", "effect": "orb_5"}, #🎯
            {"name": "Orb Affinity III", "desc": "+7% Orb Rate", "cost": 15, "type": "perm", "effect": "orb_7"}, #🎯

            {"name": "Lucky Collector I", "desc": "+5% Coin Rate", "cost": 5, "type": "perm", "effect": "coin_5"}, #🍀
            {"name": "Lucky Collector II", "desc": "+10% Coin Rate", "cost": 10, "type": "perm", "effect": "coin_10"}, #🍀
            {"name": "Lucky Collector III", "desc": "+15% Coin Rate", "cost": 15, "type": "perm", "effect": "coin_15"}, #🍀

            {"name": "Kinetic Absorption I", "desc": "5% Negate Hit", "cost": 10, "type": "perm", "effect": "absorb_5"},#💥
            {"name": "Kinetic Absorption II", "desc": "10% Negate Hit", "cost": 15, "type": "perm", "effect": "absorb_10"}, #💥
            {"name": "Kinetic Absorption III", "desc": "15% Negate Hit", "cost": 20, "type": "perm", "effect": "absorb_15"}, #💥

            # 🛡 Temporary Boosts (1–3 waves)
            {"name": "Shield", "desc": "Block next hit", "cost": 5, "type": "temp", "effect": "shield"}, #🛡️
            {"name": "Multiplier", "desc": "2x Score (1–3 waves)", "cost": 8, "type": "temp", "effect": "multiplier"}, #💰

            # 🧰 Utility
            {"name": "Skip Wave", "desc": "Skip next wave, get points", "cost": 12, "type": "util", "effect": "skip"},
            {"name": "Second Chance", "desc": "Revive with 1 Heart", "cost": 20, "type": "util", "effect": "revive"},
        ]

        # Select 3 unique random items
        self.items = random.sample(all_items, 3)

    def on_draw(self):
        self.clear()
        arcade.draw_text("🛒 SHOP", SCREEN_WIDTH // 2, SCREEN_HEIGHT - 80, arcade.color.GOLD, 36, anchor_x="center")

        for idx, item in enumerate(self.items):
            y = SCREEN_HEIGHT - 150 - idx * 50
            text = f"{idx + 1}. {item['name']} – {item['desc']} ({item['cost']} 🪙)"
            arcade.draw_text(text, 60, y, arcade.color.LIGHT_GREEN if self.player.coins >= item["cost"] else arcade.color.GRAY, 18)

        arcade.draw_text(f"Coins: {self.player.coins}", SCREEN_WIDTH - 150, SCREEN_HEIGHT - 50, arcade.color.YELLOW, 18)
        if self.message:
            arcade.draw_text(self.message, SCREEN_WIDTH // 2, 60, arcade.color.WHITE, 16, anchor_x="center")

    def on_key_press(self, symbol, modifiers):
        from arcade.key import KEY_1, KEY_2, KEY_3, KEY_4, KEY_5, KEY_6, KEY_7, KEY_8, KEY_9
        keys = [KEY_1, KEY_2, KEY_3, KEY_4, KEY_5, KEY_6, KEY_7, KEY_8, KEY_9]
        if symbol in keys:
            idx = keys.index(symbol)
            if idx < len(self.items):
                self.attempt_purchase(idx)

    def attempt_purchase(self, idx):
        item = self.items[idx]
        if self.player.coins >= item["cost"]:
            self.player.coins -= item["cost"]
            self.message = f"✅ Bought {item['name']}!"
            # TODO: Apply effect based on item["effect"]
        else:
            self.message = "❌ Not enough coins!"

    def on_mouse_press(self, x, y, button, modifiers):
        arcade.stop_sound(self.music)
        self.window.show_view(self.return_view)

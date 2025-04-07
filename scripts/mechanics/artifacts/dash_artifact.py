import arcade

class DashArtifact:
    def __init__(self, x, y):
        self.name = "Dash"
        self.cooldown = 10.0  # seconds
        self.cooldown_timer = self.cooldown  # Start fully ready!
        self.sprite = arcade.Sprite("assets/skins/mdma/artifacts/BluePunisher.png", scale=0.1)
        self.sprite.center_x = x
        self.sprite.center_y = y

    def apply_effect(self, player, *_):
        if self.cooldown_timer >= self.cooldown:
            player.perform_dash()
            self.cooldown_timer = 0
            print("⚡ Dash used!")
        else:
            print("❌ Dash on cooldown.")

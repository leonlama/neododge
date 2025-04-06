class DashArtifact:
    def __init__(self):
        self.name = "Dash"
        self.cooldown = 10.0  # seconds
        self.cooldown_timer = self.cooldown  # Start fully ready!

    def apply_effect(self, player, *_):
        if self.cooldown_timer >= self.cooldown:
            player.perform_dash()
            self.cooldown_timer = 0
            print("⚡ Dash used!")
        else:
            print("❌ Dash on cooldown.")

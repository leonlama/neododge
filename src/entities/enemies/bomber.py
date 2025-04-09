import arcade
import math
from .enemy import Enemy

class Bomber(Enemy):
    def __init__(self, x, y, scale=1.0):
        super().__init__("bomber", x, y, scale)
        self.explosion_timer = 3.0  # seconds until explosion
        self.explosion_radius = 100
        self.damage = 2
        self.exploded = False
        self.texture = arcade.load_texture("assets/skins/default/enemies/chaser.png")  # placeholder

    def update(self, delta_time: float = 1/60):
        if self.exploded:
            return

        self.explosion_timer -= delta_time
        if self.explosion_timer <= 0:
            self.explode()

    def explode(self):
        self.exploded = True
        # Check distance to player
        player = self.game_view.player
        if player:
            distance = math.hypot(player.center_x - self.center_x, player.center_y - self.center_y)
            if distance <= self.explosion_radius:
                player.take_damage(self.damage)

        # Add explosion animation/effect here
        arcade.play_sound(self.game_view.sound_manager.get("enemy", "death"))  # if sound exists
        self.kill()

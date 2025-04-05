import arcade
import random

from scripts.player import Player
from scripts.enemy import Enemy

# --- Constants ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Neododge"

class NeododgeGame(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
        arcade.set_background_color(arcade.color.BLACK)
        self.player = None
        self.enemies = None
        self.player_health = 100

    def setup(self):
        self.player = Player(self.width // 2, self.height // 2)
        self.enemies = arcade.SpriteList()

        for _ in range(3):
            x = random.randint(0, SCREEN_WIDTH)
            y = random.randint(0, SCREEN_HEIGHT)
            enemy = Enemy(x, y, self.player)
            self.enemies.append(enemy)

    def on_draw(self):
        self.clear()
        self.player.draw()
        self.enemies.draw()

        # Draw HP bar
        health_bar_width = self.player_health * 2
        arcade.draw_rectangle_filled(100, SCREEN_HEIGHT - 20, health_bar_width, 20, arcade.color.GREEN)
        arcade.draw_text(f"HP: {self.player_health}", 10, SCREEN_HEIGHT - 45, arcade.color.WHITE, 14)

    def on_update(self, delta_time):
        self.player.update(delta_time)
        for enemy in self.enemies:
            enemy.update(delta_time)

        # Collision detection
        for enemy in self.enemies:
            if arcade.check_for_collision(enemy, self.player):
                self.player_health -= 1
                print(f"💥 Hit! HP: {self.player_health}")
                if self.player_health <= 0:
                    print("💀 Game Over!")

    def on_mouse_press(self, x, y, button, modifiers):
        if button == arcade.MOUSE_BUTTON_RIGHT:
            self.player.set_target(x, y)

if __name__ == "__main__":
    game = NeododgeGame()
    game.setup()
    arcade.run()

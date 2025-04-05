import arcade
import random

from scripts.player import Player
from scripts.enemy import Enemy
from scripts.dash_artifact import DashArtifact

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
        self.dash_artifact = None

    def setup(self):
        self.player = Player(self.width // 2, self.height // 2)
        self.enemies = arcade.SpriteList()
        self.dash_artifact = DashArtifact(600, 300)

        # Spawn 1 of each type
        self.enemies.append(Enemy(100, 100, self.player, behavior="chaser"))
        self.enemies.append(Enemy(700, 100, self.player, behavior="wander"))
        self.enemies.append(Enemy(400, 500, self.player, behavior="shooter"))

    def on_draw(self):
        self.clear()
        self.player.draw()
        self.enemies.draw()

        if self.dash_artifact:
            self.dash_artifact.draw()

        for enemy in self.enemies:
            enemy.bullets.draw()

        # Draw HP bar
        health_bar_width = self.player_health * 2
        arcade.draw_rectangle_filled(100, SCREEN_HEIGHT - 20, health_bar_width, 20, arcade.color.GREEN)
        arcade.draw_text(f"HP: {self.player_health}", 10, SCREEN_HEIGHT - 45, arcade.color.WHITE, 14)

    def on_update(self, delta_time):
        self.player.update(delta_time)

        if self.dash_artifact and arcade.check_for_collision(self.player, self.dash_artifact):
            self.player.can_dash = True
            self.dash_artifact = None
            print("✨ Dash unlocked!")

        for enemy in self.enemies:
            enemy.update(delta_time)
            for bullet in enemy.bullets:
                bullet.update(delta_time)

                if bullet.age > 0.2 and arcade.check_for_collision(bullet, self.player):
                    self.player_health -= 5
                    print(f"🧨 Bullet hit! HP: {self.player_health}")
                    enemy.bullets.remove(bullet)

    def on_mouse_press(self, x, y, button, modifiers):
        if button == arcade.MOUSE_BUTTON_RIGHT:
            self.player.set_target(x, y)

    def on_key_press(self, symbol, modifiers):
        if symbol == arcade.key.SPACE:
            self.player.try_dash()

if __name__ == "__main__":
    game = NeododgeGame()
    game.setup()
    arcade.run()

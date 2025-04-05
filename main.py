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
        self.player_hearts = 3.0  # float to handle half-heart damage
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

        # Draw heart icons
        full_heart = int(self.player_hearts)
        half_heart = 1 if self.player_hearts % 1 >= 0.5 else 0

        for i in range(3):
            x = 30 + i * 40
            y = SCREEN_HEIGHT - 30
            if i < full_heart:
                arcade.draw_text("❤", x, y, arcade.color.RED, 30)
            elif i < full_heart + half_heart:
                arcade.draw_text("♥", x, y, arcade.color.LIGHT_RED_OCHRE, 30)  # half-heart style
            else:
                arcade.draw_text("♡", x, y, arcade.color.GRAY, 30)

    def on_update(self, delta_time):
        self.player.update(delta_time)

        if self.dash_artifact and arcade.check_for_collision(self.player, self.dash_artifact):
            self.player.can_dash = True
            self.dash_artifact = None
            print("✨ Dash unlocked!")

        for enemy in self.enemies:
            enemy.update(delta_time)
            if not self.player.invincible and arcade.check_for_collision(enemy, self.player):
                self.player_hearts -= 1
                self.player.invincible = True
                print(f"👾 Touched enemy! Hearts: {self.player_hearts}")
                if self.player_hearts <= 0:
                    print("💀 Game Over!")
                    arcade.close_window()
            for bullet in enemy.bullets:
                bullet.update(delta_time)

                if bullet.age > 0.2 and not self.player.invincible and arcade.check_for_collision(bullet, self.player):
                    self.player_hearts -= 0.5
                    self.player.invincible = True
                    print(f"💥 Bullet hit! Hearts: {self.player_hearts}")
                    enemy.bullets.remove(bullet)
                    if self.player_hearts <= 0:
                        print("💀 Game Over!")
                        arcade.close_window()

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

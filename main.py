import arcade
import random

from scripts.player import Player
from scripts.enemy import Enemy
from scripts.dash_artifact import DashArtifact
from scripts.orb import Orb

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
        self.orbs = None

    def setup(self):
        self.player = Player(self.width // 2, self.height // 2)
        self.enemies = arcade.SpriteList()
        self.dash_artifact = DashArtifact(600, 300)
        self.orbs = arcade.SpriteList()

        # Spawn 1 of each type
        self.enemies.append(Enemy(100, 100, self.player, behavior="chaser"))
        self.enemies.append(Enemy(700, 100, self.player, behavior="wander"))
        self.enemies.append(Enemy(400, 500, self.player, behavior="shooter"))

        # Example spawns
        self.orbs.append(Orb(300, 300, "gray"))
        self.orbs.append(Orb(300, 500, "red"))
        self.orbs.append(Orb(500, 300, "gold"))

    def on_draw(self):
        self.clear()
        self.player.draw()
        self.enemies.draw()
        self.orbs.draw()

        if self.dash_artifact:
            self.dash_artifact.draw()

        for enemy in self.enemies:
            enemy.bullets.draw()

        # Draw heart icons (left-aligned)
        x_start = 30
        y = SCREEN_HEIGHT - 30

        # Draw red/gray hearts
        for i in range(self.player.max_slots):
            x = x_start + i * 40
            if i < int(self.player.current_hearts):
                arcade.draw_text("❤", x, y, arcade.color.RED, 30)
            elif i < self.player.current_hearts:
                arcade.draw_text("♥", x, y, arcade.color.LIGHT_RED_OCHRE, 30)
            else:
                arcade.draw_text("♡", x, y, arcade.color.GRAY, 30)

        # Draw golden hearts next to them
        for i in range(self.player.gold_hearts):
            x = x_start + (self.player.max_slots + i) * 40
            arcade.draw_text("💛", x, y, arcade.color.GOLD, 30)

    def on_update(self, delta_time):
        self.player.update(delta_time)
        self.orbs.update()  # include in on_update()

        if self.dash_artifact and arcade.check_for_collision(self.player, self.dash_artifact):
            self.player.can_dash = True
            self.dash_artifact = None
            print("✨ Dash unlocked!")

        for enemy in self.enemies:
            enemy.update(delta_time)
            if not self.player.invincible and arcade.check_for_collision(enemy, self.player):
                self.player.take_damage(1.0)  # for enemy contact
                self.player.invincible = True
                print(f"👾 Touched enemy! Hearts: {self.player.current_hearts + self.player.gold_hearts}")
                if self.player.current_hearts + self.player.gold_hearts <= 0:
                    print("💀 Game Over!")
                    arcade.close_window()
            for bullet in enemy.bullets:
                bullet.update(delta_time)

                if bullet.age > 0.2 and not self.player.invincible and arcade.check_for_collision(bullet, self.player):
                    self.player.take_damage(0.5)  # for bullets
                    self.player.invincible = True
                    print(f"💥 Bullet hit! Hearts: {self.player.current_hearts + self.player.gold_hearts}")
                    enemy.bullets.remove(bullet)
                    if self.player.current_hearts + self.player.gold_hearts <= 0:
                        print("💀 Game Over!")
                        arcade.close_window()

        for orb in self.orbs:
            orb.update(delta_time)
            if orb.age > 0.5 and arcade.check_for_collision(orb, self.player):
                if orb.orb_type == "gray":
                    self.player.max_slots += 1
                    print("🩶 Bonus heart slot gained!")
                elif orb.orb_type == "red":
                    if self.player.current_hearts < self.player.max_slots:
                        self.player.current_hearts += 1
                        print("❤️ Heart restored!")
                    else:
                        print("❌ No empty slot for red orb.")
                elif orb.orb_type == "gold":
                    self.player.gold_hearts += 1
                    print("💛 Golden heart gained!")

                self.orbs.remove(orb)

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

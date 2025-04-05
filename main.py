import arcade
import random

from scripts.player import Player
from scripts.enemy import Enemy
from scripts.artifacts.dash_artifact import DashArtifact
from scripts.orbs.buff_orbs import BuffOrb
from scripts.orbs.debuff_orbs import DebuffOrb
from scripts.start_view import StartView
from scripts.game_over_view import GameOverView

# --- Constants ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Neododge"

def draw_vision_blur(player):
    shape = arcade.ShapeElementList()

    # Full screen black rectangle
    bg = arcade.create_rectangle_filled(
        SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, SCREEN_WIDTH, SCREEN_HEIGHT, arcade.color.BLACK
    )
    shape.append(bg)

    # Transparent vision circle centered on player
    vision_radius = 100  # Adjust as needed
    vision = arcade.create_ellipse_filled(
        player.center_x, player.center_y, vision_radius * 2, vision_radius * 2, (0, 0, 0, 0)
    )
    shape.append(vision)

    # Use stencil-style blend to cut hole
    shape.draw()

class NeododgeGame(arcade.View):
    def __init__(self):
        super().__init__()
        self.player = None
        self.enemies = None
        self.dash_artifact = None
        self.orbs = arcade.SpriteList()
        self.pickup_texts = []
        self.level_duration = 90.0
        self.level_timer = 0.0
        self.orb_spawn_timer = random.uniform(4, 8)
        self.artifact_spawn_timer = random.uniform(20, 30)
        self.score = 0

    def on_show(self):
        arcade.set_background_color(arcade.color.BLACK)

    def setup(self):
        self.player = Player(self.window.width // 2, self.window.height // 2)
        self.player.window = self.window  # 💡 Makes GameOverView possible
        self.player.parent_view = self    # 💡 So player can access score
        self.enemies = arcade.SpriteList()
        self.dash_artifact = DashArtifact(600, 300)
        self.orbs = arcade.SpriteList()

        # Test spawns
        self.enemies.append(Enemy(100, 100, self.player, behavior="chaser"))
        self.enemies.append(Enemy(700, 100, self.player, behavior="wander"))
        self.enemies.append(Enemy(400, 500, self.player, behavior="shooter"))

    def on_draw(self):
        self.clear()

        if self.player.vision_blur:
            arcade.draw_lrtb_rectangle_filled(
                0, SCREEN_WIDTH, SCREEN_HEIGHT, 0, arcade.color.BLACK
            )
            arcade.draw_circle_filled(
                self.player.center_x,
                self.player.center_y,
                120,  # radius of visibility
                (0, 0, 0, 0)
            )

        self.player.draw()
        self.enemies.draw()
        self.orbs.draw()

        if self.dash_artifact:
            self.dash_artifact.draw()
        for enemy in self.enemies:
            enemy.bullets.draw()

        # Draw vision blur if active
        if self.player.vision_blur:
            draw_vision_blur(self.player)

        # Draw HUD & GUI
        self.player.draw_hearts()
        self.player.draw_orb_status()
        self.player.draw_artifacts()
        for text, x, y, _ in self.pickup_texts:
            arcade.draw_text(text, x, y + 20, arcade.color.WHITE, 14, anchor_x="center")

        # Draw Score
        arcade.draw_text(f"Score: {int(self.score)}", 30, SCREEN_HEIGHT - 60, arcade.color.WHITE, 16)

    def on_update(self, delta_time):
        self.player.update(delta_time)
        self.orbs.update()
        self.level_timer += delta_time
        self.orb_spawn_timer -= delta_time
        self.artifact_spawn_timer -= delta_time
        self.score += delta_time * 10  # 10 points per second survived

        if self.orb_spawn_timer <= 0:
            x, y = random.randint(50, SCREEN_WIDTH - 50), random.randint(50, SCREEN_HEIGHT - 50)
            orb = random.choice([
                BuffOrb(x, y),
                DebuffOrb(x, y)
            ])
            self.orbs.append(orb)
            self.orb_spawn_timer = random.uniform(4, 8)

        if self.artifact_spawn_timer <= 0 and not self.dash_artifact:
            x, y = random.randint(50, SCREEN_WIDTH - 50), random.randint(50, SCREEN_HEIGHT - 50)
            self.dash_artifact = DashArtifact(x, y)
            self.artifact_spawn_timer = random.uniform(20, 30)

        if self.level_timer >= self.level_duration:
            print("✅ Level 1 Complete!")

        if self.dash_artifact and arcade.check_for_collision(self.player, self.dash_artifact):
            self.player.can_dash = True
            self.player.artifacts.append("Dash")
            self.dash_artifact = None
            print("✨ Dash unlocked!")

        for enemy in self.enemies:
            enemy.update(delta_time)
            for bullet in enemy.bullets:
                bullet.update(delta_time)

                # 🔥 Close dodge detection (within 35 px, but not hit)
                dist = arcade.get_distance_between_sprites(self.player, bullet)
                if 10 < dist < 35:
                    self.score += 1
                    print("🌀 Close dodge! +1 score")

                # Bullet hit check
                if bullet.age > 0.2 and not self.player.invincible and arcade.check_for_collision(bullet, self.player):
                    self.player.take_damage(0.5)
                    enemy.bullets.remove(bullet)

            if not self.player.invincible and arcade.check_for_collision(enemy, self.player):
                self.player.take_damage(1.0)

        for orb in self.orbs:
            orb.update(delta_time)
            if orb.age > 0.5 and arcade.check_for_collision(orb, self.player):
                orb.apply_effect(self.player)
                self.pickup_texts.append([orb.message, self.player.center_x, self.player.center_y, 1.0])
                self.orbs.remove(orb)

        # Update pickup text durations
        for t in self.pickup_texts:
            t[3] -= delta_time
        self.pickup_texts = [t for t in self.pickup_texts if t[3] > 0]

    def on_mouse_press(self, x, y, button, modifiers):
        if button == arcade.MOUSE_BUTTON_RIGHT:
            self.player.set_target(x, y)

    def on_key_press(self, symbol, modifiers):
        if symbol == arcade.key.SPACE:
            self.player.try_dash()
        elif symbol == arcade.key.S:
            self.player.set_target(self.player.center_x, self.player.center_y)

if __name__ == "__main__":
    window = arcade.Window(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    start_view = StartView()
    window.show_view(start_view)
    arcade.run()

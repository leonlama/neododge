import arcade
import random
from scripts.characters.player import Player
from scripts.characters.enemy import Enemy
from scripts.mechanics.artifacts.artifacts import (
    DashArtifact, MagnetPulseArtifact, SlowFieldArtifact,
    BulletTimeArtifact, CloneDashArtifact
)

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Artifact Test View"

ARTIFACT_COOLDOWNS = {
    "Dash": 5,
    "Magnet Pulse": 30,
    "Slow Field": 30,
    "Bullet Time": 30,
    "Clone Dash": 30
}

class TestArtifactsView(arcade.View):
    def __init__(self):
        super().__init__()
        self.player = None
        self.artifact_sprites = arcade.SpriteList()
        self.enemies = arcade.SpriteList()
        self.clone_life = 10.0  # Time before clone despawns
        self.active_clones = []

    def on_show(self):
        arcade.set_background_color(arcade.color.DARK_BLUE_GRAY)
        self.setup()

    def setup(self):
        self.player = Player(SCREEN_WIDTH // 2, 100)
        self.player.window = self.window
        self.player.parent_view = self
        self.player.pickup_messages = []
        self.player.can_dash = True
        self.player.artifact_slots = []
        self.player.artifact_cooldowns = {}
        self.player.active_artifacts = {}

        # Add artifacts for pickup
        artifact_classes = [
            DashArtifact, MagnetPulseArtifact, SlowFieldArtifact,
            BulletTimeArtifact, CloneDashArtifact
        ]
        for i, ArtifactClass in enumerate(artifact_classes):
            artifact = ArtifactClass()
            artifact.center_x = 100 + i * 140
            artifact.center_y = 400
            artifact.name = artifact.__class__.__name__.replace("Artifact", "").replace("CloneDash", "Clone Dash")
            self.artifact_sprites.append(artifact)

        # Add enemies to test effects
        for _ in range(5):
            x = random.randint(50, SCREEN_WIDTH - 50)
            y = random.randint(250, 550)
            enemy = Enemy(x, y, self.player, behavior=random.choice(["chaser", "shooter"]))
            self.enemies.append(enemy)

    def on_draw(self):
        self.clear()
        self.player.draw()
        self.artifact_sprites.draw()
        self.enemies.draw()

        for clone in self.active_clones:
            clone.draw()

        for enemy in self.enemies:
            enemy.bullets.draw()

        self.player.draw_hearts()
        self.player.draw_artifacts()

        # HUD Text for testing
        arcade.draw_text("Test Artifacts View", 30, SCREEN_HEIGHT - 40, arcade.color.WHITE, 18)

    def on_update(self, delta_time):
        self.player.update(delta_time)
        self.enemies.update()
        self.artifact_sprites.update()

        for enemy in self.enemies:
            for bullet in enemy.bullets:
                bullet.update(delta_time)

        for art in self.artifact_sprites:
            if arcade.check_for_collision(self.player, art):
                self.player.collect_artifact(art.name)
                self.artifact_sprites.remove(art)

        # Update artifact cooldowns
        for name in self.player.artifact_cooldowns:
            if self.player.artifact_cooldowns[name] > 0:
                self.player.artifact_cooldowns[name] -= delta_time

        # Despawn clones after 10 seconds
        for clone in self.active_clones:
            clone.timer -= delta_time
        self.active_clones = [c for c in self.active_clones if c.timer > 0]

    def on_mouse_press(self, x, y, button, modifiers):
        if button == arcade.MOUSE_BUTTON_RIGHT:
            self.player.set_target(x, y)

    def on_key_press(self, symbol, modifiers):
        keys = [arcade.key.Q, arcade.key.W, arcade.key.E, arcade.key.R]
        artifact_names = self.player.artifact_slots

        if symbol == arcade.key.SPACE:
            self.player.try_dash()

        elif symbol in keys:
            index = keys.index(symbol)
            if index < len(artifact_names):
                name = artifact_names[index]
                if self.player.artifact_cooldowns[name] <= 0:
                    self.activate_artifact(name)
                    self.player.artifact_cooldowns[name] = ARTIFACT_COOLDOWNS[name]

    def activate_artifact(self, name):
        from scripts.mechanics.artifacts.artifacts import (
            MagnetPulseArtifact,
            SlowFieldArtifact,
            BulletTimeArtifact,
            CloneDashArtifact,
        )

        if name == "Dash":
            self.player.try_dash()

        elif name == "Magnet Pulse":
            MagnetPulseArtifact().apply_effect(self.player, self.artifact_sprites)

        elif name == "Slow Field":
            bullets = arcade.SpriteList()
            for enemy in self.enemies:
                bullets.extend(enemy.bullets)
            SlowFieldArtifact().apply_effect(self.player, bullets)

        elif name == "Bullet Time":
            BulletTimeArtifact().apply_effect(self.enemies)

        elif name == "Clone Dash":
            clone = self.player.clone()
            clone.timer = self.clone_life
            self.active_clones.append(clone)
            CloneDashArtifact().apply_effect(self.player, self.active_clones)

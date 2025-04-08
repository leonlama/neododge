import arcade
import random
import math
from src.entities.player import Player
from src.core.resource_manager import resource_path
from src.skins.skin_manager import skin_manager
from src.ui.cooldown_bar import CooldownBar
from src.ui.hud import (
    draw_score, draw_wave_timer, draw_wave_number, 
    draw_coin_count, draw_player_health, draw_active_orbs,
    draw_game_over
)
from src.core.constants import SCREEN_WIDTH, SCREEN_HEIGHT, WAVE_DURATION, COOLDOWN_BAR_WIDTH, COOLDOWN_BAR_HEIGHT, HUD_MARGIN

class NeododgeGame(arcade.View):
    def __init__(self):
        super().__init__()
        self.player = None
        self.score = 0
        self.game_over = False
        self.enemies = arcade.SpriteList()
        self.pickups = arcade.SpriteList()
        self.bullets = arcade.SpriteList()
        self.spawn_timer = 0
        self.difficulty = 1
        self.difficulty_timer = 0
        self.game_time = 0
        self.wave = 1
        self.wave_timer = WAVE_DURATION
        self.dash_cooldown_bar = None
        self.mouse_pressed = False
        self.mouse_target_x = 0
        self.mouse_target_y = 0

    def setup(self):
        # Create the player
        self.player = Player(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, self)

        # Set up the game
        self.score = 0
        self.game_over = False
        self.enemies.clear()
        self.pickups.clear()
        self.bullets.clear()
        self.spawn_timer = 0
        self.difficulty = 1
        self.difficulty_timer = 0
        self.game_time = 0
        self.wave = 1
        self.wave_timer = WAVE_DURATION
        self.mouse_pressed = False

        # Create the dash cooldown bar
        self.dash_cooldown_bar = CooldownBar(
            "DASH", 
            HUD_MARGIN, 
            HUD_MARGIN, 
            COOLDOWN_BAR_WIDTH, 
            COOLDOWN_BAR_HEIGHT
        )

        # Add some test orb effects (using lists instead of tuples)
        self.player.active_orbs = [
            ["speed_20", 10.0],
            ["speed_35", 15.0],
            ["shield", 20.0],
            ["mult_2", 25.0]
        ]

        # Load sounds
        try:
            self.coin_sound = arcade.load_sound(resource_path("assets/audio/coin.flac"))
        except Exception as e:
            print("Failed to load coin sound:", e)
            self.coin_sound = None

    def on_draw(self):
        self.clear()

        # Draw the player
        self.player.draw()

        # Draw enemies, pickups, and bullets
        self.enemies.draw()
        self.pickups.draw()
        self.bullets.draw()

        # Draw the HUD
        self.draw_hud()

        # Draw game over text if game is over
        if self.game_over:
            draw_game_over(self.score)

    def draw_hud(self):
        # Draw wave info at top center with green font
        draw_wave_number(self.wave)

        # Draw wave timer below wave number
        draw_wave_timer(self.wave_timer, WAVE_DURATION)

        # Draw player health at top left
        draw_player_health(self.player)

        # Draw score below health
        draw_score(self.score)

        # Draw coins at bottom right
        draw_coin_count(self.player.coins)

        # Draw dash cooldown bar at bottom left
        self.dash_cooldown_bar.draw()

        # Draw active orb effects at top right
        draw_active_orbs(self.player)

    def update(self, delta_time):
        if self.game_over:
            return

        # Update game time
        self.game_time += delta_time

        # Update wave timer
        self.wave_timer -= delta_time
        if self.wave_timer <= 0:
            self.wave += 1
            self.wave_timer = WAVE_DURATION
            self.difficulty += 0.2
            # TODO: Spawn new wave of enemies

        # Handle continuous mouse movement
        if self.mouse_pressed:
            self.player.set_target(self.mouse_target_x, self.mouse_target_y)

        # Update player
        self.player.update(delta_time)

        # Update dash cooldown bar
        self.dash_cooldown_bar.set_progress(self.player.dash_timer / self.player.dash_cooldown)

        # Update enemies, bullets, and pickups
        self.enemies.update()
        self.bullets.update()
        self.pickups.update()

        # Check if player is dead
        if self.player.current_hearts <= 0:
            self.game_over = True

    def on_key_press(self, key, modifiers):
        if self.game_over:
            if key == arcade.key.RETURN:
                self.setup()
            return

        if key == arcade.key.UP or key == arcade.key.W:
            self.player.set_target(self.player.center_x, self.player.center_y + 100)
        elif key == arcade.key.DOWN or key == arcade.key.S:
            self.player.set_target(self.player.center_x, self.player.center_y - 100)
        elif key == arcade.key.LEFT or key == arcade.key.A:
            self.player.set_target(self.player.center_x - 100, self.player.center_y)
        elif key == arcade.key.RIGHT or key == arcade.key.D:
            self.player.set_target(self.player.center_x + 100, self.player.center_y)
        elif key == arcade.key.SPACE:
            if self.player.try_dash():
                self.dash_cooldown_bar.reset()

    def on_mouse_press(self, x, y, button, modifiers):
        if button == arcade.MOUSE_BUTTON_LEFT or button == arcade.MOUSE_BUTTON_RIGHT:
            self.mouse_pressed = True
            self.mouse_target_x = x
            self.mouse_target_y = y
            self.player.set_target(x, y)
            
            # Only dash with right click
            if button == arcade.MOUSE_BUTTON_RIGHT:
                if self.player.try_dash():
                    self.dash_cooldown_bar.reset()

    def on_mouse_release(self, x, y, button, modifiers):
        if button == arcade.MOUSE_BUTTON_LEFT or button == arcade.MOUSE_BUTTON_RIGHT:
            self.mouse_pressed = False

    def on_mouse_motion(self, x, y, dx, dy):
        if self.mouse_pressed:
            self.mouse_target_x = x
            self.mouse_target_y = y
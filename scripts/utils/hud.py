import arcade
from scripts.utils.constants import SCREEN_WIDTH, SCREEN_HEIGHT

def draw_score(score):
    arcade.draw_text(f"Score: {int(score)}", 30, SCREEN_HEIGHT - 60, arcade.color.WHITE, 16)

def draw_pickup_texts(pickup_texts):
    for text, x, y, _ in pickup_texts:
        arcade.draw_text(text, x, y + 20, arcade.color.WHITE, 14, anchor_x="center")

def draw_wave_timer(level_timer, wave_duration):
    time_left = max(0, int(wave_duration - level_timer))
    arcade.draw_text(f"⏱ {time_left}s left", SCREEN_WIDTH // 2, SCREEN_HEIGHT - 60,
                     arcade.color.LIGHT_GRAY, 16, anchor_x="center")

def draw_wave_message(wave_message, alpha):
    fade_color = (*arcade.color.LIGHT_GREEN[:3], alpha)
    arcade.draw_text(
        wave_message,
        SCREEN_WIDTH / 2,
        SCREEN_HEIGHT / 2,
        fade_color,
        font_size=24,
        anchor_x="center",
        font_name="Kenney Pixel"
    )

def draw_wave_number(current_wave):
    wave_text = f"Wave {current_wave}"
    wave_color = arcade.color.GOLD if current_wave % 5 == 0 else arcade.color.LIGHT_GREEN

    arcade.draw_text(
        wave_text,
        SCREEN_WIDTH - 120,
        10,
        wave_color,
        font_size=20,
        font_name="Kenney Pixel",
        anchor_x="left"
    )

def draw_coin_count(player_coins):
    arcade.draw_text(f"Coins: {player_coins}", SCREEN_WIDTH - 100, 30, arcade.color.GOLD, 18)
import arcade
from src.core.constants import SCREEN_WIDTH, SCREEN_HEIGHT

def draw_wave_message(message, alpha):
    if not message:
        return

    fade_color = (*arcade.color.LIGHT_GREEN[:3], alpha)
    arcade.draw_text(
        message,
        SCREEN_WIDTH / 2,
        SCREEN_HEIGHT / 2,
        fade_color,
        font_size=24,
        anchor_x="center",
        font_name="Kenney Pixel"
    )

def fade_wave_message_alpha(current_timer, total_time=3.0):
    return max(0, int(255 * (current_timer / total_time)))

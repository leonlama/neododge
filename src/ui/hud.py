import arcade
from src.core.constants import SCREEN_WIDTH, SCREEN_HEIGHT

def draw_score(score):
    """Draw the player's score"""
    arcade.draw_text(
        f"Score: {int(score)}",
        SCREEN_WIDTH - 20,
        SCREEN_HEIGHT - 30,
        arcade.color.WHITE,
        16,
        anchor_x="right"
    )

def draw_pickup_texts(pickup_texts):
    """Draw floating pickup text animations"""
    for text, x, y, timer in pickup_texts:
        # Calculate alpha based on remaining time
        alpha = min(255, int(timer * 255 * 2))
        arcade.draw_text(
            text,
            x, y,
            arcade.color.WHITE + (alpha,),
            14,
            anchor_x="center"
        )

def draw_wave_timer(current_time, total_time):
    """Draw the wave timer"""
    # Calculate remaining time
    remaining = total_time - current_time

    # Draw timer text
    arcade.draw_text(
        f"Time: {int(remaining)}",
        SCREEN_WIDTH - 20,
        SCREEN_HEIGHT - 60,
        arcade.color.WHITE,
        14,
        anchor_x="right"
    )

def draw_wave_number(wave_number):
    """Draw the current wave number"""
    arcade.draw_text(
        f"Wave {wave_number}",
        SCREEN_WIDTH - 20,
        SCREEN_HEIGHT - 90,
        arcade.color.WHITE,
        16,
        anchor_x="right"
    )

def draw_coin_count(coins):
    """Draw the player's coin count"""
    arcade.draw_text(
        f"Coins: {coins}",
        20,
        SCREEN_HEIGHT - 30,
        arcade.color.GOLD,
        16,
        anchor_x="left"
    )

def draw_player_health(player):
    """Draw the player's health hearts"""
    # Draw heart containers
    heart_spacing = 40
    heart_y = SCREEN_HEIGHT - 70
    heart_scale = 0.5

    # Draw current hearts as text (simpler)
    arcade.draw_text(
        f"Health: {player.current_hearts:.1f} / {player.max_slots}",
        20,
        heart_y,
        arcade.color.RED,
        16,
        anchor_x="left"
    )

def draw_active_orbs(player):
    """Draw the player's active orb effects"""
    if not hasattr(player, "active_orbs") or not player.active_orbs:
        return

    # Draw active effects as text
    arcade.draw_text(
        "Active Effects:",
        20,
        SCREEN_HEIGHT - 100,
        arcade.color.WHITE,
        14,
        anchor_x="left"
    )

    for i, (orb_type, time_left) in enumerate(player.active_orbs):
        arcade.draw_text(
            f"{orb_type}: {time_left:.1f}s",
            20,
            SCREEN_HEIGHT - 120 - i * 20,
            arcade.color.LIGHT_BLUE,
            12,
            anchor_x="left"
        )

def draw_wave_message(message, animation=None):
    """Draw wave message"""
    if not message:
        return

    # Draw simple centered message
    arcade.draw_text(
        message,
        SCREEN_WIDTH // 2,
        SCREEN_HEIGHT // 2,
        arcade.color.WHITE,
        36,
        anchor_x="center",
        anchor_y="center"
    )
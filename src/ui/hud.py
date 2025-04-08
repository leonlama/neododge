﻿import arcade
from src.core.constants import SCREEN_WIDTH, SCREEN_HEIGHT, HUD_MARGIN
from src.skins.skin_manager import skin_manager

def draw_score(score):
    arcade.draw_text(
        f"Score: {int(score)}", 
        HUD_MARGIN + 5, 
        SCREEN_HEIGHT - 80, 
        arcade.color.WHITE, 
        18,  # Increased font size
        font_name="Kenney Pixel"
    )

def draw_pickup_texts(pickup_texts):
    for text, x, y, _ in pickup_texts:
        arcade.draw_text(
            text, 
            x, 
            y + 20, 
            arcade.color.WHITE, 
            16,  # Increased font size
            anchor_x="center", 
            font_name="Kenney Pixel"
        )

def draw_wave_timer(wave_timer, wave_duration):
    time_left = max(0, int(wave_duration - wave_timer))
    arcade.draw_text(
        f"⏱ {time_left}s left", 
        SCREEN_WIDTH // 2, 
        SCREEN_HEIGHT - 55, 
        arcade.color.LIGHT_GRAY, 
        16,  # Increased font size
        anchor_x="center", 
        font_name="Kenney Pixel"
    )

def draw_wave_number(current_wave):
    color = arcade.color.GOLD if current_wave % 5 == 0 else arcade.color.LIGHT_GREEN
    arcade.draw_text(
        f"Wave {current_wave}",
        SCREEN_WIDTH // 2,
        SCREEN_HEIGHT - 30,
        color,
        font_size=20,  # Increased font size
        anchor_x="center",
        font_name="Kenney Pixel"
    )

def draw_coin_count(player_coins):
    arcade.draw_text(
        f"Coins: {player_coins}", 
        SCREEN_WIDTH - HUD_MARGIN - 10, 
        HUD_MARGIN + 10, 
        arcade.color.GOLD, 
        18,  # Increased font size
        anchor_x="right", 
        font_name="Kenney Pixel"
    )

def draw_player_health(player):
    """Draw the player's health hearts at top left"""
    heart_scale = 0.04  # Slightly increased scale
    heart_spacing = 32  # Slightly increased spacing
    start_x = HUD_MARGIN + 15
    start_y = SCREEN_HEIGHT - 30

    # Draw empty heart slots
    for i in range(player.max_slots):
        x = start_x + i * heart_spacing
        y = start_y
        arcade.draw_scaled_texture_rectangle(
            x, y, player.heart_textures["gray"], heart_scale
        )

    # Draw filled hearts
    full_hearts = int(player.current_hearts)
    for i in range(full_hearts):
        x = start_x + i * heart_spacing
        y = start_y
        arcade.draw_scaled_texture_rectangle(
            x, y, player.heart_textures["red"], heart_scale
        )

    # Draw partial heart if needed
    fraction = player.current_hearts - full_hearts
    if fraction > 0:
        x = start_x + full_hearts * heart_spacing
        y = start_y
        # Draw partial heart (this is simplified - you might want a better visual)
        arcade.draw_scaled_texture_rectangle(
            x, y, player.heart_textures["red"], heart_scale * fraction
        )

    # Draw gold hearts
    for i in range(player.gold_hearts):
        x = start_x + (player.max_slots + i) * heart_spacing
        y = start_y
        arcade.draw_scaled_texture_rectangle(
            x, y, player.heart_textures["gold"], heart_scale
        )

def draw_active_orbs(player):
    """Draw the active orb effects in the top right corner with stacking"""
    # Group effects by type
    effect_groups = {}

    for orb in player.active_orbs:
        orb_type, time_left = orb

        # Extract base type and value
        if orb_type.startswith("speed_"):
            base_type = "speed"
            value = int(orb_type.split("_")[1])
        elif orb_type.startswith("mult_"):
            base_type = "multiplier"
            value = float(orb_type.split("_")[1])
        else:
            base_type = orb_type
            value = 1

        # Add to group
        if base_type in effect_groups:
            effect_groups[base_type]["value"] += value
            effect_groups[base_type]["time"] = max(effect_groups[base_type]["time"], time_left)
        else:
            effect_groups[base_type] = {"value": value, "time": time_left}

    # Display grouped effects
    spacing = 28  # Increased spacing
    start_x = SCREEN_WIDTH - HUD_MARGIN - 10
    start_y = SCREEN_HEIGHT - 30

    for i, (effect_type, data) in enumerate(effect_groups.items()):
        y = start_y - i * spacing

        # Format display text based on effect type
        if effect_type == "speed":
            display_text = f"⚡ Speed +{data['value']}%"
            color = arcade.color.LIGHT_BLUE
        elif effect_type == "multiplier":
            display_text = f"🔥 Score x{data['value']}"
            color = arcade.color.LIGHT_YELLOW
        elif effect_type == "shield":
            display_text = "🛡️ Shield Active"
            color = arcade.color.LIGHT_GREEN
        elif effect_type == "cooldown":
            display_text = f"⏱️ Cooldown x{data['value']}"
            color = arcade.color.ORCHID
        else:
            display_text = f"{effect_type.title()}"
            color = arcade.color.WHITE

        # Draw effect text with time
        arcade.draw_text(
            f"{display_text} ({int(data['time'])}s)",
            start_x, y,
            color, 16, anchor_x="right", font_name="Kenney Pixel"  # Increased font size
        )

def draw_game_over(score):
    """Draw game over screen"""
    arcade.draw_text(
        "GAME OVER", 
        SCREEN_WIDTH // 2, 
        SCREEN_HEIGHT // 2, 
        arcade.color.RED, 
        36, 
        anchor_x="center", 
        font_name="Kenney Pixel"
    )
    arcade.draw_text(
        f"Final Score: {int(score)}", 
        SCREEN_WIDTH // 2, 
        SCREEN_HEIGHT // 2 - 50, 
        arcade.color.WHITE, 
        24, 
        anchor_x="center", 
        font_name="Kenney Pixel"
    )
    arcade.draw_text(
        "Press ENTER to restart", 
        SCREEN_WIDTH // 2, 
        SCREEN_HEIGHT // 2 - 100, 
        arcade.color.WHITE, 
        18, 
        anchor_x="center", 
        font_name="Kenney Pixel"
    )

def draw_wave_message(message, animation_state):
    """
    Draw an animated wave message that fades in from right and fades out letter by letter

    Args:
        message: The message to display
        animation_state: Dictionary containing animation parameters
            - phase: "fade_in", "hold", or "letter_fade"
            - timer: Current animation timer
            - alpha: Overall message alpha (0-255)
            - letter_positions: List of letter x positions
            - letter_alphas: List of letter alpha values
    """
    if not message or not animation_state:
        return

    phase = animation_state.get("phase", "fade_in")
    alpha = animation_state.get("alpha", 255)
    letter_positions = animation_state.get("letter_positions", [])
    letter_alphas = animation_state.get("letter_alphas", [])

    # Base color (light green)
    base_color = arcade.color.LIGHT_GREEN

    if phase == "fade_in":
        # Fade in the entire message from right
        fade_color = (*base_color[:3], alpha)
        arcade.draw_text(
            message,
            SCREEN_WIDTH / 2 + (255 - alpha) / 2,  # Slide in from right
            SCREEN_HEIGHT / 2,
            fade_color,
            font_size=26,
            anchor_x="center",
            font_name="Kenney Pixel"
        )
    elif phase == "hold":
        # Display the message at full opacity
        arcade.draw_text(
            message,
            SCREEN_WIDTH / 2,
            SCREEN_HEIGHT / 2,
            base_color,
            font_size=26,
            anchor_x="center",
            font_name="Kenney Pixel"
        )
    elif phase == "letter_fade":
        # Draw each letter with its own position and alpha
        for i, (letter, x_pos, alpha) in enumerate(zip(message, letter_positions, letter_alphas)):
            if alpha <= 0:
                continue

            letter_color = (*base_color[:3], alpha)
            arcade.draw_text(
                letter,
                x_pos,
                SCREEN_HEIGHT / 2,
                letter_color,
                font_size=26,
                anchor_x="center",
                font_name="Kenney Pixel"
            )
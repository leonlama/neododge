import arcade
from src.core.constants import SCREEN_WIDTH, SCREEN_HEIGHT, HUD_MARGIN
from src.skins.skin_manager import skin_manager

def draw_score(score):
    arcade.draw_text(
        f"Score: {int(score)}", 
        HUD_MARGIN + 5, 
        SCREEN_HEIGHT - 80, 
        arcade.color.WHITE, 
        16, 
        font_name="Kenney Pixel"
    )

def draw_pickup_texts(pickup_texts):
    for text, x, y, _ in pickup_texts:
        arcade.draw_text(
            text, 
            x, 
            y + 20, 
            arcade.color.WHITE, 
            14, 
            anchor_x="center", 
            font_name="Kenney Pixel"
        )

def draw_wave_timer(wave_timer, wave_duration):
    time_left = max(0, int(wave_timer))
    arcade.draw_text(
        f"⏱ {time_left}s left", 
        SCREEN_WIDTH // 2, 
        SCREEN_HEIGHT - 55, 
        arcade.color.LIGHT_GRAY, 
        14, 
        anchor_x="center", 
        font_name="Kenney Pixel"
    )

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
    color = arcade.color.GOLD if current_wave % 5 == 0 else arcade.color.LIGHT_GREEN
    arcade.draw_text(
        f"Wave {current_wave}",
        SCREEN_WIDTH // 2,
        SCREEN_HEIGHT - 30,
        color,
        font_size=18,
        anchor_x="center",
        font_name="Kenney Pixel"
    )

def draw_coin_count(player_coins):
    arcade.draw_text(
        f"Coins: {player_coins}", 
        SCREEN_WIDTH - HUD_MARGIN - 10, 
        HUD_MARGIN + 10, 
        arcade.color.GOLD, 
        16, 
        anchor_x="right", 
        font_name="Kenney Pixel"
    )

def draw_player_health(player):
    """Draw the player's health hearts at top left"""
    heart_scale = 0.035  # Adjust as needed
    heart_spacing = 30
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
    spacing = 25
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
            color, 14, anchor_x="right", font_name="Kenney Pixel"
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
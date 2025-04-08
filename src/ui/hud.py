import arcade
from src.core.constants import SCREEN_WIDTH, SCREEN_HEIGHT
from src.skins.skin_manager import skin_manager

def draw_hud(player, score, wave_number, wave_timer=None, wave_duration=30, active_effects=None, coins=0):
    """Draw the complete HUD with all elements"""
    # Draw player health (top left)
    draw_player_health(player)

    # Draw score (below health)
    draw_score(score)

    # Draw wave info (top middle)
    draw_wave_info(wave_number, wave_timer, wave_duration)

    # Draw active effects (top right)
    draw_active_effects(active_effects or [])

    # Draw coin count (bottom right)
    draw_coin_count(coins)

def draw_score(score):
    """Draw the player's score"""
    arcade.draw_text(
        f"Score: {int(score)}",
        30, SCREEN_HEIGHT - 70,
        arcade.color.WHITE,
        16,
        font_name="Kenney Pixel"
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
            anchor_x="center",
            font_name="Kenney Pixel"
        )

def draw_wave_info(wave_number, wave_timer=None, wave_duration=30):
    """Draw wave number and timer in the top middle"""
    # Draw wave number
    arcade.draw_text(
        f"Wave {wave_number}",
        SCREEN_WIDTH // 2,
        SCREEN_HEIGHT - 35,
        arcade.color.LIGHT_GREEN,
        18,
        anchor_x="center",
        font_name="Kenney Pixel"
    )

    # Draw wave timer if provided
    if wave_timer is not None:
        time_left = max(0, int(wave_duration - wave_timer))
        arcade.draw_text(
            f"{time_left}s left",
            SCREEN_WIDTH // 2,
            SCREEN_HEIGHT - 65,
            arcade.color.LIGHT_GRAY,
            14,
            anchor_x="center",
            font_name="Kenney Pixel"
        )

def draw_coin_count(coins):
    """Draw the player's coin count"""
    arcade.draw_text(
        f"Coins: {coins}",
        SCREEN_WIDTH - 20,
        30,
        arcade.color.GOLD,
        18,
        anchor_x="right",
        font_name="Kenney Pixel"
    )

def draw_player_health(player):
    """Draw the player's health hearts"""
    if not player:
        return
        
    # Position for the first heart
    start_x = 30
    y = SCREEN_HEIGHT - 40
    spacing = 35  # Space between hearts
    scale = 0.035   # Scale for heart sprites

    # Draw heart containers (gray hearts)
    for i in range(player.max_slots):
        x = start_x + i * spacing
        arcade.draw_scaled_texture_rectangle(
            x, y, 
            player.heart_textures["gray"],
            scale
        )

    # Draw filled hearts (red hearts)
    full_hearts = int(player.current_hearts)
    for i in range(full_hearts):
        x = start_x + i * spacing
        arcade.draw_scaled_texture_rectangle(
            x, y, 
            player.heart_textures["red"],
            scale
        )

    # Draw partial heart if needed
    if player.current_hearts % 1 > 0:
        # Calculate the fraction of the last heart
        fraction = player.current_hearts % 1
        x = start_x + full_hearts * spacing

        # Draw a partial heart (simplified approach)
        arcade.draw_scaled_texture_rectangle(
            x - (1 - fraction) * spacing / 2, y, 
            player.heart_textures["red"],
            scale * fraction, scale
        )
        
    # Draw gold hearts if any
    if player.gold_hearts > 0:
        for i in range(player.gold_hearts):
            x = start_x + (player.max_slots + i) * spacing
            arcade.draw_scaled_texture_rectangle(
                x, y, 
                player.heart_textures["gold"],
                scale
            )

def draw_active_effects(active_effects):
    """Draw active effects in the top right corner"""
    if not active_effects:
        return

    # Position for the first effect
    x = SCREEN_WIDTH - 20
    y = SCREEN_HEIGHT - 35
    line_height = 25

    # Combine similar effects (e.g., multiple speed boosts)
    combined_effects = {}

    for effect in active_effects:
        effect_type = effect.get("type", "unknown")
        effect_value = effect.get("value", 0)

        if effect_type in combined_effects:
            combined_effects[effect_type]["value"] += effect_value
        else:
            combined_effects[effect_type] = {
                "value": effect_value,
                "color": effect.get("color", arcade.color.WHITE),
                "icon": effect.get("icon", "")
            }

    # Draw each combined effect
    for i, (effect_type, effect_data) in enumerate(combined_effects.items()):
        effect_y = y - i * line_height

        # Format the effect text based on type
        if effect_type == "speed":
            text = f"{effect_data['icon']} Speed +{int(effect_data['value'] * 100)}%"
        elif effect_type == "cooldown":
            text = f"{effect_data['icon']} Cooldown -{int(effect_data['value'] * 100)}%"
        elif effect_type == "shield":
            text = f"{effect_data['icon']} Shield Active"
        elif effect_type == "multiplier":
            text = f"{effect_data['icon']} Score x{effect_data['value']:.1f}"
        else:
            text = f"{effect_data['icon']} {effect_type.capitalize()}: {effect_data['value']}"

        arcade.draw_text(
            text,
            x, effect_y,
            effect_data["color"],
            14,
            anchor_x="right",
            font_name="Kenney Pixel"
        )

def draw_active_orbs(player):
    """Draw the player's active orb effects"""
    if not hasattr(player, "active_orbs") or not player.active_orbs:
        return

    # Position for the first effect
    x = SCREEN_WIDTH - 20
    y = SCREEN_HEIGHT - 40
    line_height = 25

    # Draw active effects
    for i, (orb_type, time_left) in enumerate(player.active_orbs):
        # Format the effect name to be more readable
        effect_name = orb_type.replace("_", " ").title()
        
        # Choose color based on effect type
        color = arcade.color.LIGHT_BLUE
        if "speed" in orb_type:
            color = arcade.color.LIGHT_GREEN
        elif "mult" in orb_type:
            color = arcade.color.GOLD
        elif "shield" in orb_type:
            color = arcade.color.LIGHT_CYAN
            
        arcade.draw_text(
            f"{effect_name}: {time_left:.1f}s",
            x,
            y - i * line_height,
            color,
            14,
            anchor_x="right",
            font_name="Kenney Pixel"
        )

def draw_wave_message(message, alpha=255):
    """Draw a centered wave message with the given alpha"""
    if not message:
        return

    # Create color with alpha
    color = (arcade.color.LIGHT_GREEN[0], 
             arcade.color.LIGHT_GREEN[1], 
             arcade.color.LIGHT_GREEN[2], 
             alpha)

    arcade.draw_text(
        message,
        SCREEN_WIDTH // 2,
        SCREEN_HEIGHT // 2,
        color,
        36,
        anchor_x="center",
        anchor_y="center",
        font_name="Kenney Pixel"
    )

def draw_pickup_text(text, x, y, alpha=255):
    """Draw floating pickup text with the given alpha"""
    color = (255, 255, 255, alpha)

    arcade.draw_text(
        text,
        x, y,
        color,
        14,
        anchor_x="center",
        font_name="Kenney Pixel"
    )
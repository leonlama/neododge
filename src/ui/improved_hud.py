import arcade
from src.core.constants import SCREEN_WIDTH, SCREEN_HEIGHT
from src.skins.skin_manager import skin_manager

def draw_hud(player, score, wave_number, wave_timer=None, wave_duration=30, active_effects=None):
    """Draw the complete HUD with all elements"""
    # Draw player health (top left)
    draw_player_health(player)

    # Draw score (below health)
    draw_score(score)

    # Draw wave info (top middle)
    draw_wave_info(wave_number, wave_timer, wave_duration)

    # Draw active effects (top right)
    draw_active_effects(active_effects or {})

    # Draw coin count (bottom right)
    draw_coin_count(player.coins if hasattr(player, 'coins') else 0)

def draw_player_health(player):
    """Draw player health hearts in the top left corner"""
    if not player or not hasattr(player, 'current_hearts') or not hasattr(player, 'max_slots'):
        return

    # Position for the first heart
    start_x = 30
    y = SCREEN_HEIGHT - 40
    scale = 0.035  # Scale for heart sprites
    spacing = 25   # Spacing between hearts

    # Get heart textures
    heart_textures = {}
    heart_textures["gray"] = skin_manager.textures.get("ui/heart_gray")
    heart_textures["red"] = skin_manager.textures.get("ui/heart_red")
    heart_textures["gold"] = skin_manager.textures.get("ui/heart_gold")

    # Draw heart containers (gray hearts)
    for i in range(player.max_slots):
        x = start_x + i * spacing
        arcade.draw_scaled_texture_rectangle(
            x, y, 
            heart_textures["gray"],
            scale
        )

    # Draw filled hearts (red hearts)
    full_hearts = int(player.current_hearts)
    for i in range(full_hearts):
        x = start_x + i * spacing
        arcade.draw_scaled_texture_rectangle(
            x, y, 
            heart_textures["red"],
            scale
        )

    # Draw partial heart if needed
    if player.current_hearts % 1 > 0:
        # Calculate the fraction of the last heart
        fraction = player.current_hearts % 1
        x = start_x + full_hearts * spacing

        # Draw a partial heart
        arcade.draw_scaled_texture_rectangle(
            x, y, 
            heart_textures["red"],
            scale * fraction, scale
        )

    # Draw gold hearts if player has any
    if hasattr(player, 'gold_hearts') and player.gold_hearts > 0:
        # Position gold hearts after regular hearts
        gold_start_x = start_x + (player.max_slots + 0.5) * spacing

        for i in range(player.gold_hearts):
            x = gold_start_x + i * spacing
            arcade.draw_scaled_texture_rectangle(
                x, y, 
                heart_textures["gold"],
                scale
            )

def draw_score(score):
    """Draw the player's score"""
    arcade.draw_text(
        f"Score: {int(score)}",
        30, SCREEN_HEIGHT - 70,
        arcade.color.WHITE,
        16,
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

def draw_active_effects(active_effects):
    """Draw active effects in the top right corner"""
    if not active_effects:
        return

    # Starting position
    x = SCREEN_WIDTH - 20
    y = SCREEN_HEIGHT - 40
    spacing = 25  # Spacing between effects

    # Combine similar effects (e.g., multiple speed boosts)
    combined_effects = {}
    for effect_name, effect_data in active_effects.items():
        base_type = effect_name.split('_')[0]  # Extract base type (speed, shield, etc.)

        if base_type not in combined_effects:
            combined_effects[base_type] = {
                'value': 0,
                'color': effect_data.get('color', arcade.color.WHITE),
                'is_percentage': effect_data.get('is_percentage', False)
            }

        # Add the effect value
        combined_effects[base_type]['value'] += effect_data.get('value', 0)

    # Draw each combined effect
    for i, (effect_type, effect_data) in enumerate(combined_effects.items()):
        effect_y = y - i * spacing

        # Format the effect text
        if effect_data['is_percentage']:
            effect_text = f"{effect_type.capitalize()} +{effect_data['value']}%"
        else:
            effect_text = f"{effect_type.capitalize()} +{effect_data['value']}"

        arcade.draw_text(
            effect_text,
            x, effect_y,
            effect_data['color'],
            16,
            anchor_x="right",
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

def draw_pickup_texts(pickup_texts):
    """Draw floating pickup text animations"""
    for text, x, y, timer in pickup_texts:
        # Calculate alpha based on remaining time
        alpha = min(255, int(timer * 255 * 2))

        # Draw the text
        arcade.draw_text(
            text,
            x, y,
            arcade.color.WHITE + (alpha,),
            14,
            anchor_x="center",
            font_name="Kenney Pixel"
        )
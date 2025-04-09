import arcade
from src.core.constants import SCREEN_WIDTH, SCREEN_HEIGHT
from src.skins.skin_manager import skin_manager

def draw_hud(player, score, wave=1, wave_timer=None, heart_textures=None):
    """Draw the HUD with the specified layout."""
    from src.core.constants import SCREEN_WIDTH, SCREEN_HEIGHT

    # Draw hearts at top left
    draw_player_health(player, heart_textures, SCREEN_WIDTH, SCREEN_HEIGHT)

    # Draw score below hearts
    draw_score(score)

    # Draw wave info at top middle
    draw_wave_info(wave, wave_timer)

    # Draw active effects at top right
    if hasattr(player, 'active_effects'):
        draw_active_effects(player.active_effects)

    # Draw coin count at bottom right
    coins = getattr(player, 'coins', 0)
    draw_coin_count(coins)

def draw_player_health(player, heart_textures=None, screen_width=800, screen_height=600):
    """Draw player health hearts at top left."""
    from src.core.constants import MAX_HEARTS

    # Use provided textures or create fallbacks
    if not heart_textures or not heart_textures.get('red') or not heart_textures.get('gray'):
        heart_red = arcade.make_soft_circle_texture(30, arcade.color.RED)
        heart_gray = arcade.make_soft_circle_texture(30, arcade.color.GRAY)
    else:
        heart_red = heart_textures['red']
        heart_gray = heart_textures['gray']

    # Draw hearts
    heart_size = 20  # Smaller heart size
    heart_spacing = 5  # Smaller spacing
    start_x = 20 + heart_size // 2  # Left margin
    start_y = screen_height - 30  # Top margin

    for i in range(MAX_HEARTS):
        x = start_x + i * (heart_size + heart_spacing)
        y = start_y

        # Draw filled or empty heart
        if i < player.current_hearts:
            arcade.draw_scaled_texture_rectangle(
                center_x=x,
                center_y=y,
                texture=heart_red,
                scale=heart_size / 30.0  # Scale based on texture size
            )
        else:
            arcade.draw_scaled_texture_rectangle(
                center_x=x,
                center_y=y,
                texture=heart_gray,
                scale=heart_size / 30.0  # Scale based on texture size
            )

def draw_score(score):
    """Draw score at specified position."""
    from src.core.constants import SCREEN_HEIGHT

    arcade.draw_text(
        f"Score: {int(score)}",
        20, SCREEN_HEIGHT - 60,  # Position below hearts
        arcade.color.WHITE,
        16,
        anchor_x="left"
    )

def draw_wave_info(wave, wave_timer):
    """Draw wave info at top middle."""
    from src.core.constants import SCREEN_WIDTH, SCREEN_HEIGHT

    # Draw wave number
    arcade.draw_text(
        f"Wave {wave}",
        SCREEN_WIDTH // 2, SCREEN_HEIGHT - 30,
        arcade.color.GREEN,
        24,
        anchor_x="center"
    )

    # Draw wave timer if available
    if wave_timer is not None:
        arcade.draw_text(
            f"{int(wave_timer)}s",
            SCREEN_WIDTH // 2, SCREEN_HEIGHT - 60,
            arcade.color.WHITE,
            16,
            anchor_x="center"
        )

def draw_active_effects(active_effects):
    """Draw active effects at top right, combining similar effects."""
    from src.core.constants import SCREEN_WIDTH, SCREEN_HEIGHT

    # Aggregate effects by type
    aggregated_effects = {}

    for effect_id, effect_data in active_effects.items():
        if effect_data.get('active', False):
            # Get the base effect type
            effect_type = effect_data.get('type', effect_id.split('_')[0])

            if effect_type not in aggregated_effects:
                aggregated_effects[effect_type] = 0

            # Add the effect value
            aggregated_effects[effect_type] += effect_data.get('value', 0)

    # Draw aggregated effects
    y_offset = 0
    for effect_type, total_value in aggregated_effects.items():
        # Determine color based on effect type
        if effect_type == 'speed':
            color = arcade.color.YELLOW
            display_name = "Speed"
        elif effect_type == 'shield':
            color = arcade.color.BLUE
            display_name = "Shield"
        elif effect_type == 'multiplier':
            color = arcade.color.GREEN
            display_name = "Score Mult"
        elif effect_type == 'cooldown':
            color = arcade.color.PURPLE
            display_name = "Dash CD"
        else:
            color = arcade.color.WHITE
            display_name = effect_type.replace('_', ' ').title()

        # Format effect text
        if total_value > 0:
            text = f"{display_name}: +{int(total_value)}%"
        else:
            text = f"{display_name}: {int(total_value)}%"

        # Draw effect text
        arcade.draw_text(
            text,
            SCREEN_WIDTH - 20, SCREEN_HEIGHT - 30 - y_offset,
            color,
            16,
            anchor_x="right"
        )

        y_offset += 25

def draw_coin_count(coins):
    """Draw coin count at bottom right."""
    from src.core.constants import SCREEN_WIDTH

    arcade.draw_text(
        f"Coins: {coins}",
        SCREEN_WIDTH - 20, 30,
        arcade.color.GOLD,
        18,
        anchor_x="right"
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
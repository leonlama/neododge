import arcade
from src.core.constants import SCREEN_WIDTH, SCREEN_HEIGHT
from src.skins.skin_manager import skin_manager

def draw_hud(player, score, wave=1, wave_timer=None, heart_textures=None):
    """Draw the full HUD layout with a clean roguelike feel."""
    player.draw_hearts()
    draw_score(score)
    draw_wave_info(wave, wave_timer)
    draw_coin_count(getattr(player, 'coins', 0))
    
    if hasattr(player, 'status_effects'):
        draw_active_effects(player.status_effects.effects)

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
    heart_size = 1  # Smaller heart size
    heart_spacing = 18  # Smaller spacing
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
        20, SCREEN_HEIGHT - 90,  # Moved down from 60 to 90
        arcade.color.WHITE,
        15,
        font_name="Kenney Pixel Square",
        bold=True,
        anchor_x="left"
    )

def draw_wave_info(wave, wave_timer):
    arcade.draw_text(
        f"WAVE {wave}",
        SCREEN_WIDTH // 2, SCREEN_HEIGHT - 40,
        arcade.color.LIME_GREEN,
        16,
        anchor_x="center",
        font_name="Kenney Mini Square"
    )

    if wave_timer is not None:
        arcade.draw_text(
            f"{int(wave_timer)}s",
            SCREEN_WIDTH // 2, SCREEN_HEIGHT - 70,
            arcade.color.LIGHT_GRAY,
            18,
            anchor_x="center",
            font_name="Kenney Pixel"
        )

def draw_active_effects(active_effects):
    """Draw buff/debuff effects in a clean top-right layout."""
    from src.core.constants import SCREEN_WIDTH, SCREEN_HEIGHT

    # Group by effect type
    aggregated = {}

    for effect_id, effect in active_effects.items():
        if not effect.get('active', False):
            continue

        effect_type = effect.get('type', effect_id.split('_')[0])
        value = effect.get('value', 0)
        icon = effect.get('icon', f"ui/effects/{effect_type}")
        color = effect.get('color', arcade.color.WHITE)

        if effect_type not in aggregated:
            aggregated[effect_type] = {
                "value": value,
                "icon": icon,
                "color": color
            }
        else:
            aggregated[effect_type]["value"] += value

    # Sort for consistent ordering
    sorted_effects = sorted(aggregated.items())

    # UI constants
    x_base = SCREEN_WIDTH - 160
    y_start = SCREEN_HEIGHT - 40
    icon_size = 24
    spacing = 32

    for idx, (effect_type, data) in enumerate(sorted_effects):
        y = y_start - idx * spacing
        display_name = effect_type.replace("_", " ").title()
        value_text = f"+{int(data['value'])}%" if data["value"] > 0 else f"{int(data['value'])}%"
        # Make sure we're not passing "ui" twice in the path
        icon_path = data["icon"]
        if icon_path.startswith("ui/"):
            # Extract the part after "ui/"
            icon_path = icon_path[3:]
        
        # Use preloaded textures from status_effects manager
        effect_type = effect_type.lower()  # Ensure lowercase key match
        from src.skins.skin_manager import skin_manager

        icon_path = f"effects/{effect_type}"

        # Ensure the texture is loaded
        if not skin_manager.has_texture("ui", icon_path):
            texture_path = f"assets/skins/default/ui/{icon_path}.png"
            try:
                skin_manager.load_texture("ui", icon_path, texture_path)
                print(f"✅ Loaded texture: ui/{icon_path}")
            except FileNotFoundError:
                print(f"❌ Texture file not found: {texture_path}")

        # Get icon (may still be None)
        icon = skin_manager.get_texture("ui", icon_path)

        # Draw icon
        if icon:
            arcade.draw_scaled_texture_rectangle(
                x_base, y + icon_size // 2,
                icon,
                scale=icon_size / icon.width
            )
        else:
            print(f"⚠️ Missing icon for {effect_type}, skipping texture draw.")

        # Draw text
        arcade.draw_text(
            f"{display_name}: {value_text}",
            x_base + icon_size + 10, y + 5,
            data["color"],
            font_size=14,
            font_name="Kenney Pixel"
        )

def draw_coin_count(coins):
    """Draw coin count at bottom right."""
    from src.core.constants import SCREEN_WIDTH

    arcade.draw_text(
        f"Coins: {coins}",
        SCREEN_WIDTH - 30, 30,
        arcade.color.GOLD,
        14,
        anchor_x="right",
        font_name="Kenney Rocket"
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

# Print available textures once at game start
print("✅ Available UI textures:", skin_manager.textures.get("ui", {}).keys())
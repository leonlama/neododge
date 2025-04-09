import arcade
from src.core.constants import SCREEN_WIDTH, SCREEN_HEIGHT
from src.entities.player.player import Player
from src.entities.player.status_effects import StatusEffectManager


def draw_wave_info(wave, wave_timer=None, enemies_left=None):
    # Wave title
    arcade.draw_text(
        f"WAVE {wave}",
        SCREEN_WIDTH // 2, SCREEN_HEIGHT - 40,
        arcade.color.LIME_GREEN,
        16,
        anchor_x="center",
        font_name="Kenney Mini Square"
    )

    # Enemies left
    if enemies_left is not None:
        arcade.draw_text(
            f"{enemies_left} enemies left",
            SCREEN_WIDTH // 2, SCREEN_HEIGHT - 65,
            arcade.color.LIGHT_GRAY,
            14,
            anchor_x="center",
            font_name="Kenney Pixel"
        )

    # Optional timer
    if wave_timer is not None:
        arcade.draw_text(
            f"{int(wave_timer)}s",
            SCREEN_WIDTH // 2, SCREEN_HEIGHT - 85,
            arcade.color.LIGHT_GRAY,
            18,
            anchor_x="center",
            font_name="Kenney Pixel"
        )


def draw_player_health(player, heart_textures):
    """Draw player's hearts in the top-left corner."""
    margin = 20
    heart_size = 32
    x = margin
    y = SCREEN_HEIGHT - margin - heart_size

    # Draw full hearts
    for i in range(player.current_hearts):
        arcade.draw_texture_rectangle(x + i * (heart_size + 5), y, heart_size, heart_size, heart_textures["red"])

    # Draw empty slots (gray hearts)
    for i in range(player.max_slots):
        if i >= player.current_hearts:
            arcade.draw_texture_rectangle(x + i * (heart_size + 5), y, heart_size, heart_size, heart_textures["gray"])

    # Draw overhearts (gold)
    for i in range(player.golden_overhearts):
        arcade.draw_texture_rectangle(x + (player.max_slots + i) * (heart_size + 5), y, heart_size, heart_size, heart_textures["gold"])


def draw_score(score):
    arcade.draw_text(
        f"Score: {score}",
        20, SCREEN_HEIGHT - 75,
        arcade.color.LIGHT_GRAY,
        14,
        font_name="Kenney Pixel"
    )


def draw_active_effects(status_effects: StatusEffectManager):
    effects = status_effects.get_active_effects_summary()
    x = SCREEN_WIDTH - 180
    y = SCREEN_HEIGHT - 30
    spacing = 20

    # Draw count
    arcade.draw_text(
        f"{len(effects)} effects",
        x, y,
        arcade.color.GRAY,
        12,
        font_name="Kenney Pixel"
    )
    y -= spacing

    for effect_name, value in effects.items():
        color = get_effect_color(effect_name)
        arcade.draw_text(
            f"{effect_name.capitalize()}: +{int(value * 100)}%",
            x, y,
            color,
            13,
            font_name="Kenney Pixel"
        )
        y -= spacing


def draw_coins(coin_count):
    text = f"Coins: {coin_count}"
    arcade.draw_text(
        text,
        SCREEN_WIDTH - 120, 20,
        arcade.color.GOLD,
        14,
        font_name="Kenney Pixel"
    )


def get_effect_color(effect_name: str):
    return {
        "speed": arcade.color.BLUE,
        "multiplier": arcade.color.ORANGE,
        "cooldown": arcade.color.RED,
        "hitbox": arcade.color.WHITE,
        "vision": arcade.color.GRAY,
        "shield": arcade.color.GREEN
    }.get(effect_name, arcade.color.LIGHT_GRAY)


def draw_coin_count(coin_count: int):
    """Draw the current coin count in the bottom-right corner."""
    text = f"Coins: {coin_count}"
    margin = 20
    x = 800 - margin
    y = margin + 10
    arcade.draw_text(
        text,
        x,
        y,
        arcade.color.YELLOW,
        16,
        anchor_x="right",
        anchor_y="bottom",
        font_name="Kenney Pixel"  # or any font you're using
    )

def draw_wave_message(text: str, alpha: float):
    """Draw the wave message in the center top with a given alpha."""
    label = arcade.Text(
        text,
        start_x=arcade.get_window().width // 2,
        start_y=arcade.get_window().height - 100,
        color=arcade.color.GREEN + (int(alpha * 255),),  # Add alpha to the RGB color
        font_size=28,
        anchor_x="center",
        anchor_y="center",
        font_name="Kenney Mini Square"
    )
    label.draw()

def draw_pickup_texts(pickup_texts: list):
    """Draw pickup text notifications."""
    from src.ui.pickup_text import PickupText  # if not already present
    
    for text_obj in pickup_texts:
        if isinstance(text_obj, PickupText):
            text_obj.draw()

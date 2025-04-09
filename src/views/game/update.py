from src.views.game.coin_logic import (
    spawn_coin, spawn_coins, maybe_spawn_more_coins, 
    check_coin_collection, spawn_wave_reward, update_coins
)
from src.views.game.orb_logic import (
    spawn_orbs, spawn_orb, check_orb_collisions, apply_orb_effect
)
from src.views.game.artifact_logic import update_artifacts

def update_game(delta_time, game_view):
    # Basic logic
    game_view.player.update(delta_time)
    handle_pickups(game_view, delta_time)

    if game_view.wave_manager:
        game_view.wave_manager.update(delta_time)

    if hasattr(game_view, "update_camera"):
        game_view.update_camera()

    # Coin system
    update_coins(game_view, delta_time)
    check_coin_collection(game_view)
    maybe_spawn_more_coins(game_view)

    # Orb system
    check_orb_collisions(game_view)

    # Artifact system
    update_artifacts(game_view, delta_time)

    # Scoring
    game_view.score += 1 * getattr(game_view, 'score_multiplier', 1) * delta_time


def handle_pickups(game_view, delta_time):
    if hasattr(game_view, 'pickup_texts'):
        for text_obj in game_view.pickup_texts[:]:
            if hasattr(text_obj, 'update'):
                text_obj.update(delta_time)
                if text_obj.alpha <= 0:
                    game_view.pickup_texts.remove(text_obj)
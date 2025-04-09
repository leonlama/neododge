def handle_mouse_targeting(game_view, x, y, held=False):
    if not hasattr(game_view, 'player') or not game_view.player:
        return

    speed_multiplier = 0.8 if held else 1.0
    game_view.player.set_target(x, y, speed_multiplier=speed_multiplier)
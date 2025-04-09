def update_wave_message(game_view, delta_time):
    if hasattr(game_view, 'wave_message_alpha') and game_view.wave_message_alpha > 0:
        game_view.message_timer += delta_time
        if game_view.message_timer >= game_view.message_duration:
            game_view.wave_message_alpha -= 5
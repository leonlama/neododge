def update_wave_message(game_view, delta_time):
    # Update wave message timer
    if hasattr(game_view, 'wave_message_timer') and game_view.wave_message_timer > 0:
        game_view.wave_message_timer -= delta_time
        
        # Display for 2.5 seconds, then fade out for 1 second
        if game_view.wave_message_timer <= 0:
            game_view.wave_message = None
            game_view.wave_message_timer = 0
        elif game_view.wave_message_timer <= 1.0:
            # Fade out during the last second
            fade_percentage = game_view.wave_message_timer / 1.0
            game_view.wave_message_alpha = int(255 * fade_percentage)
    
    # Set up wave message display properties
    if hasattr(game_view, 'wave_message') and game_view.wave_message:
        if not hasattr(game_view, 'wave_message_font'):
            # Use Kenny Pixel Square font
            game_view.wave_message_font = "kenney_pixel_square"
            game_view.wave_message_alpha = 255
            game_view.wave_message_timer = 3.5  # 2.5s display + 1s fade
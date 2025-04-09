def handle_mouse_targeting(game_view, x, y, held=False):
    """Handles mouse-based movement for the player in the game view."""
    if hasattr(game_view, "camera"):
        try:
            x, y = game_view.camera.mouse_coordinates_to_world(x, y)
        except AttributeError:
            x = x / game_view.camera.scale + game_view.camera.position[0]
            y = y / game_view.camera.scale + game_view.camera.position[1]

    if game_view.player:
        speed_factor = 0.8 if held else 1.0
        game_view.player.set_target(x, y, speed_factor)
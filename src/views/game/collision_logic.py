def check_collisions(game_view):
    if not game_view.player:
        return

    # Check for collisions with enemies
    for enemy in game_view.enemies:
        if game_view.player.collides_with_sprite(enemy):
            game_view.player.take_damage(1)
            if hasattr(enemy, "on_player_hit"):
                enemy.on_player_hit()
            break  # Avoid multi-hit per frame

    # Check for collisions with enemy bullets
    for bullet in game_view.bullets:
        if game_view.player.collides_with_sprite(bullet):
            game_view.player.take_damage(0.5)
            bullet.remove_from_sprite_lists()

def check_orb_collisions(game_view):
    for orb in game_view.orbs[:]:
        if game_view.player.collides_with_sprite(orb):
            orb.apply_effect(game_view.player)
            game_view.pickup_texts.append(
                game_view.create_pickup_text("Buff Collected!", orb.center_x, orb.center_y)
            )
            game_view.orbs.remove(orb)
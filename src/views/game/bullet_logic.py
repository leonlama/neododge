import arcade

def update_enemy_bullets(game_view, delta_time):
        """Update all enemies and their bullets."""
        # Update each enemy
        for enemy in game_view.enemies:
            # Handle enemy bullets
            if hasattr(enemy, 'bullets'):
                # Check for bullet-player collisions
                bullet_hit_list = arcade.check_for_collision_with_list(game_view.player, enemy.bullets)
                for bullet in bullet_hit_list:
                    # Remove the bullet
                    bullet.remove_from_sprite_lists()

                    # Player takes damage
                    if hasattr(game_view.player, 'take_damage'):
                        game_view.player.take_damage()

                        # Play damage sound
                        game_view.play_damage_sound()

                # Update bullets
                enemy.bullets.update()  # Remove delta_time parameter

                # If bullets need delta_time, update each bullet individually
                for bullet in enemy.bullets:
                    if hasattr(bullet, 'update_with_time'):
                        bullet.update_with_time(delta_time)
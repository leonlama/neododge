import random
import arcade
from src.mechanics.artifacts.dash_artifact import DashArtifact

def update_artifacts(game_view, delta_time):
    for artifact in game_view.artifacts:
        if hasattr(artifact, "update"):
            try:
                artifact.update(delta_time)
            except TypeError:
                artifact.update()  # fallback

    if hasattr(game_view, 'artifact_spawn_timer'):
        game_view.artifact_spawn_timer -= delta_time
        if game_view.artifact_spawn_timer <= 0 and not hasattr(game_view, 'dash_artifact'):
            x = random.randint(50, arcade.get_window().width - 50)
            y = random.randint(50, arcade.get_window().height - 50)

            game_view.dash_artifact = DashArtifact(x, y)
            game_view.artifacts.append(game_view.dash_artifact)

            game_view.artifact_spawn_timer = random.uniform(20, 30)
            print("✨ Spawned a dash artifact!")

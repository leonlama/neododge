import arcade
from scripts.skins.skin_manager import skin_manager
from scripts.utils.orb_utils import get_texture_name_from_orb_type
from scripts.utils.resource_helper import resource_path

def apply_skin_to_orb(orb):
    texture_name = get_texture_name_from_orb_type(orb.orb_type)
    orb.texture = skin_manager.get_texture("orbs", texture_name, force_reload=True)
    orb.scale = skin_manager.get_orb_scale()

def apply_skin_to_artifact(artifact, name):
    artifact.texture = skin_manager.get_texture("artifacts", name, force_reload=True)
    artifact.scale = skin_manager.get_artifact_scale()

def apply_skin_toggle_to_game(game_view):
    if not skin_manager.toggle():  # Cycles and returns True if toggled
        print("⚠️ Could not switch skin.")
        return
    
    print(f"🎨 [SkinLogic] Now using skin: {skin_manager.get_selected()}")

    # Update all existing orbs
    for orb in game_view.orbs:
        apply_skin_to_orb(orb)

    # Update all collected artifacts
    for artifact in game_view.player.artifacts:
        name = getattr(artifact, "name", "dash").lower()
        apply_skin_to_artifact(artifact, name)

    # Update any uncollected artifact on field
    if game_view.dash_artifact:
        apply_skin_to_artifact(game_view.dash_artifact, "dash")

def handle_menu_skin_toggle(start_view):
    current = skin_manager.get_selected()
    new_skin = "default" if current == "mdma" else "mdma"
    
    if skin_manager.select(new_skin):
        # Visual feedback
        start_view.skin_change_indicator = 1.0
        # Audio feedback
        arcade.play_sound(arcade.load_sound(
            resource_path("assets/audio/orb_pickup.wav")
        ), volume=0.7)
        return True
    return False

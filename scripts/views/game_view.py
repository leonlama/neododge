import arcade
from scripts.utils.resource_helper import resource_path

class NeododgeGame(arcade.View):
    """
    Main game view for NeoDodge.

    Responsibilities:
    - Handle game logic and rendering
    - Manage player, enemies, orbs, and other game elements
    - Handle user input for gameplay
    """

    def __init__(self):
        super().__init__()
        self.player = None

    def setup(self):
        """Set up the game elements."""
        try:
            print("Setting up game...")

            # Set up player
            from scripts.characters.player import Player
            self.player = Player()
            self.player.center_x = self.window.width / 2
            self.player.center_y = self.window.height / 2

            # Set up other game elements
            self._setup_game_elements()

            # Play game start sound if available
            try:
                start_sound = arcade.load_sound(resource_path("assets/audio/game_start.wav"))
                arcade.play_sound(start_sound)
            except Exception as e:
                print(f"Warning: Could not play game start sound: {e}")

            print("Game setup complete")
        except Exception as e:
            print(f"❌ Error setting up game: {e}")
            import traceback
            traceback.print_exc()

    def apply_skin_toggle(self):
        """
        Toggle between available skin sets and update all game elements.
        """
        try:
            # Toggle the skin
            self.window.skin_manager.toggle_skin()

            # Update all visual elements
            self._update_visual_elements()
        except Exception as e:
            print(f"❌ Error toggling skin: {e}")

    def _update_visual_elements(self):
        """
        Update all visual elements after a skin change.
        """
        # Update dash artifact
        self._update_dash_artifact()

        # Update player elements
        self._update_player_elements()

        # Update orbs
        self._update_orbs()

        # Update enemies and bullets
        self._update_enemies_and_bullets()

        # Update coins
        self._update_coins()

    def _update_dash_artifact(self):
        """Update dash artifact textures."""
        if hasattr(self, 'dash_artifact') and self.dash_artifact:
            if hasattr(self.dash_artifact, 'update_texture'):
                self.dash_artifact.update_texture()

    def _update_player_elements(self):
        """Update player-related visual elements."""
        if hasattr(self, 'player') and self.player:
            # Update hearts
            if hasattr(self.player, 'update_hearts'):
                self.player.update_hearts()

            # Update orb icons
            if hasattr(self.player, 'update_orb_icons'):
                self.player.update_orb_icons()

            # Update artifacts
            if hasattr(self.player, 'artifacts'):
                for artifact in self.player.artifacts:
                    if hasattr(artifact, 'update_texture'):
                        artifact.update_texture()

    def _update_orbs(self):
        """Update orb textures."""
        if hasattr(self, 'orbs'):
            for orb in self.orbs:
                if hasattr(orb, 'update_texture'):
                    orb.update_texture()
                elif hasattr(orb, 'orb_type'):
                    texture_name = self._get_texture_name_from_orb_type(orb.orb_type)
                    orb.texture = self.window.skin_manager.get_texture("orbs", texture_name)
                    orb.scale = self.window.skin_manager.get_scale("orb")

    def _update_enemies_and_bullets(self):
        """Update enemy and bullet textures."""
        if hasattr(self, 'enemies'):
            for enemy in self.enemies:
                if hasattr(enemy, 'update_texture'):
                    enemy.update_texture()

                if hasattr(enemy, 'bullets'):
                    for bullet in enemy.bullets:
                        if hasattr(bullet, 'update_texture'):
                            bullet.update_texture()

    def _update_coins(self):
        """Update coin textures."""
        if hasattr(self, 'coins'):
            for coin in self.coins:
                if hasattr(coin, 'update_texture'):
                    coin.update_texture()

    def _get_texture_name_from_orb_type(self, orb_type):
        """Convert orb type to texture name."""
        # This is a placeholder - implement based on your orb types
        return orb_type.lower()
# scripts/characters/player.py
import arcade

class Player(arcade.Sprite):
    """
    Player character class.

    Responsibilities:
    - Handle player movement
    - Manage player health
    - Handle player abilities
    """

    def __init__(self):
        super().__init__()
        self.texture = arcade.load_texture("assets/skins/default/player/player.png")
        self.scale = 0.5
        self.health = 3
        self.speed = 5
        self.artifacts = []

    def update(self):
        """Update player logic."""
        # Keep player within screen bounds
        if self.left < 0:
            self.left = 0
        elif self.right > arcade.get_window().width:
            self.right = arcade.get_window().width

        if self.bottom < 0:
            self.bottom = 0
        elif self.top > arcade.get_window().height:
            self.top = arcade.get_window().height

    def update_texture(self):
        """Update player texture based on current skin."""
        try:
            window = arcade.get_window()
            if hasattr(window, 'skin_manager'):
                self.texture = window.skin_manager.get_texture("player", "player")
                self.scale = window.skin_manager.get_scale("player")
        except Exception as e:
            print(f"❌ Error updating player texture: {e}")
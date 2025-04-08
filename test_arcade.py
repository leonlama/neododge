import arcade

def test_arcade():
    print("Testing Arcade version:", arcade.__version__)

    # Test texture loading
    try:
        texture = arcade.load_texture("assets/skins/default/player/default.png")
        print("Texture loading works!")
    except Exception as e:
        print("Error loading texture:", e)

    # Test sound loading
    try:
        sound = arcade.load_sound("assets/audio/damage.wav")
        print("Sound loading works!")
    except Exception as e:
        print("Error loading sound:", e)

if __name__ == "__main__":
    test_arcade()

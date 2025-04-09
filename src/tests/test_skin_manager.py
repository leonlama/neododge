from src.skins.skin_manager import skin_manager

def test_missing_texture_returns_none():
    tex = skin_manager.get_texture("ui", "nonexistent")
    assert tex is None

class BaseArtifact:
    def __init__(self):
        self.cooldown = 10.0
        self.active = False

    def apply_effect(self, *args, **kwargs):
        raise NotImplementedError("Subclasses must implement apply_effect.")

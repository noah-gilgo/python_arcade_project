import arcade


class Frame:
    def __init__(self, sprite: arcade.Sprite):
        self.sprite = sprite
        self.age = 0.0

    def increment_age(self, dt: float):
        self.age += dt

    def reset_age(self):
        self.age = 0.0

import arcade
import settings


SPRITE_SCALING = 1.0
MOVEMENT_SPEED = 5
WINDOW_WIDTH = settings.WINDOW_WIDTH
WINDOW_HEIGHT = settings.WINDOW_HEIGHT


class Player(arcade.Sprite):
    """ Player Class """

    def update(self, delta_time: float = 1/60):
        """ Move the player """
        # Move player.
        # Remove these lines if physics engine is moving player.
        self.center_x += self.change_x
        self.center_y += self.change_y

        # Check for out-of-bounds
        if self.left < 0:
            self.left = 0
        elif self.right > WINDOW_WIDTH - 1:
            self.right = WINDOW_WIDTH - 1

        if self.bottom < 0:
            self.bottom = 0
        elif self.top > WINDOW_HEIGHT - 1:
            self.top = WINDOW_HEIGHT - 1


class PlayerCharacter(arcade.Sprite):
    def __init__(self, default_texture, scale: float, center_x: float, center_y: float, angle: float, name: str,
                 max_hp: int, attack: int, defense: int, magic: int):
        super().__init__(default_texture, scale)
        self.center_x = center_x
        self.center_y = center_y
        self.angle = angle
        self.name = name
        self.max_hp = max_hp
        self.hp = max_hp
        self.attack = attack
        self.defense = defense
        self.magic = magic

    def update(self, delta_time: float = 1 / 60, **kwargs):
        """ Helps the player do things.
        :param delta_time: the amount of time in seconds that the player updates
        :param **kwargs:
        """

        pass

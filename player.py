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

import arcade
from arcade import Sprite, Texture
from arcade.examples.sprite_health import sprite_off_screen
from arcade.hitbox import HitBox

import settings


class Bullet(Sprite):
    def __init__(self, path_or_texture: Texture | str, center_x: float = 0.0, center_y: float = 0.0, angle: float = 0.0,
                 scale: float = 1.0, lifetime: float = 10.0, kill_bullet_when_offscreen: bool = True,
                 base_damage: float = 50.0 ,tp_gain = 0.5, element_id: int = 0, targets_multiple_players: bool = False):
        super().__init__(
            path_or_texture=path_or_texture,
            center_x=center_x,
            center_y=center_y,
            angle=angle,
            scale=scale
        )

        self.time = 0.0
        self.lifetime = lifetime
        self.kill_bullet_when_offscreen = kill_bullet_when_offscreen
        self.base_damage = base_damage # The base damage that the bullet should deal to its target.
        self.tp_gain = tp_gain  # The amount of TP gained when the soul grazes the bullet
        self.element_id = element_id # The element ID of the bullet. Defaults to 0
        self.targets_multiple_players = targets_multiple_players # Determines if the bullet should damage multiple players

        self.lower_limit = -self.height
        self.upper_limit = settings.WINDOW_HEIGHT + self.height
        self.left_limit = -self.width
        self.right_limit = settings.WINDOW_WIDTH + self.width

    def update_animation(self, delta_time: float = 1 / 60):
        self.time += delta_time

        # Kills the bullet if it goes offscreen if the bullet is configured to be killed offscreen.
        if self.kill_bullet_when_offscreen:
            if self.top < self.lower_limit or self.bottom > self.upper_limit or self.right < self.left_limit or self.left > self.right_limit:
                self.kill()

        # Kills the bullet if it is on screen for longer than the bullets designated lifetime.
        if self.time > self.lifetime:
            self.kill()

class BlackDiamondBullet(Bullet):
    """
    The black diamond bullet. Used a lot in Chapter 1, primarily by Rudinns but also by enemies like Jevil.
    """
    def __init__(self, center_x: float = 0.0, center_y: float = 0.0, angle: float = 0.0, scale: float = 2.0):
        super().__init__(
            path_or_texture="assets/sprites/bullets/rudinn_diamond.png",
            center_x=center_x,
            center_y=center_y,
            angle=angle,
            scale=scale
        )

        self.initial_center_x = center_x
        self.initial_center_y = center_y

        self.hit_box = HitBox(
            points=[
                (-4.14, -10.0),
                ( 4.14, -10.0),
                (10.0, -4.14),
                (10.0,  4.14),
                ( 4.14, 10.0),
                (-4.14, 10.0),
                (-10.0,  4.14),
                (-10.0, -4.14),
            ]
        )

        self.alpha = 0

    def update_animation(self, delta_time: float = 1 / 60):
        super().update_animation(delta_time)
        if self.alpha < 255:
            self.alpha = min(self.alpha + (delta_time * 512), 255)

        self.center_y = self.center_y - (2 * (self.time ** 2) - 1)

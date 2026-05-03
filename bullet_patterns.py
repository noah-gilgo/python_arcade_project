import random

from bullet_board import BulletBoard
from bullets import Bullet, BlackDiamondBullet
from sprites_and_effects_collection import SpritesAndEffectsCollection


class BulletPattern:
    def __init__(self, sprites_and_effects_collection: SpritesAndEffectsCollection, total_duration: float = 10.0):
        self.sprites_and_effects_collection = sprites_and_effects_collection
        self.total_duration = total_duration

        self.time = 0
        self.bullets_sprite_list = [] # When spawning a bullet, add it to this list so it can be cleaned up later
        self.total_duration = total_duration
        self.is_terminated = False

    def update_animation(self, delta_time: float):
        self.time += delta_time

        if self.time > self.total_duration:
            self.terminate_animation()

    def terminate_animation(self):
        self.is_terminated = True
        for sprite in self.bullets_sprite_list:
            sprite.kill()

    def spawn_bullet(self, bullet: Bullet):
        """
        Add bullets to the bullets sprite list. Also adds the new sprites to the effects sprite list.
        :return: None
        """
        self.bullets_sprite_list.append(bullet)

        self.sprites_and_effects_collection.effects.append(bullet)
        self.sprites_and_effects_collection.bullet_sprites.append(bullet)

    def spawn_bullets(self, bullets: list[Bullet]):
        """
        Add sprites to the bullets sprite list. Also adds the new sprites to the effects sprite list.
        :return: None
        """

        for bullet in bullets:
            self.bullets_sprite_list.append(bullet)

            self.sprites_and_effects_collection.effects.append(bullet)
            self.sprites_and_effects_collection.bullet_sprites.append(bullet)


class RainingDiamondBulletPattern(BulletPattern):
    def __init__(self, sprites_and_effects_collection, bullet_board: BulletBoard, total_duration: float = 20.0,
                 frequency: float = 1.0):
        super().__init__(sprites_and_effects_collection, total_duration)

        self.bullet_board = bullet_board
        self.time_since_last_diamond_spawned = 0.0
        self.diamond_frequency = frequency / 4  # The amount of time in seconds between each diamond spawn

    def update_animation(self, delta_time: float):
        super().update_animation(delta_time)

        self.time_since_last_diamond_spawned += delta_time
        if self.time_since_last_diamond_spawned > self.diamond_frequency:
            bullet = BlackDiamondBullet(
                center_x=random.randint(self.bullet_board.bullet_board_sprite.left, self.bullet_board.bullet_board_sprite.right),
                center_y=self.bullet_board.bullet_board_sprite.top + 20
            )
            self.spawn_bullet(bullet)

            self.time_since_last_diamond_spawned = 0.0

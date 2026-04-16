import random

from bullets import Bullet, BlackDiamondBullet


class BulletPattern:
    def __init__(self, controller, total_duration: float = 10.0):
        self.controller = controller
        self.bullet_board = self.controller.bullet_board
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

        self.controller.effects_list.append(bullet)
        self.controller.effects_sprite_list.append(bullet)

    def spawn_bullets(self, bullets: list[Bullet]):
        """
        Add sprites to the bullets sprite list. Also adds the new sprites to the effects sprite list.
        :return: None
        """

        for bullet in bullets:
            self.bullets_sprite_list.append(bullet)

            self.controller.effects_list.append(bullet)
            self.controller.effects_sprite_list.append(bullet)


class RainingDiamondBulletPattern(BulletPattern):
    def __init__(self, controller):
        super().__init__(controller, 999.0)

        self.time_since_last_diamond_spawned = 0.0
        self.diamond_frequency = 0.5

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

import math

import arcade
from arcade import Sprite, Sound, play_sound, SpriteCircle
from math import sin, cos, tan, atan2

from graphics_objects import MultiSpriteAnimation, AnimatedSprite


class IceShockAnimation(MultiSpriteAnimation):
    def __init__(self, center_x: float, center_y: float):
        self.triangle = (
            (center_x - 45, center_y + 30),
            (center_x + 45, center_y + 30),
            (center_x, center_y - 40)
        )

        self.center_x = center_x
        self.center_y = center_y

        sprites = [
            AnimatedSprite(Sprite(path_or_texture="assets/sprites/effects/snowflake.png", scale=3.0,
                                  center_x=self.triangle[0][0], center_y=self.triangle[0][1], visible=False), 1),
            AnimatedSprite(Sprite(path_or_texture="assets/sprites/effects/snowflake.png", scale=3.0,
                                  center_x=self.triangle[1][0], center_y=self.triangle[1][1], visible=False), 2),
            AnimatedSprite(Sprite(path_or_texture="assets/sprites/effects/snowflake.png", scale=3.0,
                                  center_x=self.triangle[2][0], center_y=self.triangle[2][1], visible=False), 2),
            AnimatedSprite(Sprite(path_or_texture="assets/sprites/effects/snowflake.png", scale=1.2,
                                  center_x=self.triangle[0][0], center_y=self.triangle[0][1], visible=False), 4),
            AnimatedSprite(Sprite(path_or_texture="assets/sprites/effects/snowflake.png", scale=1.2,
                                  center_x=self.triangle[0][0], center_y=self.triangle[0][1], visible=False), 5),
            AnimatedSprite(Sprite(path_or_texture="assets/sprites/effects/snowflake.png", scale=1.2,
                                  center_x=self.triangle[0][0], center_y=self.triangle[0][1], visible=False), 6),
            AnimatedSprite(Sprite(path_or_texture="assets/sprites/effects/snowflake.png", scale=1.2,
                                  center_x=self.triangle[0][0], center_y=self.triangle[0][1], visible=False), 7),
            AnimatedSprite(Sprite(path_or_texture="assets/sprites/effects/snowflake.png", scale=1.2,
                                  center_x=self.triangle[0][0], center_y=self.triangle[0][1], visible=False), 8),
            AnimatedSprite(Sprite(path_or_texture="assets/sprites/effects/snowflake.png", scale=1.2,
                                  center_x=self.triangle[0][0], center_y=self.triangle[0][1], visible=False), 9),
            AnimatedSprite(Sprite(path_or_texture="assets/sprites/effects/snowflake.png", scale=1.2,
                                  center_x=self.triangle[1][0], center_y=self.triangle[1][1], visible=False), 10),
            AnimatedSprite(Sprite(path_or_texture="assets/sprites/effects/snowflake.png", scale=1.2,
                                  center_x=self.triangle[1][0], center_y=self.triangle[1][1], visible=False), 11),
            AnimatedSprite(Sprite(path_or_texture="assets/sprites/effects/snowflake.png", scale=1.2,
                                  center_x=self.triangle[1][0], center_y=self.triangle[1][1], visible=False), 12),
            AnimatedSprite(Sprite(path_or_texture="assets/sprites/effects/snowflake.png", scale=1.2,
                                  center_x=self.triangle[1][0], center_y=self.triangle[1][1], visible=False), 13),
            AnimatedSprite(Sprite(path_or_texture="assets/sprites/effects/snowflake.png", scale=1.2,
                                  center_x=self.triangle[1][0], center_y=self.triangle[1][1], visible=False), 14),
            AnimatedSprite(Sprite(path_or_texture="assets/sprites/effects/snowflake.png", scale=1.2,
                                  center_x=self.triangle[1][0], center_y=self.triangle[1][1], visible=False), 15),
            AnimatedSprite(Sprite(path_or_texture="assets/sprites/effects/snowflake.png", scale=1.2,
                                  center_x=self.triangle[2][0], center_y=self.triangle[2][1], visible=False), 16),
            AnimatedSprite(Sprite(path_or_texture="assets/sprites/effects/snowflake.png", scale=1.2,
                                  center_x=self.triangle[2][0], center_y=self.triangle[2][1], visible=False), 17),
            AnimatedSprite(Sprite(path_or_texture="assets/sprites/effects/snowflake.png", scale=1.2,
                                  center_x=self.triangle[2][0], center_y=self.triangle[2][1], visi5le=False), 18),
            AnimatedSprite(Sprite(path_or_texture="assets/sprites/effects/snowflake.png", scale=1.2,
                                  center_x=self.triangle[2][0], center_y=self.triangle[2][1], visible=False), 19),
            AnimatedSprite(Sprite(path_or_texture="assets/sprites/effects/snowflake.png", scale=1.2,
                                  center_x=self.triangle[2][0], center_y=self.triangle[2][1], visible=False), 20),
            AnimatedSprite(Sprite(path_or_texture="assets/sprites/effects/snowflake.png", scale=1.2,
                                  center_x=self.triangle[2][0], center_y=self.triangle[2][1], visible=False), 21)
        ]

        self.circle_active = False
        self.circle_radius = 30
        self.circle_alpha = 255

        super().__init__(sprites, 2.0)
        self.flag1 = False
        self.flag2 = False
        self.flag3 = False
        self.flag4 = False

        self.iceshock_sound = Sound("assets/audio/magic/snd_icespell.ogg", False)

    def update(self):
        self.time += self.delta_time

        if self.time >= 0.05 and not self.flag1:
            self.sprites[0].sprite.visible = True
            self.flag1 = True
            play_sound(self.iceshock_sound)

        if self.time >= 0.25 and not self.flag2:
            self.sprites[1].sprite.visible = True
            self.flag2 = True

        if self.time >= 0.45 and not self.flag3:
            self.sprites[2].sprite.visible = True
            self.flag3 = True

        if self.time >= 0.9 and not self.flag4:
            self.sprites[0].sprite.visible = False
            self.sprites[1].sprite.visible = False
            self.sprites[2].sprite.visible = False
            sprite_index = 0
            for sprite in self.sprites[3:]:
                sprite.sprite.visible = True
                angle = math.radians(((sprite_index * 60)) % 360)
                sprite_velocity_x = cos(angle)
                sprite_velocity_y = sin(angle)
                sprite.sprite.velocity = (sprite_velocity_x, sprite_velocity_y)
                sprite_index += 1

            self.circle_active = True
            self.flag4 = True

        if self.time > 0.9:
            dt = self.time - 0.8
            sprite_index = 0
            for sprite in self.sprites[3:]:
                center = self.triangle[sprite_index // 6]
                center_x = center[0]
                center_y = center[1]
                sprite.sprite.turn_left(4.0)
                sprite.sprite.update()
                dx = sprite.sprite.center_x - center_x
                dy = sprite.sprite.center_y - center_y
                angle = atan2(dy, dx)
                tangent_x = -dy
                tangent_y = dx
                tangent_length = math.sqrt(tangent_x ** 2 + tangent_y ** 2)
                if tangent_length != 0:
                    tangent_x /= tangent_length
                    tangent_y /= tangent_length
                radial_velocity_x = (cos(angle) * (((1 - (dt/1.5)) ** 2) * 12))
                radial_velocity_y = (sin(angle) * (((1 - (dt/1.5)) ** 2) * 12))
                tangent_velocity_x = tangent_x * 2.5
                tangent_velocity_y = tangent_y * 2.5
                sprite_velocity_x = radial_velocity_x + tangent_velocity_x
                sprite_velocity_y = radial_velocity_y + tangent_velocity_y
                sprite.sprite.velocity = (sprite_velocity_x, sprite_velocity_y)
                sprite.sprite.alpha = max(0, int(255 * (1 - (dt/1.5))))
                sprite_index += 1

        if self.time >= 2.5:
            for sprite in self.sprites:
                sprite.sprite.kill()

    def draw(self):
        if self.circle_active and self.circle_alpha > 0:
            arcade.draw_circle_outline(
                self.center_x,
                self.center_y,
                self.circle_radius,
                (255, 255, 255, self.circle_alpha),
                5
            )

            self.circle_radius += 5
            self.circle_alpha = self.circle_alpha - 16 if self.circle_alpha - 16 > 0 else 0

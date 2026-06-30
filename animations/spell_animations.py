import math

import arcade
from arcade import Sprite, Sound, play_sound
from math import sin, cos, atan2

from arcade.easing import ease_in

import character
from graphics_methods import make_texture_solid_color
from graphics_objects import MultiSpriteAnimation, AnimatedSprite, SingleSpriteAnimation
from sprites_and_effects_collection import SpritesAndEffectsCollection


class IceShockAnimation(MultiSpriteAnimation):
    def __init__(self, target: character.Character = None):
        if target:
            self.target = target

            self.triangle = (
                (target.center_x - 45, target.center_y + 30),
                (target.center_x + 45, target.center_y + 30),
                (target.center_x, target.center_y - 40)
            )

            self.center_x = target.center_x
            self.center_y = target.center_y

            sprites = [
                AnimatedSprite(Sprite(path_or_texture="assets/sprites/effects/snowflake.png", scale=3.0,
                                      center_x=self.triangle[0][0], center_y=self.triangle[0][1], visible=False), 1),
                AnimatedSprite(Sprite(path_or_texture="assets/sprites/effects/snowflake.png", scale=3.0,
                                      center_x=self.triangle[1][0], center_y=self.triangle[1][1], visible=False), 2),
                AnimatedSprite(Sprite(path_or_texture="assets/sprites/effects/snowflake.png", scale=3.0,
                                      center_x=self.triangle[2][0], center_y=self.triangle[2][1], visible=False), 3),
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
                                      center_x=self.triangle[2][0], center_y=self.triangle[2][1], visible=False), 18),
                AnimatedSprite(Sprite(path_or_texture="assets/sprites/effects/snowflake.png", scale=1.2,
                                      center_x=self.triangle[2][0], center_y=self.triangle[2][1], visible=False), 19),
                AnimatedSprite(Sprite(path_or_texture="assets/sprites/effects/snowflake.png", scale=1.2,
                                      center_x=self.triangle[2][0], center_y=self.triangle[2][1], visible=False), 20),
                AnimatedSprite(Sprite(path_or_texture="assets/sprites/effects/snowflake.png", scale=1.2,
                                      center_x=self.triangle[2][0], center_y=self.triangle[2][1], visible=False), 21)
            ]

            super().__init__(sprites, 2.0)

        self.circle_active = False
        self.circle_radius = 30
        self.circle_alpha = 255

        self.flag1 = False
        self.flag2 = False
        self.flag3 = False
        self.flag4 = False

        self.iceshock_sound = Sound("assets/audio/magic/snd_icespell.ogg", False)

        self.total_duration = 2.0

    def update_animation(self, delta_time):
        self.time += delta_time

        if self.time >= 0.05 and not self.flag1:
            self.sprites[0].sprite.visible = True
            self.flag1 = True
            play_sound(self.iceshock_sound)

        if self.time >= 0.15 and not self.flag2:
            self.sprites[1].sprite.visible = True
            self.flag2 = True

        if self.time >= 0.25 and not self.flag3:
            self.sprites[2].sprite.visible = True
            self.flag3 = True

        if self.time >= 0.40 and not self.flag4:
            self.sprites[0].sprite.visible = False
            self.sprites[1].sprite.visible = False
            self.sprites[2].sprite.visible = False
            sprite_index = 0
            for sprite in self.sprites[3:]:
                sprite.sprite.visible = True
                angle = math.radians((sprite_index * 60) % 360)
                sprite_velocity_x = cos(angle)
                sprite_velocity_y = sin(angle)
                sprite.sprite.velocity = (sprite_velocity_x, sprite_velocity_y)
                sprite_index += 1

            self.circle_active = True
            self.flag4 = True

        if self.time > 0.40:
            # dt = self.time # (self.time - 0.4) * 2
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
                radial_velocity_x = (cos(angle) * (((1 - (self.time/1.5)) ** 2) * 12))
                radial_velocity_y = (sin(angle) * (((1 - (self.time/1.5)) ** 2) * 12))
                tangent_velocity_x = tangent_x * 2.5
                tangent_velocity_y = tangent_y * 2.5
                sprite_velocity_x = radial_velocity_x + tangent_velocity_x
                sprite_velocity_y = radial_velocity_y + tangent_velocity_y
                sprite.sprite.velocity = (sprite_velocity_x, sprite_velocity_y)
                sprite.sprite.alpha = max(0, int(255 * (1 - (self.time/1.5))))
                sprite_index += 1

        if self.time >= self.total_duration:
            for sprite in self.sprites:
                sprite.sprite.kill()
            self.terminate_animation()

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
            self.circle_alpha = self.circle_alpha - 18 if self.circle_alpha - 18 > 0 else 0


class FreezeAnimation(SingleSpriteAnimation):
    def __init__(self, target: character.Character):
        super().__init__(
            sprite=target
        )

        self.freeze_texture = make_texture_solid_color(self.sprite.texture)

        self.freeze_sprites = []

        for i in range(2):
            freeze_sprite = Sprite(
                path_or_texture=self.freeze_texture.crop(
                    x=0,
                    y=self.freeze_texture.image.height - 1,
                    width=self.freeze_texture.image.width - 1,
                    height=1
                ),
                center_x=self.sprite.center_x - 5 + (i * 10),
            )
            freeze_sprite.width = self.sprite.width
            freeze_sprite.alpha = 174
            freeze_sprite.bottom = self.sprite.bottom
            self.freeze_sprites.append(freeze_sprite)

        self.total_duration = 1.2

    def update_animation(self, delta_time):
        if self.time < self.total_duration:
            self.time += delta_time

            full_height = self.freeze_texture.image.height
            height = max(int(full_height * (self.time / self.total_duration)), 1)
            y = full_height - height

            for freeze_sprite in self.freeze_sprites:
                freeze_sprite.texture = self.freeze_texture.crop(
                    0,
                    y,
                    self.freeze_texture.image.width - 1,
                    height
                )
                freeze_sprite.height = max(int(self.sprite.height * (self.time / self.total_duration)), 1)
                freeze_sprite.center_y = int(self.sprite.center_y - ((self.sprite.height - freeze_sprite.height) / 2))

    def get_sprites(self):
        return self.freeze_sprites


class FireShockAnimation(MultiSpriteAnimation):
    def __init__(self, target: character.Character = None):
        if target:
            self.target = target
            self.triangle = (
                (target.center_x - 45, target.center_y + 30),
                (target.center_x + 45, target.center_y + 30),
                (target.center_x, target.center_y - 40)
            )

            self.center_x = target.center_x
            self.center_y = target.center_y

            sprites = [
                AnimatedSprite(Sprite(path_or_texture="assets/sprites/effects/spr_firespell_flame.png", scale=3.0,
                                      center_x=self.triangle[0][0], center_y=self.triangle[0][1], visible=False), 4),
                AnimatedSprite(Sprite(path_or_texture="assets/sprites/effects/spr_firespell_flame.png", scale=3.0,
                                      center_x=self.triangle[1][0], center_y=self.triangle[1][1], visible=False), 5),
                AnimatedSprite(Sprite(path_or_texture="assets/sprites/effects/spr_firespell_flame.png", scale=3.0,
                                      center_x=self.triangle[2][0], center_y=self.triangle[2][1], visible=False), 6),
                AnimatedSprite(Sprite(path_or_texture="assets/sprites/effects/spr_firespell_smallflame.png", scale=4.0,
                                      center_x=self.triangle[0][0], center_y=self.triangle[0][1], visible=False), 7),
                AnimatedSprite(Sprite(path_or_texture="assets/sprites/effects/spr_firespell_smallflame.png", scale=4.0,
                                      center_x=self.triangle[0][0], center_y=self.triangle[0][1], visible=False), 8),
                AnimatedSprite(Sprite(path_or_texture="assets/sprites/effects/spr_firespell_smallflame.png", scale=4.0,
                                      center_x=self.triangle[0][0], center_y=self.triangle[0][1], visible=False), 9),
                AnimatedSprite(Sprite(path_or_texture="assets/sprites/effects/spr_firespell_smallflame.png", scale=4.0,
                                      center_x=self.triangle[0][0], center_y=self.triangle[0][1], visible=False), 10),
                AnimatedSprite(Sprite(path_or_texture="assets/sprites/effects/spr_firespell_smallflame.png", scale=4.0,
                                      center_x=self.triangle[0][0], center_y=self.triangle[0][1], visible=False), 11),
                AnimatedSprite(Sprite(path_or_texture="assets/sprites/effects/spr_firespell_smallflame.png", scale=4.0,
                                      center_x=self.triangle[0][0], center_y=self.triangle[0][1], visible=False), 12),
                AnimatedSprite(Sprite(path_or_texture="assets/sprites/effects/spr_firespell_smallflame.png", scale=4.0,
                                      center_x=self.triangle[1][0], center_y=self.triangle[1][1], visible=False), 13),
                AnimatedSprite(Sprite(path_or_texture="assets/sprites/effects/spr_firespell_smallflame.png", scale=4.0,
                                      center_x=self.triangle[1][0], center_y=self.triangle[1][1], visible=False), 14),
                AnimatedSprite(Sprite(path_or_texture="assets/sprites/effects/spr_firespell_smallflame.png", scale=4.0,
                                      center_x=self.triangle[1][0], center_y=self.triangle[1][1], visible=False), 15),
                AnimatedSprite(Sprite(path_or_texture="assets/sprites/effects/spr_firespell_smallflame.png", scale=4.0,
                                      center_x=self.triangle[1][0], center_y=self.triangle[1][1], visible=False), 16),
                AnimatedSprite(Sprite(path_or_texture="assets/sprites/effects/spr_firespell_smallflame.png", scale=4.0,
                                      center_x=self.triangle[1][0], center_y=self.triangle[1][1], visible=False), 17),
                AnimatedSprite(Sprite(path_or_texture="assets/sprites/effects/spr_firespell_smallflame.png", scale=4.0,
                                      center_x=self.triangle[1][0], center_y=self.triangle[1][1], visible=False), 18),
                AnimatedSprite(Sprite(path_or_texture="assets/sprites/effects/spr_firespell_smallflame.png", scale=4.0,
                                      center_x=self.triangle[2][0], center_y=self.triangle[2][1], visible=False), 19),
                AnimatedSprite(Sprite(path_or_texture="assets/sprites/effects/spr_firespell_smallflame.png", scale=4.0,
                                      center_x=self.triangle[2][0], center_y=self.triangle[2][1], visible=False), 20),
                AnimatedSprite(Sprite(path_or_texture="assets/sprites/effects/spr_firespell_smallflame.png", scale=4.0,
                                      center_x=self.triangle[2][0], center_y=self.triangle[2][1], visible=False), 21),
                AnimatedSprite(Sprite(path_or_texture="assets/sprites/effects/spr_firespell_smallflame.png", scale=4.0,
                                      center_x=self.triangle[2][0], center_y=self.triangle[2][1], visible=False), 22),
                AnimatedSprite(Sprite(path_or_texture="assets/sprites/effects/spr_firespell_smallflame.png", scale=4.0,
                                      center_x=self.triangle[2][0], center_y=self.triangle[2][1], visible=False), 23),
                AnimatedSprite(Sprite(path_or_texture="assets/sprites/effects/spr_firespell_smallflame.png", scale=4.0,
                                      center_x=self.triangle[2][0], center_y=self.triangle[2][1], visible=False), 24)
            ]

            super().__init__(sprites, 2.0)

            self.burn_animation = None

        self.circle_active = False
        self.circle_radius = 30
        self.circle_alpha = 255

        self.flag1 = False
        self.flag2 = False
        self.flag3 = False
        self.flag4 = False

        self.fireshock_sound = Sound("assets/audio/magic/snd_firespell.wav", False)

        self.burn_sound = arcade.load_sound("assets/audio/battle/player_character/spells/snd_petrify.wav",
                                       False)

        self.total_duration = 2.0

    def update_animation(self, delta_time):
        self.time += delta_time

        if self.time >= 0.05 and not self.flag1:
            self.sprites[0].sprite.visible = True
            self.flag1 = True
            play_sound(sound=self.fireshock_sound, volume=2.0)

        if self.time >= 0.15 and not self.flag2:
            self.sprites[1].sprite.visible = True
            self.flag2 = True

        if self.time >= 0.25 and not self.flag3:
            self.sprites[2].sprite.visible = True
            self.flag3 = True

        if self.time >= 0.40 and not self.flag4:
            self.sprites[0].sprite.visible = False
            self.sprites[1].sprite.visible = False
            self.sprites[2].sprite.visible = False
            sprite_index = 0
            self.target.set_animation_state("battle_hurt")
            self.burn_sound.play(speed=0.5)  # the speed modifier doesn't do anything for some reason

            for sprite in self.sprites[3:]:
                sprite.sprite.visible = True
                angle = math.radians(((sprite_index * 60) % 360) + 180)
                sprite_velocity_x = cos(angle)
                sprite_velocity_y = sin(angle)
                sprite.sprite.velocity = (sprite_velocity_x, sprite_velocity_y)
                sprite_index += 1
                sprite.sprite.angle = angle
                if sprite.sprite in self.target.sprites_and_effects_collection.effects_sprites:
                    self.target.sprites_and_effects_collection.effects_sprites.remove(sprite.sprite)

            # Spawn burn animation
            self.burn_animation = BurnAnimation(self.target)
            self.sprites = self.burn_animation.get_sprites() + self.sprites

            for sprite in self.sprites[6:]:
                self.target.sprites_and_effects_collection.effects_sprites.append(sprite.sprite)

            self.circle_active = True
            self.flag4 = True

        if self.time > 0.40:
            self.burn_animation.update_animation(delta_time)
            # dt = self.time # (self.time - 0.4) * 2
            sprite_index = 0
            new_alpha = max(0, int(255 * (1 - (ease_in(self.time / 1.5) ** 2))))
            for sprite in self.sprites[6:]:
                center = self.triangle[sprite_index // 6]
                center_x = center[0]
                center_y = center[1]
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
                radial_velocity_x = (cos(angle) * (((1 - (self.time/1.5)) ** 2) * 12))
                radial_velocity_y = (sin(angle) * (((1 - (self.time/1.5)) ** 2) * 12))
                tangent_velocity_x = tangent_x * 2.5
                tangent_velocity_y = tangent_y * 2.5
                sprite_velocity_x = radial_velocity_x + tangent_velocity_x
                sprite_velocity_y = radial_velocity_y + tangent_velocity_y
                sprite.sprite.velocity = (sprite_velocity_x, sprite_velocity_y)
                sprite.sprite.alpha = new_alpha
                sprite_index += 1

                #sprite.sprite.turn_left(3.0)
                sprite.sprite.angle = math.degrees(-angle) - 60

        if self.time >= self.total_duration:
            """
            for sprite in self.sprites:
                if isinstance(sprite, Sprite):
                    sprite.kill()
                else:
                    sprite.sprite.kill()
            """

            self.terminate_animation()

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
            self.circle_alpha = self.circle_alpha - 18 if self.circle_alpha - 18 > 0 else 0

    def terminate_animation(self):
        for sprite in self.sprites[3:]:
            sprite.kill()


class BurnAnimation(SingleSpriteAnimation):
    def __init__(self, target: character.Character):
        super().__init__(
            sprite=target
        )

        self.target = target

        self.burn_texture = make_texture_solid_color(
            texture=self.sprite.texture,
            color=arcade.color.SMOKY_BLACK
        )

        self.burn_sprites = []

        self.burn_sprites.append(target)

        # Darken the target on the first frame of the attack.
        self.sprite.color = arcade.color.TAUPE

        for i in range(2):
            ash_sprite = Sprite(
                path_or_texture=self.burn_texture.crop(
                    x=0,
                    y=self.burn_texture.image.height - 1,
                    width=self.burn_texture.image.width - 1,
                    height=1
                ),
                center_x=self.sprite.center_x - 5 + (i * 10),
            )
            ash_sprite.width = self.sprite.width
            ash_sprite.alpha = 128
            ash_sprite.bottom = self.sprite.bottom
            self.burn_sprites.append(ash_sprite)

        for sprite in self.burn_sprites:
            self.target.sprites_and_effects_collection.effects_sprites.append(sprite)

        self.total_duration = 1.2

    def update_animation(self, delta_time):
        if self.time < self.total_duration:
            self.time += delta_time

            full_height = self.burn_texture.image.height
            height = max(int(full_height * (self.time / self.total_duration)), 1)
            y = full_height - height

            for burn_sprite in self.burn_sprites[1:]:
                burn_sprite.texture = self.burn_texture.crop(
                    0,
                    y,
                    self.burn_texture.image.width - 1,
                    height
                )
                burn_sprite.height = max(int(self.sprite.height * (self.time / self.total_duration)), 1)
                burn_sprite.center_y = int(self.sprite.center_y - ((self.sprite.height - burn_sprite.height) / 2))


    def get_sprites(self):
        return self.burn_sprites

    def terminate_animation(self):
        pass

"""
class HealPrayerAnimation(MultiSpriteAnimation):
    def __init__(self, target: character.Character):
"""

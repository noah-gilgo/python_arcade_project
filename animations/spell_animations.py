import math
import random

import arcade
from arcade import Sprite, Sound, play_sound, Texture
from math import sin, cos, atan2

from arcade.easing import ease_in, ease_out, ease_in_sin, ease_out_sin

import character
import player_character
import settings
import sprites_and_effects_collection
from graphics_methods import make_texture_solid_color
from graphics_objects import MultiSpriteAnimation, AnimatedSprite, SingleSpriteAnimation
from math_methods import ease_in_circ, ease_out_circ
from sprites_and_effects_collection import SpritesAndEffectsCollection
from texture_methods import load_textures_at_filepath_into_texture_array


class IceShockAnimation(MultiSpriteAnimation):
    def __init__(self, caster: character.Character = None, target: character.Character = None,
                 sprites_and_effects_collection: SpritesAndEffectsCollection = None):
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
    def __init__(self, caster: character.Character = None, target: character.Character = None,
                 sprites_and_effects_collection: SpritesAndEffectsCollection = None):
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

        self.total_duration = 2.0

        self.burn_animation_spawned = False

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

            for sprite in self.sprites[3:]:
                sprite.sprite.visible = True
                angle = math.radians(((sprite_index * 60) % 360) + 180)
                sprite_velocity_x = cos(angle)
                sprite_velocity_y = sin(angle)
                sprite.sprite.velocity = (sprite_velocity_x, sprite_velocity_y)
                sprite_index += 1
                sprite.sprite.angle = angle
                """
                if sprite.sprite in self.target.sprites_and_effects_collection.effects_sprites:
                    self.target.sprites_and_effects_collection.effects_sprites.remove(sprite.sprite)
                self.target.sprites_and_effects_collection.effects_sprites.append(sprite.sprite)
                """

            """
            # Spawn burn animation
            if self.target.hp < 0:
                self.burn_animation = BurnAnimation(self.target)
                self.sprites = self.burn_animation.get_sprites() + self.sprites

                for sprite in self.sprites[6:]:
                    self.target.sprites_and_effects_collection.effects_sprites.append(sprite.sprite)

                self.burn_animation_spawned = True
            else:
                print(self.target.hp)
            """

            self.circle_active = True
            self.flag4 = True

        if self.time > 0.40:
            """
            if self.burn_animation_spawned:
                self.burn_animation.update_animation(delta_time)
            """
            sprite_index = 0
            new_alpha = max(0, int(255 * (1 - (ease_in(self.time / 1.5) ** 2))))
            for sprite in self.sprites[3:]:
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
            self.circle_alpha = self.circle_alpha - 12 if self.circle_alpha - 12 > 0 else 0

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
                burn_sprite.height = min(self.sprite.height, max(int(self.sprite.height * (self.time / self.total_duration)), 1))
                burn_sprite.center_y = int(self.sprite.center_y - ((self.sprite.height - burn_sprite.height) / 2))


    def get_sprites(self):
        return self.burn_sprites

    def terminate_animation(self):
        pass


class RudeBusterBeam(Sprite):
    """
    The "wave" sprite that makes up the Rude Buster when Susie casts it.
    """
    def __init__(self, beam_textures: list[Texture], center_x: float = 0.0, center_y: float = 0.0,
                 scale: float = 4.5, angle: float = 0.0):
        """
        :param beam_textures: The textures that the beam sprites cycle through to create the illusion of movement.
        :param center_x: The x coordinate of the center of the beam.
        :param center_y: The y coordinate of the center of the beam.
        :param height: The height of the sprite when spawned.
        :param angle: The angle of the sprite when spawned.
        """
        super().__init__(
            center_x=center_x,
            center_y=center_y,
            angle=angle,
            scale=scale
        )
        for texture in beam_textures:
            self.append_texture(texture)
        self.set_texture(0)
        self.texture_cycle_rate = 0.1 # Amount of time that passes between texture changes
        self.time = 0.0
        self.lifetime = 3.0

        self.number_of_textures = len(self.textures)

    def update_animation(self, delta_time):
        self.time += delta_time
        if self.time > self.lifetime:
            self.kill()
        else:
            current_texture_index = int((self.time // self.texture_cycle_rate) % self.number_of_textures)
            self.set_texture(current_texture_index)


class RudeBusterTrailingBeam(RudeBusterBeam):
    """
    The trailing beam that follows the main beam.
    """
    def __init__(self, beam_textures: list[Texture], center_x: float = 0.0, center_y: float = 0.0,
                 scale: float = 2.5, angle: float = 0.0):
        super().__init__(beam_textures, center_x, center_y, scale, angle)
        self.alpha = 128
        self.scale = 3.0

    def update_animation(self, delta_time):
        super().update_animation(delta_time)
        if self.time > 0.12:
            self.alpha -= 600 * delta_time
            self.scale_y -= 8 * delta_time


class RudeBusterImpactAnimation(MultiSpriteAnimation):
    """
    The Rude Buster sprites created on impact with the target.
    """
    def __init__(self, beam_textures: list[Texture], center_x: float = 0.0, center_y: float = 0.0, spread_multiplier: float = 1.0):
        sprites=[
            RudeBusterBeam(beam_textures, center_x + 50, center_y - 50, 4.0 * spread_multiplier, 45.0),
            RudeBusterBeam(beam_textures, center_x + 50, center_y - 50, 4.0 * spread_multiplier, 45.0),
            RudeBusterBeam(beam_textures, center_x - 50, center_y - 50, 4.0 * spread_multiplier, 135.0),
            RudeBusterBeam(beam_textures, center_x - 50, center_y - 50, 4.0 * spread_multiplier, 135.0),
            RudeBusterBeam(beam_textures, center_x - 50, center_y + 50, 4.0 * spread_multiplier, 225.0),
            RudeBusterBeam(beam_textures, center_x - 50, center_y + 50, 4.0 * spread_multiplier, 225.0),
            RudeBusterBeam(beam_textures, center_x + 50, center_y + 50, 4.0 * spread_multiplier, 315.0),
            RudeBusterBeam(beam_textures, center_x + 50, center_y + 50, 4.0 * spread_multiplier, 315.0)
        ]

        super().__init__(sprites)
        self.sprite_initial_positions = []
        for sprite in self.sprites:
            self.sprite_initial_positions.append([sprite.center_x, sprite.center_y])

        self.total_shrink_duration = 1.5

        self.beam_total_distance_traveled = 50  # The total distance the wave travels before despawning

        # The additional spread granted by the spread multiplier
        self.spread_multiplier = spread_multiplier

    def update_animation(self, delta_time):
        super().update_animation(delta_time)
        if self.time < self.total_shrink_duration:
            sprite_index = 0

            # This has to be calculated a lot for this function
            one_minus_ease_in_circ = (1 - ease_in_circ(self.time / self.total_shrink_duration))

            for sprite in self.sprites:
                if sprite_index < 2 or sprite_index > 5:
                    dx = max(0.1, 1.9 * one_minus_ease_in_circ)
                else:
                    dx = -max(0.1, 1.9 * one_minus_ease_in_circ)
                if sprite_index > 3:
                    dy = max(0.1, 1.9 * one_minus_ease_in_circ)
                else:
                    dy = -max(0.1, 1.9 * one_minus_ease_in_circ)
                if sprite_index % 2 == 0:
                    if dx > 0:
                        dx *= 1.2
                    else:
                        dx *= 1.2
                    if dy > 0:
                        dy *= 1.2
                    else:
                        dy *= 1.2

                dx *= self.spread_multiplier
                dy *= self.spread_multiplier

                sprite.center_x += dx
                sprite.center_y += dy

                one_minus_ease_out_circ = ease_out_circ(self.time / self.total_shrink_duration)

                sprite.scale_x = max(0.1, 5.0 * one_minus_ease_out_circ)
                sprite.alpha = max(1.0, 255 * one_minus_ease_out_circ)
                sprite_index += 1
        else:
            for sprite in self.sprites:
                sprite.kill()


class RudeBusterAnimation(MultiSpriteAnimation):
    def __init__(self, caster: character.Character = None, target: character.Character = None,
                 sprites_and_effects_collection: SpritesAndEffectsCollection = None):
        if caster is not None and target is not None and sprites_and_effects_collection is not None:
            self.caster = caster
            self.target = target
            self.sprites_and_effects_collection = sprites_and_effects_collection

            self.rude_buster_beam_textures = load_textures_at_filepath_into_texture_array(
                folder_path="assets/sprites/effects/rude_buster_beam"
            )
            self.number_of_wave_sprites = 18
            self.trajectory_arc_height = -70

            self.rude_buster_arc_coordinates = self.calculate_parabolic_coordinates_of_rude_buster_beam()

            self.time_for_beam_to_connect_to_target = 0.4  # The time it takes for the beam to reach the target
            self.time_between_each_beam_spawn = self.time_for_beam_to_connect_to_target / self.number_of_wave_sprites
            self.time_since_last_beam_spawn = 0.0
            self.current_arc_coordinate_index = 0

            self.leading_rude_buster_beam = RudeBusterBeam(
                beam_textures=self.rude_buster_beam_textures,
                center_x=self.rude_buster_arc_coordinates[0][0],
                center_y=self.rude_buster_arc_coordinates[0][1],
                angle=self.rude_buster_arc_coordinates[0][2]
            )

            super().__init__(
                sprites=[self.leading_rude_buster_beam]
            )

            self.rude_buster_swing_sound = arcade.load_sound(path="assets/audio/magic/snd_rudebuster_swing.wav")
            self.rude_buster_hit_sound = arcade.load_sound(path="assets/audio/magic/snd_rudebuster_hit.wav")

            self.rude_buster_swing_sound.play()

            self.spell_traveling_to_target = True

            self.rude_buster_impact_animation = None

            # The parent Spell object that created this animation.
            self.parent_spell = None

            # Variables used to control the Confirm button combo behavior.
            self.confirm_not_pressed = True
            self.frames_between_confirm_and_impact = 0

    def update_animation(self, delta_time):
        self.time += delta_time
        self.time_since_last_beam_spawn += delta_time
        if self.current_arc_coordinate_index < self.number_of_wave_sprites:
            # If Rude Buster has not yet impacted the target
            if self.confirm_not_pressed:
                if self.parent_spell.controller.z_pressed:
                    self.confirm_not_pressed = False
            else:
                # Since Deltarune only runs at 30 FPS, this is only fair
                self.frames_between_confirm_and_impact += 30 * delta_time

            if self.time_since_last_beam_spawn > self.time_between_each_beam_spawn:
                self.time_since_last_beam_spawn -= self.time_between_each_beam_spawn
                trailing_beam_sprite = RudeBusterTrailingBeam(
                    beam_textures=self.rude_buster_beam_textures,
                    center_x=self.rude_buster_arc_coordinates[self.current_arc_coordinate_index][0],
                    center_y=self.rude_buster_arc_coordinates[self.current_arc_coordinate_index][1],
                    angle=self.rude_buster_arc_coordinates[self.current_arc_coordinate_index][2]
                )
                self.current_arc_coordinate_index += 1
                if self.current_arc_coordinate_index < self.number_of_wave_sprites:
                    self.leading_rude_buster_beam.center_x = self.rude_buster_arc_coordinates[self.current_arc_coordinate_index][0]
                    self.leading_rude_buster_beam.center_y = self.rude_buster_arc_coordinates[self.current_arc_coordinate_index][1]
                    self.leading_rude_buster_beam.angle = self.rude_buster_arc_coordinates[self.current_arc_coordinate_index][2]
                    self.leading_rude_buster_beam.update_animation(delta_time)
                else:
                    self.leading_rude_buster_beam.kill()
                self.sprites.append(trailing_beam_sprite)
                self.sprites_and_effects_collection.effects_sprites.append(trailing_beam_sprite)
                self.sprites_and_effects_collection.effects.append(trailing_beam_sprite)
        else:
            # If Rude Buster has impacted the target
            if self.spell_traveling_to_target:
                self.frames_between_confirm_and_impact = math.floor(self.frames_between_confirm_and_impact)
                self.spell_traveling_to_target = False
                if self.frames_between_confirm_and_impact >= len(self.parent_spell.damage_addition_amount_list):
                    spread_multiplier = 1.0
                else:
                    spread_multiplier = 1.0 + ((len(self.parent_spell.damage_addition_amount_list) - self.frames_between_confirm_and_impact) / 20)

                if not self.confirm_not_pressed:
                    self.parent_spell.frames_between_confirm_and_impact = self.frames_between_confirm_and_impact
                self.parent_spell.affect_targets_with_spell()
                self.rude_buster_hit_sound.play()
                # Plays the sound a second time over the first time, giving the illusion that it's louder
                if not self.confirm_not_pressed:
                    self.rude_buster_hit_sound.play()
                self.rude_buster_impact_animation = RudeBusterImpactAnimation(
                    beam_textures=self.rude_buster_beam_textures,
                    center_x=self.target.center_x,
                    center_y=self.target.center_y,
                    spread_multiplier=spread_multiplier
                )
                for sprite in self.rude_buster_impact_animation.get_sprites():
                    self.sprites_and_effects_collection.effects_sprites.append(sprite)

                self.sprites_and_effects_collection.effects.append(self.rude_buster_impact_animation)
            else:
                self.rude_buster_impact_animation.update_animation(delta_time)

    def terminate_animation(self):
        for sprite in self.sprites:
            sprite.kill()

        for sprite in self.rude_buster_impact_animation.get_sprites():
            sprite.kill()

        self.sprites_and_effects_collection.effects.remove(self.rude_buster_impact_animation)
        self.sprites_and_effects_collection.effects.remove(self)


    def calculate_parabolic_coordinates_of_rude_buster_beam(self):
        """
        Calculates the coordinates and angles of every pre-impact sprite of the Rude Buster beam.
        :return: A list of all the coordinates for each Rude Buster wave sprite.
        """
        caster_x = self.caster.center_x
        caster_y = self.caster.center_y
        target_x = self.target.center_x
        target_y = self.target.center_y

        # Distance between caster and target along x and y dimensions
        dx = target_x - caster_x
        dy = target_y - caster_y

        # Horizontal angle between caster and target
        theta = math.atan2(dy, dx)

        # Horizontal/vertical displacement of the coordinates based on the spell angle
        cos_theta = math.cos(theta)
        sin_theta = math.sin(theta)

        # Array containing the points to be returned
        points = []
        for i in range(self.number_of_wave_sprites):
            t = i / (self.number_of_wave_sprites - 1)
            y = 4 * self.trajectory_arc_height * t * (1 - t)

            # Local coordinates
            lx = dx * t
            ly = y

            # World coordinates
            wx = caster_x + lx * cos_theta - ly * sin_theta
            wy = caster_y + lx * sin_theta + ly * cos_theta

            # Calculate angle of each rude buster wave
            ldx = dx
            ldy = 4 * self.trajectory_arc_height * (1 - 2 * t)

            tx = ldx * cos_theta - ldy * sin_theta
            ty = ldx * sin_theta + ldy * cos_theta

            angle = 360 - math.degrees(math.atan2(ty, tx))

            points.append([wx, wy, angle])

        return points


class SpinningSnowflake(Sprite):
    """ One of the miniature snowflakes spawned by the SleepMist animation."""
    def __init__(self, texture: Texture, center_x: float, center_y: float,
                 sprites_and_effects_collection: SpritesAndEffectsCollection):
        super().__init__(
            path_or_texture=texture,
            center_x=center_x,
            center_y=center_y,
            scale=0.8
        )

        self.sprites_and_effects_collection = sprites_and_effects_collection

        self.time = 0.0

    def update_animation(self, delta_time: float):
        self.time += delta_time

        self.turn_left(50 * delta_time)

        if self.time > 0.6:
            self.alpha = max(0, int(255 * ease_in((1.0 - self.time) * 2.5)))

        if self.alpha == 0:
            if self in self.sprites_and_effects_collection.effects:
                self.sprites_and_effects_collection.effects.remove(self)
            self.kill()


class SleepMistAnimation(MultiSpriteAnimation):
    def __init__(self, caster: character.Character = None, target: character.Character = None,
                 sprites_and_effects_collection: SpritesAndEffectsCollection = None):
        if caster is not None and target is not None and sprites_and_effects_collection is not None:
            self.caster = caster
            self.target = target
            self.sprites_and_effects_collection = sprites_and_effects_collection

            self.target_initial_x = self.target.center_x
            self.target_initial_y = self.target.center_y

            self.sleep_mist_texture = arcade.load_texture(
                file_path="assets/sprites/effects/sleep_mist.png"
            )

            self.snowflake_texture = arcade.load_texture("assets/sprites/effects/snowflake.png")
            self.snowflake_spawning_attempts = 0
            self.interval_between_snowflake_spawning_attempts = 0.1

            self.sleep_mist_sprites = []
            for i in range(2):
                sleep_mist_sprite = Sprite(
                    path_or_texture=self.sleep_mist_texture,
                    scale=(8.0, 4.0),
                    center_x=self.target.center_x,
                    center_y=self.target.center_y
                )
                sleep_mist_sprite.alpha = 0
                self.sleep_mist_sprites.append(sleep_mist_sprite)
                self.sprites_and_effects_collection.effects.append(sleep_mist_sprite)

            super().__init__(self.sleep_mist_sprites)

            self.mist_duration = 3.5
            self.half_of_mist_duration = self.mist_duration / 2

            self.total_duration = 5.0
            self.radius = 0.0
            self.angle = 0.0  # measured in radians

            # A rectangle measures around the animation. Controls the area in which snowflakes can spawn.
            self.snowflake_min_x = int(self.target_initial_x - 200)
            self.snowflake_max_x = int(self.target_initial_x + 200)

            self.snowflake_min_y = int(self.target_initial_y - 100)
            self.snowflake_max_y = int(self.target_initial_y + 100)

    def update_animation(self, delta_time: float):
        self.time += self.delta_time
        self.angle += self.delta_time * 1.8

        # Randomly spawn snowflakes
        if self.time < 2.0 and self.time // self.interval_between_snowflake_spawning_attempts != self.snowflake_spawning_attempts:
            if random.randint(0, 3) == 0:
                snowflake_center_x = random.randint(self.snowflake_min_x, self.snowflake_max_x)
                snowflake_center_y = random.randint(self.snowflake_min_y, self.snowflake_max_y)
                spinning_snowflake = SpinningSnowflake(
                    texture=self.snowflake_texture,
                    center_x=snowflake_center_x,
                    center_y=snowflake_center_y,
                    sprites_and_effects_collection=self.sprites_and_effects_collection
                )
                self.sprites_and_effects_collection.effects.append(spinning_snowflake)
                self.sprites_and_effects_collection.effects_sprites_2.append(spinning_snowflake)

            self.snowflake_spawning_attempts += 1

        if self.time < self.mist_duration:
            is_odd = True
            for sprite in self.sleep_mist_sprites:
                if self.time < self.half_of_mist_duration:
                    coefficient = (1 - ease_out_circ(self.time / self.half_of_mist_duration))
                    self.radius = 40 * coefficient
                    sprite.alpha = 128 * coefficient
                else:
                    coefficient = (1 - ease_in_sin((self.time - self.half_of_mist_duration) / self.half_of_mist_duration))
                    self.radius = 40 * coefficient
                    sprite.alpha = 128 * coefficient
                if is_odd:
                    angle = self.angle
                else:
                    angle = self.angle + math.pi

                dx = self.radius * math.cos(angle)
                dy = self.radius * math.sin(angle)

                sprite.center_x = self.target_initial_x + dx
                sprite.center_y = self.target_initial_y + dy

                is_odd = not is_odd


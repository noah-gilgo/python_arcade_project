import math
import random

import arcade.color
from arcade import Sprite
from arcade.types import Color

import settings
import texture_methods
from graphics_methods import make_texture_solid_color
from graphics_objects import SingleSpriteAnimation

import math


class ShakeAnimation(SingleSpriteAnimation):
    def __init__(self, sprite: Sprite, angle: float = 0, magnitude: float = 20.0, total_duration: float = 0.4,
                 frequency: float = 0.05):
        super().__init__(
            sprite=sprite,
            total_duration=total_duration
        )
        self.angle = angle
        self.magnitude = magnitude
        self.frequency = frequency
        self.initial_center_x = sprite.center_x
        self.initial_center_y = sprite.center_y
        self.delta_is_positive = True
        self.current_period_duration = 0.0
        self.normalized_horizontal_ratio = math.cos(math.radians(self.angle))
        self.normalized_vertical_ratio = math.sin(math.radians(self.angle))

    def update_animation(self, delta_time):
        if self.time < self.total_duration:
            percentage_of_time_left = 1 - (self.time / self.total_duration)
            if self.current_period_duration > self.frequency:
                sign = 1 if self.delta_is_positive else -1
                self.sprite.center_x = self.initial_center_x + (
                        self.magnitude * self.normalized_horizontal_ratio * sign * percentage_of_time_left)
                self.sprite.center_y = self.initial_center_y + (
                        self.magnitude * self.normalized_vertical_ratio * sign * percentage_of_time_left)
                self.delta_is_positive = not self.delta_is_positive

                self.current_period_duration = 0

            self.time += delta_time
            self.current_period_duration += delta_time
        else:
            self.sprite.center_x = self.initial_center_x
            self.sprite.center_y = self.initial_center_y
            self.terminate_animation()


class FadeInFadeOutColorAnimation(SingleSpriteAnimation):
    def __init__(self, sprite: Sprite, color: Color = arcade.color.WHITE, min_alpha: int = 0, max_alpha: int = 255,
                 total_duration: float = 0.15, is_continuous: bool = False):
        super().__init__(
            sprite=sprite,
            total_duration=total_duration
        )

        self.color = color
        self.min_alpha = min_alpha
        self.max_alpha = max_alpha
        self.alpha_amplitude = self.max_alpha - self.min_alpha

        self.is_continuous = is_continuous

        self.filter_sprite = arcade.Sprite()
        self.filter_sprite.texture = make_texture_solid_color(self.sprite.texture)
        self.filter_sprite.scale = self.sprite.scale
        self.filter_sprite.color = self.color
        self.filter_sprite.alpha = self.min_alpha
        self.inflection_point = self.total_duration / 2

    def update_animation(self, delta_time):
        # TODO: Maybe find a way to optimize this.
        if self.filter_sprite.texture != self.sprite.texture:
            self.filter_sprite.texture = make_texture_solid_color(self.sprite.texture)
        self.time += delta_time

        self.filter_sprite.center_x = self.sprite.center_x
        self.filter_sprite.center_y = self.sprite.center_y

        normalized_time = self.time / self.total_duration

        self.filter_sprite.alpha = self.min_alpha + (self.alpha_amplitude * (-abs((2*normalized_time) - 1) + 1))
        """
        if self.time < self.inflection_point:
            self.filter_sprite.alpha = (self.time * ((2 / self.total_duration) * self.max_alpha)) * self.alpha_ratio
        elif self.inflection_point <= self.time < self.total_duration:
            self.filter_sprite.alpha = (self.time * ((2 / self.total_duration) * self.max_alpha)) * self.alpha_ratio
        """
        if self.time > self.total_duration:
            if self.is_continuous:
                self.time -= self.total_duration
            else:
                self.filter_sprite.kill()
                self.terminate_animation()


class SparkleAnimation(SingleSpriteAnimation):
    def __init__(self, target: Sprite, total_duration: float = 1.0, color: Color = None):
        super().__init__(
            sprite=target,
            total_duration=total_duration
        )

        self.sprite_pack_path = "assets/sprites/effects/heal_spare_particles"

        spare_particle_textures = texture_methods.load_textures_at_filepath_into_texture_array(
            self.sprite_pack_path
        )
        if color is not None:
            colored_spare_particle_textures = []
            for texture in spare_particle_textures:
                colored_spare_particle_textures.append(make_texture_solid_color(texture, color))
            self.spare_particle_textures = colored_spare_particle_textures
        else:
            self.spare_particle_textures = spare_particle_textures

        self.spare_particle_sprite_list = []

        self.spare_particle_distribution = self.sprite.width if self.sprite.width > self.sprite.height else self.sprite.height

        self.spare_particle_min_x = int(self.sprite.center_x - (self.spare_particle_distribution / 1.8))
        self.spare_particle_max_x = int(self.sprite.center_x + (self.spare_particle_distribution / 1.8))

        self.spare_particle_min_y = int(self.sprite.center_y - (self.spare_particle_distribution / 1.8))
        self.spare_particle_max_y = int(self.sprite.center_y + (self.spare_particle_distribution / 1.8))


        for i in range(10):
            sprite = arcade.Sprite()
            sprite.textures = self.spare_particle_textures
            sprite.set_texture(0)
            sprite.center_x = random.randint(self.spare_particle_min_x, self.spare_particle_max_x)
            sprite.center_y = random.randint(self.spare_particle_min_y, self.spare_particle_max_y)
            sprite.scale = random.randint(3, 5)
            sprite.visible = True
            self.spare_particle_sprite_list.append(sprite)

        # Miscellaneous variables so that on_update isn't repeating redundant calculations
        self.particle_sprite_translation_factor = settings.WINDOW_WIDTH / 84

    def update_animation(self, delta_time):
        self.time += delta_time

        # Animate the particle sprites to rotate, drift to the right, and change textures
        texture_index = int(self.time * 6) % len(self.spare_particle_textures)
        for particle_sprite in self.spare_particle_sprite_list:
            particle_sprite.set_texture(texture_index)
            particle_sprite.turn_right(delta_time * 100)
            particle_sprite.center_x += self.time * self.particle_sprite_translation_factor

            particle_sprite.alpha = int((1 - (self.time / self.total_duration)) * 255)
        if self.time > self.total_duration:
            for particle_sprite in self.spare_particle_sprite_list:
                particle_sprite.kill()
            self.terminate_animation()

    def get_sprites(self):
        """
        Get the sprites used by this animation.
        :return: Both of the fading out sprites used by this animation.
        """
        return self.spare_particle_sprite_list

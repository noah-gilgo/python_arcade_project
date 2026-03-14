import math

import arcade.color
from arcade import Sprite
from arcade.types import Color

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
    def __init__(self, sprite: Sprite, color: Color = arcade.color.WHITE, max_alpha: int = 255,
                 total_duration: float = 0.15, is_continuous: bool = False):
        super().__init__(
            sprite=sprite,
            total_duration=total_duration
        )

        self.color = color
        self.max_alpha = max_alpha
        self.is_continuous = is_continuous

        self.filter_sprite = arcade.Sprite()
        self.filter_sprite.texture = make_texture_solid_color(self.sprite.texture)
        self.filter_sprite.scale = self.sprite.scale
        self.filter_sprite.color = self.color
        self.filter_sprite.alpha = 0
        self.inflection_point = self.total_duration / 2

    def update_animation(self, delta_time):
        # This is probably not the most optimal way to do this.
        if self.filter_sprite.texture != self.sprite.texture:
            self.filter_sprite.texture = make_texture_solid_color(self.sprite.texture)
        self.time += delta_time

        self.filter_sprite.center_x = self.sprite.center_x
        self.filter_sprite.center_y = self.sprite.center_y

        if self.time < self.inflection_point:
            self.filter_sprite.alpha += delta_time * ((2 / self.total_duration) * 255)
        elif self.inflection_point <= self.time < self.total_duration:
            self.filter_sprite.alpha -= delta_time * ((2 / self.total_duration) * 255)
        else:
            if self.is_continuous:
                self.time = 0
            else:
                self.filter_sprite.kill()
                self.terminate_animation()

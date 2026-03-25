import arcade
from arcade.types import Color

import settings
from character import Character
from graphics_objects import MultiSpriteAnimation, SingleSpriteAnimation


class NumberBounceAnimation(SingleSpriteAnimation):
    def __init__(self, text = "", color: Color = arcade.color.WHITE, target: Character = None):
        if type(text) == str:
            text_string = text
        else:
            text_string = str(text)

        text_sprite = arcade.create_text_sprite(
            text=text_string,
            color=color,
            font_size=24,
            font_name="Greater Determination DR Damage"
        )

        super().__init__(
            sprite=text_sprite
        )

        self.target = target

        self.sprite.center_x = self.target.center_x + 24
        self.sprite.center_y = self.target.center_y - 24
        self.sprite.scale_x = 2.0
        self.sprite.scale_y = 0.1

        self.time_after_initial_slide = 0

        self.number_has_not_bounced = True
        self.time_after_bounce = 0
        self.total_duration = 3.0
        self.floor = self.target.center_y - 56
        self.number_has_not_bounced_again = True

    def update_animation(self, delta_time: float = settings.FRAMERATE, *args, **kwargs) -> None:
        self.time += delta_time

        # Transition the text from being squashed to being normal-sized.
        if self.time < 0.3:
            if self.sprite.scale_x > 0.9:
                self.sprite.scale_x = max(2.0 - (self.time * 25), 0.9)
            if self.sprite.scale_y < 0.9:
                self.sprite.scale_y = min(self.time * 9, 0.9)
                self.sprite.center_x += 5 * (delta_time * settings.FRAMES_PER_SECOND)
                return

        # Translate the sprite based on provided coordinates.
        if self.sprite.scale_y == 0.9 and self.time < 2.0:
            horizontal_velocity = max(420 - (self.time_after_initial_slide * 30 * settings.FRAMES_PER_SECOND), 0)
            self.sprite.center_x += horizontal_velocity * delta_time
            if self.number_has_not_bounced:
                if self.sprite.center_y > self.floor and self.number_has_not_bounced:
                    vertical_velocity = (10 - (self.time * 50)) * settings.FRAMES_PER_SECOND
                    self.sprite.center_y += vertical_velocity * delta_time
                else:
                    self.number_has_not_bounced = False
            else:
                if self.number_has_not_bounced_again:
                    self.time_after_bounce += delta_time
                    vertical_velocity = (5 - (self.time_after_bounce * 40)) * settings.FRAMES_PER_SECOND
                    self.sprite.center_y += vertical_velocity * delta_time
                    if self.sprite.center_y < self.floor and vertical_velocity < 0:
                        self.number_has_not_bounced_again = False
            self.time_after_initial_slide += delta_time

        if self.time >= 1.3:
            if self.sprite.alpha > 0:
                self.sprite.scale_y += 1.8 * delta_time
                self.sprite.alpha -= 720 * delta_time
                self.sprite.center_y += 180 * delta_time

        if self.time > self.total_duration:
            self.sprite.kill()

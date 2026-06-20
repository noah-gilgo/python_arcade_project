#import math
import random

import arcade.color
from arcade import Sprite, Rect, LRBT, Texture
#from arcade.easing import ease_in_out, ease_in
from arcade.types import Color

import settings
import texture_methods
from graphics_methods import make_texture_solid_color, ease_out
from graphics_objects import SingleSpriteAnimation, MultiSpriteAnimation

import math

from music_player import MusicPlayer
from soul import Soul
from text_box import SpriteTextBox, SpriteTextBoxDialog


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
        self.filter_sprite.center_x = self.sprite.center_x
        self.filter_sprite.center_y = self.sprite.center_y
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
        if self.time > self.total_duration:
            if self.is_continuous:
                self.time -= self.total_duration
            else:
                self.filter_sprite.kill()
                self.terminate_animation()


class SoulFragment(Sprite):
    """
    The fragments of the soul when shattered upon the player's defeat.
    """
    def __init__(self, soul: Soul, soul_fragment_textures: list[Texture]):
        super().__init__(
            center_x=soul.center_x,
            center_y=soul.center_y,
            scale=soul.scale
        )

        self.textures = soul_fragment_textures
        self.set_texture(0)
        self.visible = False

        # Velocity data
        self.dx = random.random() * random.choice([1, -1]) * 10
        self.dy = random.random() * random.choice([1, -1]) * 10

        # Area in which the sprite can exist onscreen before despawning.
        self.lower_limit = -self.height
        self.upper_limit = settings.WINDOW_HEIGHT + self.height
        self.left_limit = -self.width
        self.right_limit = settings.WINDOW_WIDTH + self.width

        # Time data
        self.time = 0

    def update_animation(self, delta_time: float):
        # Change the velocity of the sprite over time.
        self.time += delta_time
        self.set_texture(int(self.time // 0.2) % len(self.textures))

        self.center_x += self.dx
        self.dy -= 0.1
        self.center_y += self.dy

        # Dim the soul fragment if it's been on screen for too long.
        if self.time > 2.0:
            self.alpha = max(0, self.alpha - 12)

        # Kill the sprite if it goes offscreen or if it is not visible.
        if self.alpha == 0:
            self.kill()


class GameOverAnimation(MultiSpriteAnimation):
    """
    The animation that plays when the game ends in player defeat.
    """
    def __init__(self, soul: Soul, music_player: MusicPlayer, sprites_and_effects_collection):
        self.soul = soul
        self.music_player = music_player
        self.sprites_and_effects_collection = sprites_and_effects_collection

        self.soul.graze_sprite.visible = False
        self.soul.visible = False
        self.soul_sprite = Sprite(
            center_x=self.soul.center_x,
            center_y=self.soul.center_y,
            scale=self.soul.scale
        )
        self.soul_sprite.textures = [
            arcade.load_texture("assets/sprites/soul/soul.png"),
            arcade.load_texture("assets/sprites/soul/soul_broken.png")
        ]
        self.soul_sprite.set_texture(0)

        self.game_over_title_sprite = Sprite(
            path_or_texture="assets/sprites/game_over_title.png",
            center_x=settings.WINDOW_CENTER_X,
            center_y=int(settings.WINDOW_HEIGHT * .75),
            scale=4.0
        )
        self.game_over_title_sprite.alpha = 0

        self.soul_fragment_textures = texture_methods.load_textures_at_filepath_into_texture_array(
            "assets/sprites/soul/soul_fragments"
        )

        self.soul_fragments = []
        for i in range(6):
            self.soul_fragments.append(SoulFragment(self.soul, self.soul_fragment_textures))

        super().__init__(
            sprites=[
                self.soul_sprite,
                self.game_over_title_sprite
            ] + self.soul_fragments
        )

        # Sounds used by the animation
        self.soul_break_sound = arcade.load_sound("assets/audio/soul/snd_break1.wav")
        self.soul_shatter_sound = arcade.load_sound("assets/audio/soul/snd_break2.wav")

        # Animation state flags
        self.soul_not_made_visible = True
        self.soul_not_broken = True
        self.soul_not_shattered = True
        self.faint_courage_not_playing = True
        self.text_box_not_loaded = True

        # Death message textbox
        self.death_message_textbox = None

        # Dialog options for the death message text box
        self.death_messages = [
            [
                SpriteTextBoxDialog(
                    text="This is not your fate...!",
                    text_sound_path="assets/audio/dialog/snd_txtral.wav",
                    font_size=48,
                    text_spacing=16,
                    rate_of_text=0.06
                ),
                SpriteTextBoxDialog(
                    text="Please,\ndon't give up!",
                    text_sound_path="assets/audio/dialog/snd_txtral.wav",
                    font_size=48,
                    text_spacing=16,
                    rate_of_text=0.06
                ),
            ],
            [
                SpriteTextBoxDialog(
                    text="Come on, that all you got!?",
                    text_sound_path="assets/audio/dialog/snd_txtsus.wav",
                    font_size=48,
                    text_spacing=16,
                    rate_of_text=0.06
                ),
                SpriteTextBoxDialog(
                    text="Kris, get up...!",
                    text_sound_path="assets/audio/dialog/snd_txtsus.wav",
                    font_size=48,
                    text_spacing=16,
                    rate_of_text=0.06
                ),
            ]
        ]

        self.chosen_death_message = random.choice(self.death_messages)
        self.chosen_death_message_index = 0

    def update_animation(self, delta_time):
        super().update_animation(delta_time)

        if 0 < self.time < 0.8:  # Non-battle soul sprite is made visible
            if self.soul_not_made_visible:
                self.soul_sprite.visible = True
                self.soul_not_made_visible = False
        elif 0.8 <= self.time < 2.0:  # Soul is broken
            if self.soul_not_broken:
                self.soul_sprite.set_texture(1)
                self.soul_break_sound.play()
                self.soul_not_broken = False
        elif 2.0 <= self.time < 4.5:
            if self.soul_not_shattered:
                self.soul_sprite.visible = False
                for soul_fragment in self.soul_fragments:
                    soul_fragment.visible = True
                self.soul_shatter_sound.play()
                self.soul_not_shattered = False
            else:
                if len(self.soul_fragments) > 0:
                    for soul_fragment in self.soul_fragments:
                        soul_fragment.update_animation(delta_time)

        elif 4.5 <= self.time < 7.0:
            if self.faint_courage_not_playing:
                self.music_player.play_sound("faint_courage")
                self.faint_courage_not_playing = False

            if self.game_over_title_sprite.alpha < 255:
                self.game_over_title_sprite.alpha = min(255, self.game_over_title_sprite.alpha + 4)

        elif 7.0 <= self.time:
            if self.text_box_not_loaded:
                self.death_message_textbox = SpriteTextBox(
                    center_x=settings.WINDOW_CENTER_X,
                    center_y=int(settings.WINDOW_HEIGHT * .15),
                    width=700,
                    height=400,
                    sprites_and_effects_collection=self.sprites_and_effects_collection
                )
                self.death_message_textbox.load_dialog(self.chosen_death_message[self.chosen_death_message_index])
                self.chosen_death_message_index += 1
                self.text_box_not_loaded = False
            else:
                self.death_message_textbox.update_animation(delta_time)

    def load_next_dialog_in_text_box(self):
        """
        Loads the next dialog into the text box.
        :return:
        """
        if self.death_message_textbox:
            if self.chosen_death_message_index < len(self.chosen_death_message):
                self.death_message_textbox.load_dialog(self.chosen_death_message[self.chosen_death_message_index])
                self.chosen_death_message_index += 1
            else:
                self.death_message_textbox.clear_dialog()

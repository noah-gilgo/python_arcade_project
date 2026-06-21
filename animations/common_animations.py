#import math
import random

import arcade.color
from arcade import Sprite, Rect, LRBT, Texture, Text
from arcade.easing import ease_in, ease_out
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


class BlurrySoulSprite(Sprite):
    """
    The blurry sprite of the soul used in the DEVICE segments of the game, such as the game over screen.
    """
    def __init__(self):
        super().__init__(
            path_or_texture="assets/sprites/soul/soul_blurry.png",
            scale=4.0,
            center_x=settings.WINDOW_CENTER_X,
            center_y=settings.WINDOW_HEIGHT * .15
        )


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

        self.blurry_soul_sprite = Sprite(
            path_or_texture="assets/sprites/soul/soul_blurry.png",
            scale=4.0,
            center_x=settings.WINDOW_CENTER_X,
            center_y=settings.WINDOW_HEIGHT * .2
        )
        self.blurry_soul_sprite.alpha = 0

        # arcade.create_text_sprite has been oddly buggy for this feature. In the interim while I do not know the cause
        # of this bugginess, I have manually made sprites for the options.
        self.continue_option_sprite = Sprite(
            path_or_texture="assets/sprites/game_over_screen/continue.png",
            center_x=int(settings.WINDOW_WIDTH * .35),
            center_y=int(settings.WINDOW_HEIGHT * .2)
        )

        self.continue_option_sprite.append_texture(arcade.load_texture("assets/sprites/game_over_screen/continue_highlighted.png"))
        self.continue_option_sprite.set_texture(0)
        self.continue_option_sprite.alpha = 0

        self.give_up_option_sprite = Sprite(
            path_or_texture="assets/sprites/game_over_screen/give_up.png",
            center_x=int(settings.WINDOW_WIDTH * .65),
            center_y=int(settings.WINDOW_HEIGHT * .2)
        )

        self.give_up_option_sprite.append_texture(
            arcade.load_texture("assets/sprites/game_over_screen/give_up_highlighted.png"))
        self.give_up_option_sprite.set_texture(0)
        self.give_up_option_sprite.alpha = 0

        """
        continue_option_sprite_texture = arcade.create_text_sprite(
            text="CONTINUE",
            font_name="8bitoperator JVE",
            font_size=48,
            color=(255, 255, 255, 255)
        ).texture
        

        continue_option_sprite_highlight_texture = arcade.create_text_sprite(
            text="CONTINUE",
            font_name="8bitoperator JVE",
            font_size=48,
            color=(255, 255, 0, 255)
        ).texture

        self.continue_option_sprite = arcade.create_text_sprite(
            text="CONTINUE",
            font_name="8bitoperator JVE",
            font_size=48,
            color=(255, 255, 255, 255)
        )
        self.continue_option_sprite.center_x = int(settings.WINDOW_WIDTH * .35)
        self.continue_option_sprite.center_y = int(settings.WINDOW_HEIGHT * .2)

        #self.continue_option_sprite.append_texture(continue_option_sprite_texture)
        self.continue_option_sprite.append_texture(continue_option_sprite_highlight_texture)
        self.continue_option_sprite.set_texture(0)
        self.continue_option_sprite.alpha = 0

        
        give_up_option_sprite_texture = arcade.create_text_sprite(
            text="GIVE UP",
            font_name="8bitoperator JVE",
            font_size=48,
            color=(255, 255, 255, 255)
        ).texture
        

        give_up_option_sprite_highlight_texture = arcade.create_text_sprite(
            text="GIVE UP",
            font_name="8bitoperator JVE",
            font_size=48,
            color=(255, 255, 0, 255)
        ).texture

        self.give_up_option_sprite = arcade.create_text_sprite(
            text="GIVE UP",
            font_name="8bitoperator JVE",
            font_size=48,
            color=(255, 255, 255, 255)
        )
        self.give_up_option_sprite.center_x = int(settings.WINDOW_WIDTH * .65)
        self.give_up_option_sprite.center_y = int(settings.WINDOW_HEIGHT * .2)

        #self.give_up_option_sprite.append_texture(give_up_option_sprite_texture)
        self.give_up_option_sprite.append_texture(give_up_option_sprite_highlight_texture)
        self.give_up_option_sprite.set_texture(0)
        self.give_up_option_sprite.alpha = 0
        """

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
                self.game_over_title_sprite,
                self.blurry_soul_sprite,
                self.continue_option_sprite,
                self.give_up_option_sprite,
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
        self.death_message_textbox_unloaded = False
        self.load_continue_options = False
        self.continue_options_loaded = False

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
                    text="Please, don't give up!",
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

        # Variables used by soul moving function.
        self.blurry_soul_starting_x = 0
        self.blurry_soul_ending_x = 0
        self.blurry_soul_starting_y = 0
        self.blurry_soul_ending_y = 0
        self.blurry_soul_dx = 0
        self.blurry_soul_dy = 0

        self.blurry_soul_movement_time = 0.0
        self.blurry_soul_movement_total_duration = 0.4

        self.blurry_soul_moving = False
        self.continue_option_selected = False
        self.give_up_option_selected = False

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
                if not self.death_message_textbox_unloaded:
                    self.death_message_textbox.update_animation(delta_time)
                else:
                    self.load_continue_options = True

            if self.load_continue_options and not self.continue_options_loaded:
                self.blurry_soul_sprite.alpha = (min(128, self.blurry_soul_sprite.alpha + (128 * delta_time)))
                self.continue_option_sprite.alpha = (min(255, self.continue_option_sprite.alpha + (255 * delta_time)))
                self.give_up_option_sprite.alpha = (min(255, self.give_up_option_sprite.alpha + (255 * delta_time)))
                if self.continue_option_sprite.alpha >= 255:
                    self.continue_options_loaded = True
                else:
                    print(self.give_up_option_sprite.alpha, self.give_up_option_sprite.visible, self.give_up_option_sprite.center_x, self.give_up_option_sprite.center_y)

            if self.continue_options_loaded:
                if self.blurry_soul_moving:
                    self.move_blurry_soul_to_sprite_slightly(delta_time)

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
                self.death_message_textbox_unloaded = True

    def load_continue_options(self):
        """
        Loads the CONTINUE and GIVE UP options, as well as the soul for choosing between them.
        :return:
        """
        self.load_continue_options = True

    def move_blurry_soul_to_sprite(self, sprite: Sprite):
        """
        Sets the initial conditions for the blurry soul movement and starts the updates.
        :return:
        """
        self.blurry_soul_starting_x = self.blurry_soul_sprite.center_x
        self.blurry_soul_starting_y = self.blurry_soul_sprite.center_y
        self.blurry_soul_ending_x = sprite.center_x
        self.blurry_soul_ending_y = sprite.center_y

        self.blurry_soul_dx = self.blurry_soul_ending_x - self.blurry_soul_starting_x
        self.blurry_soul_dy = self.blurry_soul_ending_y - self.blurry_soul_starting_y

        self.blurry_soul_moving = True
        self.blurry_soul_movement_time = 0.0

    def move_blurry_soul_to_sprite_slightly(self, delta_time: float):
        """
        The function that moves the blurry soul to the supplied coordinates each frame.
        :return: None
        """
        self.blurry_soul_movement_time += delta_time

        fraction_of_distance_travelled = ease_out(self.blurry_soul_movement_time / self.blurry_soul_movement_total_duration)

        self.blurry_soul_sprite.center_x = self.blurry_soul_starting_x + (self.blurry_soul_dx * fraction_of_distance_travelled)
        self.blurry_soul_sprite.center_y = self.blurry_soul_starting_y + (self.blurry_soul_dy * fraction_of_distance_travelled)

        if self.blurry_soul_movement_time >= self.blurry_soul_movement_total_duration:
            self.blurry_soul_moving = False
            self.blurry_soul_sprite.center_x = self.blurry_soul_ending_x
            self.blurry_soul_sprite.center_y = self.blurry_soul_ending_y

    def move_blurry_soul_to_continue_option(self):
        """
        Moves the blurry soul to the continue option.
        :return: None
        """
        if self.continue_options_loaded and not self.continue_option_selected:
            self.move_blurry_soul_to_sprite(self.continue_option_sprite)
            self.continue_option_selected = True
            self.give_up_option_selected = False
            self.continue_option_sprite.set_texture(1)
            self.give_up_option_sprite.set_texture(0)
            print(len(self.continue_option_sprite.textures))

    def move_blurry_soul_to_give_up_option(self):
        """
        Moves the blurry soul to the give up option.
        :return: None
        """
        if self.continue_options_loaded and not self.give_up_option_selected:
            self.move_blurry_soul_to_sprite(self.give_up_option_sprite)
            self.continue_option_selected = False
            self.give_up_option_selected = True
            self.continue_option_sprite.set_texture(0)
            self.give_up_option_sprite.set_texture(1)

import random

import arcade
import pyglet
from PIL import Image
from arcade import Sprite, Texture
from arcade.types import Color

import non_player_character
import player_character
import settings
import texture_methods
from animations.common_animations import SparkleAnimation
from character import Character
from graphics_methods import make_texture_solid_color
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

        self.sprite.right = self.target.right + 24
        self.sprite.center_y = self.target.center_y - 24 + (self.target.times_struck_this_turn * 40)
        self.sprite.scale_x = 2.0
        self.sprite.scale_y = 0.1

        self.time_after_initial_slide = 0

        self.number_has_not_bounced = True
        self.time_after_bounce = 0
        self.total_duration = 3.0
        self.floor = (self.target.center_y - 56) + (self.target.times_struck_this_turn * 40)
        self.number_has_not_bounced_again = True

        self.target.times_struck_this_turn += 1

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
        if self.sprite.scale_y >= 0.9 and self.time < 2.0:
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


class EnemySparedAnimation(SingleSpriteAnimation):
    def __init__(self, target: Sprite, total_duration: float = 1.0):
        super().__init__(
            sprite=target,
            total_duration=total_duration
        )

        self.sprite_pack_path = "assets/sprites/effects/heal_spare_particles"

        self.spare_particle_textures = self._texture_array = texture_methods.load_textures_at_filepath_into_texture_array(
            self.sprite_pack_path
        )

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
            sprite.visible = False
            self.spare_particle_sprite_list.append(sprite)

        self.fading_sprite = arcade.Sprite()
        self.fading_sprite.texture = make_texture_solid_color(self.sprite.texture, arcade.color.WHITE)
        self.fading_sprite.scale = self.sprite.scale
        self.fading_sprite.color = arcade.color.WHITE
        self.fading_sprite.alpha = 0
        self.fading_sprite.center_x = self.sprite.center_x
        self.fading_sprite.center_y = self.sprite.center_y

        self.extra_fading_sprite = arcade.Sprite()
        self.extra_fading_sprite.visible = False

        self.inflection_point = self.total_duration / 4
        self.inflection_point_reached = False
        self.time_after_inflection_point = 0.0
        self.duration_after_inflection_point = self.total_duration - self.inflection_point

        # Used to track whether or not the base enemy texture has changed.
        self._cached_base_texture = self.sprite.texture

        # Miscellaneous variables so that on_update isn't repeating redundant calculations
        self.fading_sprite_translation_factor = settings.WINDOW_WIDTH / 10
        self.extra_fading_sprite_translation_factor = settings.WINDOW_WIDTH / 5
        self.particle_sprite_translation_factor = settings.WINDOW_WIDTH / 84

    def update_animation(self, delta_time):
        # This is probably not the most optimal way to do this.
        if self.sprite.texture != self._cached_base_texture:
            # Since most characters have an animated "spared" state, change the animation sprite textures every time the
            # character sprite changes.
            self.fading_sprite.texture = make_texture_solid_color(self.sprite.texture)
            self.extra_fading_sprite.texture = make_texture_solid_color(self.sprite.texture, arcade.color.WHITE)
            self._cached_base_texture = self.sprite.texture
        self.time += delta_time

        if self.time < self.inflection_point:
            self.fading_sprite.alpha = int((self.time / self.inflection_point) * 255)
        elif self.inflection_point <= self.time < self.total_duration:
            if not self.inflection_point_reached:
                # Intialize self.extra_fading_sprite
                self.extra_fading_sprite.texture = make_texture_solid_color(self.sprite.texture, arcade.color.WHITE)
                self.extra_fading_sprite.scale = self.sprite.scale
                self.extra_fading_sprite.color = arcade.color.WHITE
                self.extra_fading_sprite.alpha = 128
                self.extra_fading_sprite.center_x = self.sprite.center_x
                self.extra_fading_sprite.center_y = self.sprite.center_y

                # Flag inflection point reached
                self.inflection_point_reached = True

                # Set the character sprite to be invisible
                self.sprite.visible = False

                # Set the extra fading sprite to be visible
                self.extra_fading_sprite.visible = True

                # Set the particles to be visible
                for particle_sprite in self.spare_particle_sprite_list:
                    particle_sprite.visible = True

            # Animate both the fading sprites to fade away
            self.time_after_inflection_point += delta_time

            self.fading_sprite.center_x += delta_time * self.fading_sprite_translation_factor
            self.extra_fading_sprite.center_x += delta_time * self.extra_fading_sprite_translation_factor

            self.fading_sprite.alpha = int((1 - (self.time_after_inflection_point / self.duration_after_inflection_point)) * 255)
            self.extra_fading_sprite.alpha = int((1 - (self.time_after_inflection_point / self.duration_after_inflection_point)) * 128)

            # Animate the particle sprites to rotate, drift to the right, and change textures
            texture_index = int(self.time_after_inflection_point * 6) % len(self.spare_particle_sprite_list)
            for particle_sprite in self.spare_particle_sprite_list:
                particle_sprite.set_texture(texture_index)
                particle_sprite.turn_right(delta_time * 100)
                particle_sprite.center_x += self.time_after_inflection_point * self.particle_sprite_translation_factor

                particle_sprite.alpha = int((1 - (self.time_after_inflection_point / self.duration_after_inflection_point)) * 255)
        else:
            self.sprite.kill()
            self.fading_sprite.kill()
            self.extra_fading_sprite.kill()
            for particle_sprite in self.spare_particle_sprite_list:
                particle_sprite.kill()
            self.terminate_animation()

    def get_sprites(self):
        """
        Get the sprites used by this animation.
        :return: Both of the fading out sprites used by this animation.
        """
        return [self.fading_sprite, self.extra_fading_sprite] + self.spare_particle_sprite_list


class HealAnimation(SparkleAnimation):
    """
    The default heal animation. (green sparkles drifing up)
    """
    def __init__(self, target: Sprite):
        super().__init__(
            target=target,
            total_duration=0.8,
            color=arcade.color.NEON_GREEN, # Color(0, 214, 0, 255),
            particle_starting_rect=target.rect,
            number_of_particles=10
        )


class TPGainAnimation(SparkleAnimation):
    """
    The default heal animation. (orange sparkles drifting up)
    """
    def __init__(self, target: Sprite):
        super().__init__(
            target=target,
            total_duration=0.8,
            color=Color(255, 160, 64, 255),
            particle_starting_rect=target.rect,
            number_of_particles=10
        )


class FightHitBar(SingleSpriteAnimation):
    """
    The little bar that you have to time with the fight sprite thingy.
    """
    def __init__(self, controller, actor, target, bar_height: int = 30, bar_center_y: int = 100):
        self.bar_width = 12
        self.bar_height = bar_height
        self.bar_center_y = bar_center_y
        self.bar_texture = Texture(Image.new("RGBA", (self.bar_width, self.bar_height), (255, 255, 255, 255)))
        self.critical_bar_texture = make_texture_solid_color(self.bar_texture, arcade.color.YELLOW)
        self.initial_center_x = random.randint(int(settings.WINDOW_WIDTH / 400), int(settings.WINDOW_WIDTH / 200)) * 200

        super().__init__(
            sprite=Sprite(
                path_or_texture=self.bar_texture,
                center_x=self.initial_center_x,
                center_y=bar_center_y,
            )
        )

        self.sprite.textures = [self.bar_texture, self.critical_bar_texture]
        self.sprite.texture_index = 0

        self.actor = actor
        self.target = target
        self.controller = controller

        self.trailing_bars = []
        self.trailing_bars_spawn_rate = 0.2
        self.trailing_bars_respawn_distance = 30
        self.trailing_bar_center_x = self.initial_center_x

        for i in range(7):
            trailing_bar_sprite = Sprite(
                path_or_texture=self.bar_texture,
                center_x=self.trailing_bar_center_x,
                center_y=self.sprite.center_y
            )
            trailing_bar_sprite.visible = False
            trailing_bar_sprite.alpha = 128
            self.trailing_bars.append(trailing_bar_sprite)

        self.hit_registered = False
        self.critical_hit_registered = False
        self.time_since_hit_registered = 0.0
        self.bar_is_moving = True
        self.bar_is_not_removed = True

    def update_animation(self, delta_time: float):
        """ Updates the bar animation. """
        self.time += delta_time
        if self.bar_is_moving:
            self.sprite.center_x -= delta_time * 400
        if self.sprite.center_x < self.trailing_bar_center_x - self.trailing_bars_respawn_distance:
            for bar in self.trailing_bars:
                if not bar.visible:
                    bar.center_x = self.sprite.center_x
                    bar.visible = True
                    self.trailing_bar_center_x = self.sprite.center_x
                    break
                if bar.alpha == 0 and not self.hit_registered:
                    bar.center_x = self.sprite.center_x
                    bar.alpha = 128
                    self.trailing_bar_center_x = self.sprite.center_x
        for bar in self.trailing_bars:
            if bar.visible:
                bar.alpha = max(bar.alpha - 5, 0)
        if self.sprite.center_x < 150:
            self.sprite.visible = False
            self.bar_is_moving = False
            if self.bar_is_not_removed:
                self.controller.attack_target(self.actor, self.target, 0.0)
                self.controller.fight_hit_markers.remove(self)
                self.bar_is_not_removed = False
            pyglet.clock.schedule_once(lambda dt: self.terminate_animation(), 1.0)

        if self.hit_registered:
            self.time_since_hit_registered += delta_time
            if self.critical_hit_registered:
                self.sprite.scale = 1.0 + (self.time_since_hit_registered * 12)
                self.sprite.center_y = self.bar_center_y + (self.time_since_hit_registered * 16)
            else:
                self.sprite.scale = 1.0 + (self.time_since_hit_registered * 6)
                self.sprite.center_y = self.bar_center_y + (self.time_since_hit_registered * 8)
            self.sprite.alpha = max(255 - (self.time_since_hit_registered * 1000), 0)
            if self.time_since_hit_registered > 1:
                self.terminate_animation()

    def get_bar_sprite(self) -> Sprite:
        """
        Returns the main bar sprite of the animation (the one the player lines up with the hit box).
        :return: self.sprite (the bar sprite the player lines up with the hit box in the FIGHT widget)
        """
        return self.sprite

    def get_sprites(self):
        """
        Returns a list of sprites used by this animation.
        :return: list[Sprite]
        """
        return self.trailing_bars + [self.sprite]

    def kill_sprites(self):
        """
        Kills all sprites used by this animation.
        :return:
        """
        self.sprite.kill()
        for sprite in self.trailing_bars:
            sprite.kill()

    def register_hit(self):
        self.hit_registered = True
        self.bar_is_moving = False

    def register_critical_hit(self):
        self.sprite.set_texture(1)
        self.critical_hit_registered = True

        self.register_hit()

    def terminate_animation(self):
        super().terminate_animation()
        self.kill_sprites()

import math

import arcade

import settings
from graphics_objects import AnimatedSprite
from sprites_and_effects_collection import SpritesAndEffectsCollection


class DepthsBackgroundAnimation:
    """
    The IMAGE_DEPTHS animation used in the background of the GONERMAKER.
    """
    def __init__(self, sprites_and_effects_collection: SpritesAndEffectsCollection):
        self.sprites_and_effects_collection = sprites_and_effects_collection

        self.depths_texture = arcade.load_texture(
            file_path="assets/textures/backgrounds/IMAGE_DEPTHS_lowres.png"
        )
        self.depths_frame_array = []

        self.depths_animation_timer = 0.0  # The timer used by the animation

        self.depths_animation_initial_scale = 10.0  # Initial scale of depths animation frames when initially rendered
        self.depths_animation_scale_increment = 0.05  # How much the scale of each animation frame is increased every frame
        self.depths_animation_lifetime = 5  # Amount of time between when frame is created and when frame is reset
        self.depths_animation_number_of_frames = 5  # Number of frames used in the animation
        self.depths_animation_period = self.depths_animation_lifetime / self.depths_animation_number_of_frames # Time between each frame
        self.depths_animation_max_alpha = 60  # The max alpha each frame will have before it starts to decrement
        self.depths_animation_coefficient = 2 * (self.depths_animation_max_alpha / self.depths_animation_lifetime)
        self.depths_animation_framerate = 0.05  # The time interval at which each frame will update

        # The interval of time between when the terminate depths animation function
        # checks if the frame array is empty.
        self.terminate_depths_animation_check_period = 1

        self.depths_frame_array = []

        # Variables used by the process of adding new frames.
        self.terminate_depths_animation_flag = False
        self.previous_frame_index = -1

    def update_animation(self, delta_time: float):
        # For every sprite in the frame:
        # 1. If alpha = 0, reset the alpha to 1 and the scale to 1.0.
        self.depths_animation_timer += delta_time

        if len(self.depths_frame_array) < self.depths_animation_number_of_frames:
            if self.previous_frame_index != self.depths_animation_timer // self.depths_animation_period:
                self.add_sprite_to_depths_array()
                self.previous_frame_index = self.depths_animation_timer // self.depths_animation_period


        for frame in self.depths_frame_array:
            sprite = frame.sprite
            sprite._center_x = settings.WINDOW_CENTER_X
            sprite._center_y = settings.WINDOW_CENTER_Y
            if frame.age >= self.depths_animation_lifetime:
                sprite.scale_x = self.depths_animation_initial_scale
                sprite.scale_y = self.depths_animation_initial_scale
                sprite.alpha = 0
                frame.reset_age()
            else:
                frame.age += delta_time
                sprite.scale_x += self.depths_animation_scale_increment
                sprite.scale_y += self.depths_animation_scale_increment
                alpha = -abs(math.ceil(
                    (self.depths_animation_coefficient * frame.age) - self.depths_animation_max_alpha)) + self.depths_animation_max_alpha
                if alpha < 0:
                    sprite.alpha = 0
                else:
                    sprite.alpha = alpha

    def add_sprite_to_depths_array(self):
        if len(self.depths_frame_array) < self.depths_animation_number_of_frames and not self.terminate_depths_animation_flag:
            sprite = arcade.Sprite(path_or_texture="assets/textures/backgrounds/IMAGE_DEPTHS_lowres.png",
                                   center_x=settings.WINDOW_CENTER_X,
                                   center_y=settings.WINDOW_CENTER_Y,)
            sprite.alpha = 1
            sprite.scale_x = self.depths_animation_initial_scale
            sprite.scale_y = self.depths_animation_initial_scale
            frame = AnimatedSprite(sprite, 1)
            self.depths_frame_array.append(frame)
            self.sprites_and_effects_collection.background_sprites.append(sprite)
        if self.terminate_depths_animation_flag:
            for frame in self.depths_frame_array:
                if frame.sprite.alpha <= 0:
                    self.sprites_and_effects_collection.background_sprites.remove(frame.sprite)
                    self.depths_frame_array.remove(frame)

    # Instantly terminates the depths animation.
    def instantly_terminate_depths_animation(self):
        for frame in self.depths_frame_array:
            if frame.sprite in self.sprites_and_effects_collection.background_sprites:
                self.sprites_and_effects_collection.background_sprites.remove(frame.sprite)
                frame.sprite.kill()
        self.depths_frame_array.clear()

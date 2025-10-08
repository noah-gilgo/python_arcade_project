import arcade
import pyglet
import math
from graphics_objects import Frame

DEPTHS_ANIMATION_INITIAL_SCALE = 7.0
DEPTHS_ANIMATION_SCALE_INCREMENT = 0.05
DEPTHS_ANIMATION_LIFETIME = 10
DEPTHS_ANIMATION_NUMBER_OF_SPRITES = 10
DEPTHS_ANIMATION_PERIOD = DEPTHS_ANIMATION_LIFETIME / DEPTHS_ANIMATION_NUMBER_OF_SPRITES
DEPTHS_ANIMATION_MAX_ALPHA = 40
DEPTHS_ANIMATION_COEFFICIENT = 2 * (DEPTHS_ANIMATION_MAX_ALPHA / DEPTHS_ANIMATION_LIFETIME)

depths_frame_array = []


def add_sprite_to_depths_array(dt, center, sprite_list):
    if len(depths_frame_array) < DEPTHS_ANIMATION_NUMBER_OF_SPRITES:
        sprite = arcade.Sprite(path_or_texture="assets/textures/backgrounds/IMAGE_DEPTHS_lowres.png",
                               center_x=center[0],
                               center_y=center[1],
                               )
        sprite.alpha = 1
        sprite.scale_x = DEPTHS_ANIMATION_INITIAL_SCALE
        sprite.scale_y = DEPTHS_ANIMATION_INITIAL_SCALE
        frame = Frame(sprite)
        depths_frame_array.append(frame)
        sprite_list.append(sprite)


def initialize_depths_array(time_interval, center, sprite_list):
    pyglet.clock.schedule_interval(
        lambda dt: add_sprite_to_depths_array(dt, center, sprite_list),
        time_interval
    )


def animate_depths_frames(dt):
    # For every sprite in the frame:
    # 1. If alpha = 0, reset the alpha to 1 and the scale to 1.0.
    frame_array_index = 0
    frame_array_length = len(depths_frame_array)
    for frame in depths_frame_array:
        sprite = frame.sprite
        if sprite.alpha <= 0:
            sprite.scale_x = DEPTHS_ANIMATION_INITIAL_SCALE
            sprite.scale_y = DEPTHS_ANIMATION_INITIAL_SCALE
            sprite.alpha = 1
            if frame_array_length > 0:
                frame.reset_age()
            print("alpha reached zero")
        else:
            if frame_array_length > 0:
                frame.age += dt
            sprite.scale_x += DEPTHS_ANIMATION_SCALE_INCREMENT
            sprite.scale_y += DEPTHS_ANIMATION_SCALE_INCREMENT
            sprite.alpha = -abs(math.ceil((DEPTHS_ANIMATION_COEFFICIENT * frame.age) - DEPTHS_ANIMATION_MAX_ALPHA)) + DEPTHS_ANIMATION_MAX_ALPHA
        frame_array_index += 1


def animate_depths(time_interval):
    pyglet.clock.schedule_interval(
        lambda dt: animate_depths_frames(dt),
        time_interval
    )

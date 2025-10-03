import arcade
import pyglet
import math

INITIAL_SCALE = 10.0
SCALE_INCREMENT = 0.05
ANIMATION_PERIOD = 10


def add_sprite_to_array(dt, sprite_array: list[arcade.Sprite], center, sprite_list):
    if len(sprite_array) < 10:
        sprite = arcade.Sprite(path_or_texture="assets/textures/backgrounds/IMAGE_DEPTHS_lowres.png",
                               center_x=center[0],
                               center_y=center[1],
                               )
        sprite.alpha = 1
        sprite.scale_x = INITIAL_SCALE
        sprite.scale_y = INITIAL_SCALE
        sprite_array.append(sprite)
        sprite_list.append(sprite)


def initialize_depths_array(sprite_array, time_interval, center, sprite_list):
    pyglet.clock.schedule_interval(
        lambda dt: add_sprite_to_array(dt, sprite_array, center, sprite_list),
        time_interval
    )


def animate_depths_frames(dt, sprite_array: list[arcade.Sprite]):
    # For every sprite in the frame:
    # 1. If alpha = 0, reset the alpha to 255 and the scale to 1.0.
    for sprite in sprite_array:
        if sprite.alpha <= 0:
            sprite.scale_x = INITIAL_SCALE
            sprite.scale_y = INITIAL_SCALE
            sprite.alpha = 1
            print("alpha reached zero")
        else:
            sprite.scale_x += SCALE_INCREMENT
            sprite.scale_y += SCALE_INCREMENT
            sprite.alpha = -abs((math.ceil(12.5*(sprite.scale_x - INITIAL_SCALE))) - 31) + 31
    # 2. Else, decrement the alpha by 8, and scale the sprite by a factor of 1.01
    pass


def animate_depths(sprite_array, time_interval):
    pyglet.clock.schedule_interval(
        lambda dt: animate_depths_frames(dt, sprite_array),
        time_interval
    )
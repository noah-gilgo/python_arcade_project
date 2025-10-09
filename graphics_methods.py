import arcade
import pyglet
import math
from graphics_objects import Frame
import main

DEPTHS_ANIMATION_INITIAL_SCALE = 10.0  # Initial scale of depths animation frames when initially rendered
DEPTHS_ANIMATION_SCALE_INCREMENT = 0.05  # How much the scale of each animation frame is increased every frame
DEPTHS_ANIMATION_LIFETIME = 5  # Amount of time between when frame is created and when frame is reset
DEPTHS_ANIMATION_NUMBER_OF_FRAMES = 5  # Number of frames used in the animation
DEPTHS_ANIMATION_PERIOD = DEPTHS_ANIMATION_LIFETIME / DEPTHS_ANIMATION_NUMBER_OF_FRAMES  # Time between each frame
DEPTHS_ANIMATION_MAX_ALPHA = 60  # The max alpha each frame will have before it starts to decrement
DEPTHS_ANIMATION_COEFFICIENT = 2 * (DEPTHS_ANIMATION_MAX_ALPHA / DEPTHS_ANIMATION_LIFETIME)
DEPTHS_ANIMATION_FRAMERATE = 0.05  # The time interval at which each frame will update

# The interval of time between when the terminate depths animation function
# checks if the frame array is empty.
TERMINATE_DEPTHS_ANIMATION_CHECK_PERIOD = 1

depths_frame_array = []

terminate_depths_animation_flag = False


# Step function for initialize_depths_array function.
def add_sprite_to_depths_array(dt, center, sprite_list: list[arcade.Sprite]):
    global terminate_depths_animation_flag
    if len(depths_frame_array) < DEPTHS_ANIMATION_NUMBER_OF_FRAMES and not terminate_depths_animation_flag:
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
    if terminate_depths_animation_flag:
        for frame in depths_frame_array:
            if frame.sprite.alpha <= 0:
                sprite_list.remove(frame.sprite)
                depths_frame_array.remove(frame)


add_sprite_to_depths_array_callback = None


# Gradually adds depths animation sprites/frames to the sprite/frame arrays every DEPTHS_ANIMATION_PERIOD number of
# frames until the number of frames = DEPTHS_ANIMATION_NUMBER_OF_FRAMES
def initialize_depths_array(center, sprite_list):
    global add_sprite_to_depths_array_callback
    def add_sprite_to_depths_array_callback(dt):
        add_sprite_to_depths_array(dt, center, sprite_list)

    pyglet.clock.schedule_interval(
        add_sprite_to_depths_array_callback,
        DEPTHS_ANIMATION_PERIOD
    )


# Step function for animate_depths function.
def animate_each_depths_frame(dt):
    # For every sprite in the frame:
    # 1. If alpha = 0, reset the alpha to 1 and the scale to 1.0.
    for frame in depths_frame_array:
        sprite = frame.sprite
        if frame.age >= DEPTHS_ANIMATION_LIFETIME:
            sprite.scale_x = DEPTHS_ANIMATION_INITIAL_SCALE
            sprite.scale_y = DEPTHS_ANIMATION_INITIAL_SCALE
            sprite.alpha = 0
            frame.reset_age()
        else:
            frame.age += dt
            sprite.scale_x += DEPTHS_ANIMATION_SCALE_INCREMENT
            sprite.scale_y += DEPTHS_ANIMATION_SCALE_INCREMENT
            alpha = -abs(math.ceil(
                (DEPTHS_ANIMATION_COEFFICIENT * frame.age) - DEPTHS_ANIMATION_MAX_ALPHA)) + DEPTHS_ANIMATION_MAX_ALPHA
            if alpha < 0:
                sprite.alpha = 0
            else:
                sprite.alpha = alpha


# Animates all of the frames in depths_frame_array every DEPTHS_ANIMATION_FRAMERATE seconds.
def animate_depths_frames():
    pyglet.clock.schedule_interval(
        animate_each_depths_frame,
        DEPTHS_ANIMATION_FRAMERATE
    )


def animate_depths(center, sprite_list: list[arcade.Sprite]):
    initialize_depths_array(center, sprite_list)
    animate_depths_frames()


# Step function for gradually_terminate_depths_animation function.
def check_for_no_depths_frames(dt):
    if len(depths_frame_array) == 0:
        pyglet.clock.unschedule(animate_each_depths_frame)
        pyglet.clock.unschedule(add_sprite_to_depths_array_callback)
        pyglet.clock.unschedule(check_for_no_depths_frames)


# Gradually terminates the depths animation.
def gradually_terminate_depths_animation():
    global terminate_depths_animation_flag
    terminate_depths_animation_flag = True
    pyglet.clock.schedule_interval(
        check_for_no_depths_frames,
        TERMINATE_DEPTHS_ANIMATION_CHECK_PERIOD
    )


# Instantly terminates the depths animation.
def instantly_terminate_depths_animation(sprite_list: list[arcade.Sprite]):
    pyglet.clock.unschedule(animate_each_depths_frame)
    pyglet.clock.unschedule(add_sprite_to_depths_array_callback)
    for frame in depths_frame_array:
        if frame.sprite in sprite_list:
            sprite_list.remove(frame.sprite)
    depths_frame_array.clear()

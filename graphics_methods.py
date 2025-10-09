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

depths_frame_array = []

terminate_depths_animation = False


def add_sprite_to_depths_array(dt, center, sprite_list):
    global terminate_depths_animation
    if len(depths_frame_array) < DEPTHS_ANIMATION_NUMBER_OF_FRAMES and not terminate_depths_animation:
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
    else:
        terminate_depths_animation = True
    if terminate_depths_animation:
        for frame in depths_frame_array:
            if frame.sprite.alpha <= 0:
                sprite_list.remove(frame.sprite)
                depths_frame_array.remove(frame)


# Since add_sprite_to_depths_array_callback requires parameters, it's callback from initialize_depths_array will be
# stored in a global variable.
add_sprite_to_depths_array_callback = None


def initialize_depths_array(center, sprite_list):
    global add_sprite_to_depths_array_callback

    def add_sprite_to_depths_array_callback(dt):
        add_sprite_to_depths_array(dt, center, sprite_list)

    pyglet.clock.schedule_interval(
        add_sprite_to_depths_array_callback,
        DEPTHS_ANIMATION_PERIOD
    )


def animate_depths_frames(dt):
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


def animate_depths():
    pyglet.clock.schedule_interval(
        animate_depths_frames,
        DEPTHS_ANIMATION_FRAMERATE
    )

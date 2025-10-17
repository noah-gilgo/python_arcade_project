import arcade

import texture_methods


class Frame:
    def __init__(self, sprite: arcade.Sprite):
        self.sprite = sprite
        self.age = 0.0

    def increment_age(self, dt: float):
        self.age += dt

    def reset_age(self):
        self.age = 0.0


class SimpleLoopAnimation:
    """
    Simple class used for storing data needed for simple looping animations with a constant yet adjustable time
    interval between frames.
    """
    def __init__(self, sprite_pack_path: str, frame_duration: float, loop_animation: bool):
        self._sprite_pack_path = sprite_pack_path
        self._frame_duration = frame_duration
        self._loop_animation = loop_animation

        self._texture_array = texture_methods.load_textures_at_filepath_into_texture_array(
            self._sprite_pack_path
        )

    def __len__(self):
        return len(self._texture_array)

    def __getitem__(self, item):
        return self._texture_array[item]

    def get_sprite_pack_path(self):
        """
        Gets the sprite path on the animation.
        :return str: The file path of the folder containing all of the frames of the animation.
        """
        return self._sprite_pack_path

    def set_sprite_pack_path(self, sprite_pack_path: str):
        """
        Sets the sprite path on the animation.
        :param sprite_pack_path:
        :return: None
        """
        self._sprite_pack_path = sprite_pack_path

    def get_frame_duration(self):
        """
        Gets the frame duration on the animation.
        :return: The frame duration of the animation in seconds.
        """
        return self._frame_duration

    def set_frame_duration(self, frame_duration: float):
        """
        Sets the frame duration on the animation.
        :param frame_duration: The frame duration of the animation in seconds.
        :return: None
        """
        self._frame_duration = frame_duration

    def get_loop_animation(self):
        """
        Gets whether or not the animation is meant to loop.
        :return: A bool representing whether or not the animation is meant to loop.
        """
        return self._loop_animation

    def set_loop_animation(self, loop_animation: bool):
        """
        Sets whether or not the animation is meant to loop.
        :param loop_animation: A bool representing whether or not the animation is meant to loop.
        :return: None
        """
        self._loop_animation = loop_animation

    def get_texture_array(self):
        """
        Gets an array of textures containing all of the textures loaded into the texture array.
        :return: A List[Texture] containing Textures representing every image located at the file path.
        """
        return self._texture_array

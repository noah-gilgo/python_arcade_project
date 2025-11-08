from PIL.Image import Image, Resampling
from arcade import Texture
from arcade.gui import UIWidget, UILabel, UILayout, UIBoxLayout, UIImage

import settings
import arcade


class TextBoxPortrait(UIImage):
    def __init__(self, texture_path):

        super().__init__(
            texture=arcade.Texture(arcade.load_image(texture_path).resize((192, 192), Resampling.NEAREST)),
            x=36,
            y=24
        )


class TextBoxText(UILabel):
    def __init__(self,
                 **kwargs):
        super().__init__(
            width=(settings.WINDOW_WIDTH - 144)-192-32,
            height=settings.WINDOW_HEIGHT/4 - 64,
            x=72+192+64,
            y=54,
            text="This is test text.",
            font_name="8bitoperator JVE",
            font_size=48,
            multiline=True
        )
        """
        self._text = text
        self._talk_sprite_path = talk_sprite_path
        self._character_render_noise_path = character_render_noise_path
        self._rate_of_text = rate_of_text

        self._height = 200  # height of the text box in pixels
        self._width = settings.WINDOW_WIDTH - 100 if talk_sprite_path in (None, "") else settings.WINDOW_WIDTH - 300
        """


class TextBoxDialog:
    """
    Stores the data representing a particular dialogue within the text box at the bottom of the screen during battle.
    If the portrait_texture_path is anything besides null or an empty string, it will be assumed that the dialogue will
    render with a character's talksprite.
    """
    def __init__(self, text: str, rate_of_text: float, portrait_texture_path: str, text_sound_path: str):
        self._text = text
        self._rate_of_text = rate_of_text

        self._portrait_texture = None
        if portrait_texture_path not in (None, ""):
            self._portrait_texture = arcade.Texture(arcade.load_image(portrait_texture_path).resize((192, 192), Resampling.NEAREST))
        self._text_sound = arcade.load_sound("assets/audio/dialog/snd_text.wav", False)
        if text_sound_path not in (None, ""):
            self._text_sound = arcade.load_sound(text_sound_path, False)

    def has_portrait(self):
        """
        Returns a bool representing whether or not the dialog has a talk sprite texture.
        :return: a bool representing whether or not the dialog has a talk sprite texture.
        """
        return self._portrait_texture is not None

    def get_text(self):
        """
        Returns the dialogue string stored within the object.
        :return: the dialogue string stored within the object.
        """
        return self._text

    def get_rate_of_text(self):
        """
        Returns the rate, in seconds, that each character of the text will be displayed by the TextBoxText object.
        :return: the rate that each character of the text will be displayed by the TextBoxText object (in seconds)
        """
        return self._rate_of_text

    def get_portrait_texture(self):
        """
        Returns an arcade.Texture object containing the texture of the portrait referenced by the object.
        :return: an arcade.Texture object containing the texture of the portrait referenced by the object.
        """
        return self._portrait_texture

    def get_text_sound(self):
        """
        Returns an arcade.Sound object storing the text sound located at the path passed into the object on creation.
        :return: an arcade.Sound object storing the text sound located at the path passed into the object on creation.
        """
        return self._text_sound


class TextBox(UIWidget):
    def __init__(self, **kwargs):
        super().__init__(
            x=0,
            y=0,
            width=settings.WINDOW_WIDTH,
            height=int(settings.WINDOW_HEIGHT / 4),
            children=[TextBoxPortrait("assets/sprites/player_characters/susie/dialog_portraits/susie_small_grin.png"),
                      TextBoxText()]
        )
        self.with_background(color=arcade.uicolor.BLACK)


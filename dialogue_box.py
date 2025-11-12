import pyglet.clock
from PIL.Image import Image, Resampling
from arcade import Texture
from arcade.gui import UIWidget, UILabel, UILayout, UIBoxLayout, UIImage

import settings
import arcade


class TextBoxPortrait(UIImage):
    def __init__(self, texture: arcade.Texture, x=36, y=24, width=192, height=192):
        """
        The widget for the textbox portrait that displays character portraits when they talk.
        :param texture_path: The path to the image file of the character portrait.
        :param dimensions: A tuple/list containing the x, y, width, and height dimensions of the portrait, respectively
        """
        super().__init__(
            texture=texture,
            x=x,
            y=y,
            width=width,
            height=height
        )

    def set_texture(self, texture: arcade.Texture):
        """
        Loads a texture into the widget.
        :param texture: The Texture object to replace the old texture.
        :return:
        """
        self.texture = texture


class TextBoxText(UILabel):
    def __init__(self,
                 text: str = "* Hell yeah Kris I'm in fortnite",
                 x=72,
                 y=54,
                 width=settings.WINDOW_WIDTH - 144,
                 height=settings.WINDOW_HEIGHT/4 - 64,
                 font_name: str = "8bitoperator JVE",
                 font_size: int = 48):
        super().__init__(
            x=x,
            y=y,
            width=width,
            height=height,
            text=text,
            font_name=font_name,
            font_size=font_size,
            multiline=True
        )

    def set_text(self, text: str):
        """
        Sets the text within the widget.
        :param text:
        :return:
        """
        self.text = text


class TextBoxDialog:
    """
    Stores the data representing a particular dialogue within the text box at the bottom of the screen during battle.
    If the portrait_texture_path is anything besides null or an empty string, it will be assumed that the dialogue will
    render with a character's talksprite.
    """
    def __init__(self,
                 portrait_texture_path: str = "",
                 text: str = "This is test text",
                 rate_of_text: float = 0.05,
                 text_sound_path: str = "assets/audio/dialog/snd_text.wav"
                 ):
        self._text = text
        self._rate_of_text = rate_of_text

        self._portrait_texture_path = portrait_texture_path
        self._is_dialogue_with_portrait = self._portrait_texture_path not in (None, "")

        self._text_sound_path = text_sound_path

        """
        self._default_portrait_dimensions = (36, 24, 192, 192)  # x pos, y pos, width, height
        self._default_textbox_dimensions = [264, 54, (settings.WINDOW_WIDTH - 144), settings.WINDOW_HEIGHT/4 - 64]
        if self._is_dialogue_with_portrait:
            self._default_textbox_dimensions[2] -= 192
        """

    def has_portrait(self):
        """
        Returns a bool representing whether or not the dialog has a talk sprite texture.
        :return: a bool representing whether or not the dialog has a talk sprite texture.
        """
        return self._is_dialogue_with_portrait

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

    def get_portrait_texture_path(self):
        """
        Returns an arcade.Texture object containing the texture of the portrait referenced by the object.
        :return: an arcade.Texture object containing the texture of the portrait referenced by the object.
        """
        return self._portrait_texture_path

    def get_text_sound_path(self):
        """
        Returns an arcade.Sound object storing the text sound located at the path passed into the object on creation.
        :return: an arcade.Sound object storing the text sound located at the path passed into the object on creation.
        """
        return self._text_sound_path


class TextBox(UIWidget):
    def __init__(self, dialog_box: TextBoxDialog = None):
        self._dialog_box = TextBoxDialog()
        if dialog_box:
            self._dialog_box = dialog_box

        self._text_box_text = TextBoxText()
        self._dialog_string = self._dialog_box.get_text()
        self._current_character_in_text_box_index = 0
        self._text_box_text.set_text("")

        if self._dialog_box.has_portrait():
            self._text_box_text.x = 264
        else:
            self._text_box_text.x = 72

        super().__init__(
            x=0,
            y=0,
            width=settings.WINDOW_WIDTH,
            height=int(settings.WINDOW_HEIGHT / 4),
            children=[self._text_box_text]
        )

        self._text_box_portrait = None

        self._text_box_portrait_path = ""
        self._text_box_portrait_texture = None
        if self._text_box_portrait_path not in (None, ""):
            self._text_box_portrait_texture = arcade.Texture(
                arcade.load_image(self._text_box_portrait_path).resize((192, 192), Resampling.NEAREST))
            self._text_box_portrait = TextBoxPortrait(self._text_box_portrait_texture)
            self.add(self._text_box_portrait)

        self.with_background(color=arcade.uicolor.BLACK)

        self._text_sound = arcade.load_sound(self._dialog_box.get_text_sound_path(), False)

    def load_dialog(self, text_box_dialog: TextBoxDialog):
        """
        Loads the data from a text box dialog into the parent TextBox widget.
        :param text_box_dialog: the TextBoxDialog object to overwrite the current data of the TextBox
        :return: None
        """
        self._dialog_string = text_box_dialog.get_text()
        self._text_box_text.set_text("")
        self._current_character_in_text_box_index = 0

        if text_box_dialog.has_portrait():
            if not self._dialog_box.has_portrait():
                self._text_box_text.move(dx=192)
            self._text_box_portrait_path = text_box_dialog.get_portrait_texture_path()
            self._text_box_portrait_texture = arcade.Texture(
                arcade.load_image(self._text_box_portrait_path).resize((192, 192), Resampling.NEAREST)
            )
            if self._text_box_portrait:
                self._text_box_portrait.set_texture(self._text_box_portrait_texture)
            else:
                self._text_box_portrait = TextBoxPortrait(self._text_box_portrait_texture)
                self.add(self._text_box_portrait)

        else:
            if self._dialog_box.has_portrait():
                self._text_box_text.move(dx=-192)
            self._text_box_portrait_path = ""
            self.remove(self._text_box_portrait)
            self._text_box_portrait = None

        self._text_sound = arcade.load_sound(text_box_dialog.get_text_sound_path(), False)

        self._dialog_box = text_box_dialog

        self.animate_character_dialog()

    def add_character_to_text_box_text(self, dt):
        """
        Scheduled event that adds a character to the textbox text.
        If the textbox text length already matches the index of the character to be added, the scheduled event is
        unscheduled.
        :return: None
        """

        if self._current_character_in_text_box_index < len(self._dialog_string):
            self._text_box_text.text += self._dialog_string[self._current_character_in_text_box_index]
            self._text_sound.play()
            self._current_character_in_text_box_index += 1
        else:
            self._current_character_in_text_box_index = 0
            pyglet.clock.unschedule(self.add_character_to_text_box_text)

    def animate_character_dialog(self):
        pyglet.clock.schedule_interval(
            self.add_character_to_text_box_text,
            self._dialog_box.get_rate_of_text()
        )

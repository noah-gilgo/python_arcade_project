import pyglet.clock
from PIL import Image
from arcade.gui import UIWidget, UILabel, UIImage, Surface, UILayout, UIBoxLayout

import settings
import arcade


class TextBoxPortrait(UIImage):
    def __init__(self, texture_path: str = "", width=192, height=192):
        """
        The widget for the textbox portrait that displays character portraits when they talk.
        :param texture_path: The path to the image file of the character portrait.
        :param dimensions: A tuple/list containing the x, y, width, and height dimensions of the portrait, respectively
        """

        if texture_path:
            image = Image.open(texture_path)
            texture = arcade.Texture(arcade.load_image(texture_path).resize(image.size, Image.Resampling.NEAREST))
            self.visible = True
        else:
            texture = None
            self.visible = False

        super().__init__(
            texture=texture,
            width=192,
            height=192,
            x=24,
            y=24
        )

        #self.with_border(color=arcade.color.RED)

    def set_texture(self, texture_path: str = ""):
        """
        Loads a texture into the widget.
        :param texture_path: The file path of the texture to replace the old texture.
        :return:
        """
        if texture_path:
            image = Image.open(texture_path)
            texture = arcade.Texture(arcade.load_image(texture_path).resize(image.size, Image.Resampling.NEAREST))
            self.texture = texture
            self.visible = True
            self.width = 192
            #self.width = self.texture.width
        else:
            #self.texture = None
            self.visible = False


class TextBoxText(UILabel):
    def __init__(self,
                 text: str = "* Hell yeah Kris I'm in fortnite",
                 width=settings.WINDOW_WIDTH - 164,
                 height=settings.WINDOW_HEIGHT/4 - 32,
                 font_name: str = "8bitoperator JVE",
                 font_size: int = 48):
        super().__init__(
            width=width,
            height=height,
            text=text,
            font_name=font_name,
            font_size=font_size,
            multiline=True,
            x=64,
            y=16
        )

        #self.with_background(color=arcade.color.BLACK)
        #self.with_border(color=arcade.color.NEON_GREEN)

    def set_text(self, text: str):
        """
        Sets the text within the widget.
        :param text:
        :return:
        """
        self.text = text

    def do_render(self, surface: Surface):
        super().do_render(surface)
        #self.width = settings.WINDOW_WIDTH - 192


class TextBoxDialog:
    """
    Stores the data representing a particular dialogue within the text box at the bottom of the screen during battle.
    If the portrait_texture_path is anything besides null or an empty string, it will be assumed that the dialogue will
    render with a character's talksprite.
    """
    def __init__(self,
                 portrait_texture_path: str = "",
                 text: str = "This is test text",
                 rate_of_text: float = 0.04,
                 text_sound_path: str = "assets/audio/dialog/snd_text.wav"
                 ):
        self.text = text
        self.rate_of_text = rate_of_text

        self.portrait_texture_path = portrait_texture_path
        self.is_dialogue_with_portrait = self.portrait_texture_path not in (None, "")

        self.text_sound_path = text_sound_path

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
        return self.is_dialogue_with_portrait

    def get_text(self):
        """
        Returns the dialogue string stored within the object.
        :return: the dialogue string stored within the object.
        """
        return self.text

    def get_rate_of_text(self):
        """
        Returns the rate, in seconds, that each character of the text will be displayed by the TextBoxText object.
        :return: the rate that each character of the text will be displayed by the TextBoxText object (in seconds)
        """
        return self.rate_of_text

    def get_portrait_texture_path(self):
        """
        Returns an arcade.Texture object containing the texture of the portrait referenced by the object.
        :return: an arcade.Texture object containing the texture of the portrait referenced by the object.
        """
        return self.portrait_texture_path

    def get_text_sound_path(self):
        """
        Returns an arcade.Sound object storing the text sound located at the path passed into the object on creation.
        :return: an arcade.Sound object storing the text sound located at the path passed into the object on creation.
        """
        return self.text_sound_path


class TextBox(UIBoxLayout):
    def __init__(self, text_box_dialog: TextBoxDialog = None):
        self.text_box_dialog = text_box_dialog  # The TextBoxDialog object containing the data to be loaded by the widget
        self.text_box_text = TextBoxText()  # The part of the widget containing the text
        self.text_box_portrait = TextBoxPortrait()  # The part of the widget containing the dialog portrait
        self.current_character_in_text_box_index = 0
        self.text_box_text.set_text("")

        if text_box_dialog:
            self.text_box_portrait.visible = self.text_box_dialog.has_portrait()
            self.dialog_string = self.text_box_dialog.get_text()
            if self.text_box_portrait.visible:
                self.text_box_portrait.width = 192
                self.text_box_text.width = settings.WINDOW_WIDTH - 216
            else:
                self.text_box_portrait.width = 1
                self.text_box_text.width = settings.WINDOW_WIDTH - 88
            self.text_sound = arcade.load_sound(self.text_box_dialog.get_text_sound_path(), False)
            self.rate_of_text = self.text_box_dialog.get_rate_of_text()

        super().__init__(
            x=0,
            y=0,
            width=settings.WINDOW_WIDTH,
            height=int(settings.WINDOW_HEIGHT / 4),
            vertical=False,
            align="center",
        )

        self.text_box_portrait_path = ""
        self.text_box_portrait_texture = None

        self.add(self.text_box_portrait)
        self.add(self.text_box_text)

        """
        if self._text_box_portrait_path not in (None, ""):
            self._text_box_portrait = TextBoxPortrait(self._text_box_portrait_path)
            self.add(self._text_box_portrait)
        """

        self.with_background(color=arcade.uicolor.BLACK)
        #self.with_border(color=arcade.color.LIGHT_BLUE)

        # self.text_box_text.visible = False
        self.do_layout()

    def load_dialog(self, text_box_dialog: TextBoxDialog):
        """
        Loads the data from a text box dialog into the parent TextBox widget.
        :param text_box_dialog: the TextBoxDialog object to overwrite the current data of the TextBox
        :return: None
        """
        previous_text_box_dialog = self.text_box_dialog
        self.text_box_dialog = text_box_dialog

        self.dialog_string = text_box_dialog.get_text()
        self.text_box_text.set_text("")
        self.current_character_in_text_box_index = 0

        if text_box_dialog.has_portrait():
            self.text_box_portrait_path = text_box_dialog.get_portrait_texture_path()
            print(self.text_box_portrait_path)
            self.text_box_portrait.set_texture(self.text_box_portrait_path)
            self.text_box_portrait.visible = True
            print(str(self.children))
            print("self.text_box_portrait.visible:", self.text_box_portrait.visible)
            print("self.text_box_portrait.width:", self.text_box_portrait.width)
            self.text_box_portrait.width = 192
            self.text_box_text.width=settings.WINDOW_WIDTH - 300
            if previous_text_box_dialog and not previous_text_box_dialog.has_portrait():
                self.text_box_text.move(dx=192)
        else:
            if previous_text_box_dialog and previous_text_box_dialog.has_portrait():
                self.text_box_text.move(dx=-192)
            self.text_box_portrait.visible = False
            self.text_box_portrait.width = 1
            self.text_box_text.width=settings.WINDOW_WIDTH - 144

        self.do_layout()

        if text_box_dialog.get_text_sound_path():
            self.text_sound = arcade.load_sound(text_box_dialog.get_text_sound_path(), False)
        else:
            self.text_sound = None

        self.text_box_dialog = text_box_dialog

        self.rate_of_text = text_box_dialog.get_rate_of_text()

        pyglet.clock.unschedule(self.add_character_to_text_box_text)
        self.animate_character_dialog()

    def clear_dialog(self):
        """
        Clears the dialog from the text box.
        :return: None
        """
        self.load_dialog(
            text_box_dialog=TextBoxDialog(
                text="",
            )
        )

    def add_character_to_text_box_text(self, dt):
        """
        Scheduled event that adds a character to the textbox text.
        If the textbox text length already matches the index of the character to be added, the scheduled event is
        unscheduled.
        :return: None
        """

        if self.current_character_in_text_box_index < len(self.dialog_string):
            self.text_box_text.text += self.dialog_string[self.current_character_in_text_box_index]
            if self.text_sound:
                self.text_sound.play()
            self.current_character_in_text_box_index += 1
        else:
            self.current_character_in_text_box_index = 0
            pyglet.clock.unschedule(self.add_character_to_text_box_text)

    def animate_character_dialog(self):
        pyglet.clock.schedule_interval(
            self.add_character_to_text_box_text,
            self.rate_of_text
        )

    def do_layout(self):
        self.width = settings.WINDOW_WIDTH
        self.height = int(settings.WINDOW_HEIGHT / 4)
        self.with_background(color=arcade.uicolor.BLACK)

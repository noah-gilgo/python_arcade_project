import pyglet.clock
from PIL import Image
from arcade import Sprite, SpriteSolidColor
from arcade.gui import UIWidget, UILabel, UIImage, Surface, UILayout, UIBoxLayout

import settings
import arcade

from sprites_and_effects_collection import SpritesAndEffectsCollection
from text_box import SpriteTextBox, SpriteTextBoxDialog
from text_texture_dicts import DWDefaultTextureDict


class TextBoxPortrait(Sprite):
    def __init__(self, texture_path: str = "", width=192, height=192):
        """
        The sprite for the textbox portrait that displays character portraits when they talk.
        :param texture_path: The path to the image file of the character portrait.
        """
        if texture_path:
            super().__init__(
                path_or_texture=texture_path,
                center_x=120,
                center_y=120,
                scale=4.0
            )

        #self.with_border(color=arcade.color.RED)

    def set_texture(self, texture_path: str = ""):
        """
        Loads a texture into the widget.
        :param texture_path: The file path of the texture to replace the old texture.
        :return:
        """
        if texture_path:
            self.texture=arcade.load_texture(texture_path)
            self.visible = True
            self.width = 192
        else:
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

class BattleTextBoxDialog(SpriteTextBoxDialog):
    def __init__(
        self,
        text: str = "",
        font_size: float = 48.0,
        character_width: int = 16,
        character_height: int = 32,
        text_spacing: int = 0,
        line_spacing: int = 8,
        rate_of_text: float = 0.036,
        text_sound_path: str = "assets/audio/dialog/snd_text.wav",
        font_name: str = "8bitoperator JVE",
        portrait_texture_path: str = "",
        sprites_and_effects_collection: SpritesAndEffectsCollection = None
    ):
        super().__init__(
            text=text,
            font_size=font_size,
            character_width=character_width,
            character_height=character_height,
            text_spacing=text_spacing,
            line_spacing=line_spacing,
            rate_of_text=rate_of_text,
            text_sound_path=text_sound_path,
            font_name=font_name,
            font_texture_dict=sprites_and_effects_collection.dw_default_font_texture_dict,
            include_starting_asterisk=True
        )

        self.portrait_texture_path = portrait_texture_path


class BattleDialogTextBox(SpriteSolidColor):
    def __init__(self, sprites_and_effects_collection: SpritesAndEffectsCollection):
        self.portrait = None  # The sprite containing the portrait
        self.text_box = SpriteTextBox(sprites_and_effects_collection=sprites_and_effects_collection)  # The text box where the text spawns.

        self.sprites_and_effects_collection = sprites_and_effects_collection

        super().__init__(
            width=settings.WINDOW_WIDTH,
            height=int(settings.WINDOW_HEIGHT / 4),
            center_x=settings.WINDOW_WIDTH / 2,
            center_y=settings.WINDOW_HEIGHT / 8,
            color=arcade.color.BLACK
        )

        self.sprites_and_effects_collection.gui_sprites_1.append(self)

        self.portrait_horizontal_padding = 24
        self.portrait_width = 192
        self.portrait_height = 192

        self.text_box_vertical_padding = 16
        self.text_box_horizontal_padding = 32

        self.text_box.height = self.height - (self.text_box_vertical_padding * 2)
        self.text_box.center_y = self.text_box.height / 2

    def load_dialog(self, text_box_dialog: BattleTextBoxDialog):
        """
        Loads the data from a text box dialog into the parent TextBox widget.
        :param text_box_dialog: the SpriteTextBoxDialog object to overwrite the current data of the TextBox
        :return: None
        """
        if self.text_box not in self.sprites_and_effects_collection.effects:
            self.sprites_and_effects_collection.effects.append(self.text_box)
        if text_box_dialog.portrait_texture_path:
            self.portrait = Sprite(
                path_or_texture=text_box_dialog.portrait_texture_path,
                scale=4.0,
                center_x=self.portrait_horizontal_padding + (self.portrait_width / 2),
                center_y=self.center_y
            )
            self.sprites_and_effects_collection.gui_sprites_1.append(self.portrait)
            self.text_box.width = settings.WINDOW_WIDTH - (((self.text_box_horizontal_padding + self.portrait_horizontal_padding) * 2) + self.portrait_width)
            self.text_box.center_x = settings.WINDOW_WIDTH / 2 + ((((self.portrait_horizontal_padding + self.text_box_horizontal_padding) * 2) + self.portrait_width) / 2)
        else:
            if isinstance(self.portrait, Sprite):
                self.portrait.kill()
                self.portrait = None
            self.text_box.width = settings.WINDOW_WIDTH - (self.text_box_horizontal_padding * 2)
            self.text_box.center_x = settings.WINDOW_WIDTH / 2

        self.text_box.load_dialog(text_box_dialog)

    def clear_dialog(self):
        """
        Clears the dialog from the text box.
        :return: None
        """
        self.text_box.clear_dialog()
        if self.text_box in self.sprites_and_effects_collection.effects:
            self.sprites_and_effects_collection.effects.remove(self.text_box)

        if isinstance(self.portrait, Sprite):
            self.portrait.kill()
            self.portrait = None

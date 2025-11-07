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
    def __init__(self, text: str,
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
        self.text = text
        """
        self._text = text
        self._talk_sprite_path = talk_sprite_path
        self._character_render_noise_path = character_render_noise_path
        self._rate_of_text = rate_of_text

        self._height = 200  # height of the text box in pixels
        self._width = settings.WINDOW_WIDTH - 100 if talk_sprite_path in (None, "") else settings.WINDOW_WIDTH - 300
        """


"""
class TextBoxLayout(UIBoxLayout):
    def __init__(self):
        super().__init__(
            x=0,
            y=0,
            vertical=False,
            size_hint=(1, 0.25),
            align="left"
        )

        self.add(TextBox())
"""


class TextBox(UIWidget):
    def __init__(self, **kwargs):
        super().__init__(
            x=0,
            y=0,
            width=settings.WINDOW_WIDTH,
            height=int(settings.WINDOW_HEIGHT / 4),
            children=[TextBoxPortrait("assets/sprites/player_characters/susie/dialog_portraits/susie_small_grin.png"),
                      TextBoxText("* Heck yeah check it out Kris I've got a dialog box.")]
        )
        self.with_background(color=arcade.uicolor.BLACK)


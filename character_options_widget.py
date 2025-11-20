import arcade
from PIL import Image
from arcade.gui import UITextureButton, UIBoxLayout, UIWidget
from arcade.types.color import Color


class BattleButton(UITextureButton):
    def __init__(self,
                 button_unselected_texture_path: str = "assets/textures/gui_graphics/battle/character_battle_buttons/battle_buttons_13.png",
                 button_selected_texture_path: str = "assets/textures/gui_graphics/battle/character_battle_buttons/battle_buttons_1.png"):

        button_unselected_image = Image.open(button_unselected_texture_path)
        texture = arcade.Texture(button_unselected_image.resize(button_unselected_image.size,
                                                                Image.Resampling.NEAREST))

        button_selected_image = Image.open(button_selected_texture_path)
        texture_hovered = arcade.Texture(button_selected_image.resize(button_selected_image.size,
                                                                      Image.Resampling.NEAREST))

        super().__init__(
            width=button_unselected_image.size[0],
            height=button_unselected_image.size[1],
            texture=texture,
            texture_hovered=texture_hovered
        )


class BattleButtonLayout(UIBoxLayout):
    def __init__(self):
        super().__init__(
            width=300,
            height=40,
            vertical=False,
            align="center"
        )


class BattleButtonLayoutBackground(UIWidget):
    def __init__(self):
        super().__init__(
            width=300,
            height=40
        )

        self.with_background(color=Color(0, 0, 0, 256))
        self.with_border(width=2, color=Color(0, 0, 256, 256))

    def set_border_color(self, color: Color):
        self.self.with_border(width=2, color=color)


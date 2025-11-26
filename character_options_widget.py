import arcade
from PIL import Image
from arcade.gui import UITextureButton, UIBoxLayout, UIWidget, UILabel, UIImage, bind, Property
from arcade.types.color import Color


class BattleHUDButton(UITextureButton):
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
            width=button_unselected_image.size[0] * 2,
            height=button_unselected_image.size[1] * 2,
            texture=texture,
            texture_hovered=texture_hovered
        )


class BattleHUDButtonLayout(UIBoxLayout):
    def __init__(self, border_color: Color = Color(0, 255, 0, 255)):
        super().__init__(
            width=440,
            height=40,
            vertical=False,
            #align="center",
            space_between=2,
            children=[
                BattleHUDButton("assets/textures/gui_graphics/battle/character_battle_buttons/battle_buttons_13.png",
                             "assets/textures/gui_graphics/battle/character_battle_buttons/battle_buttons_1.png"),
                BattleHUDButton("assets/textures/gui_graphics/battle/character_battle_buttons/battle_buttons_14.png",
                             "assets/textures/gui_graphics/battle/character_battle_buttons/battle_buttons_2.png"),
                BattleHUDButton("assets/textures/gui_graphics/battle/character_battle_buttons/battle_buttons_15.png",
                             "assets/textures/gui_graphics/battle/character_battle_buttons/battle_buttons_3.png"),
                BattleHUDButton("assets/textures/gui_graphics/battle/character_battle_buttons/battle_buttons_16.png",
                             "assets/textures/gui_graphics/battle/character_battle_buttons/battle_buttons_4.png"),
                BattleHUDButton("assets/textures/gui_graphics/battle/character_battle_buttons/battle_buttons_17.png",
                             "assets/textures/gui_graphics/battle/character_battle_buttons/battle_buttons_5.png")
            ]
        )

        self.with_background(color=Color(0, 0, 0, 255))
        #self.with_border(width=3, color=border_color)


class BattleHUDCharacterHPText(UILabel):
    def __init__(self, hp: int = 70):
        super().__init__(
            width=180,
            height=22,
            text=str(hp),
            font_name="3x5 font",
            font_size=20,
            multiline=False
        )

    def set_hp_on_character_card(self, hp: int):
        self.text = str(hp)


class BattleHUDCharacterSlashText(UIImage):
    def __init__(self):
        image = Image.open("assets/textures/gui_graphics/battle/hp_graphics/hp_slash.png")
        texture = arcade.Texture(arcade.load_image("assets/textures/gui_graphics/battle/hp_graphics/hp_slash.png").resize(image.size, Image.Resampling.NEAREST))

        super().__init__(
            texture=texture,
            width=24,
            height=20
        )


class BattleHUDCharacterMaxHPText(UILabel):
    def __init__(self, max_hp: int = 110):
        super().__init__(
            width=180,
            height=22,
            text=str(max_hp),
            font_name="3x5 font",
            font_size=20,
            multiline=False
        )

    def set_max_hp_on_character_card(self, hp: int):
        self.text = str(hp)


class BattleHUDCharacterHP(UIBoxLayout):
    def __init__(self):
        super().__init__(
            children=[
                BattleHUDCharacterHPText(),
                BattleHUDCharacterSlashText(),
                BattleHUDCharacterMaxHPText()
            ],
            vertical=False,
            align="top",
            space_between=4
        )


class BattleHUDHPLabel(UIImage):
    def __init__(self):
        image = Image.open("assets/textures/gui_graphics/battle/hp_graphics/hp.png")
        texture = arcade.Texture(
            arcade.load_image("assets/textures/gui_graphics/battle/hp_graphics/hp.png").resize(image.size,
                                                                                               Image.Resampling.NEAREST))

        super().__init__(
            texture=texture,
            width=28,
            height=16
        )


class BattleHUDHPMeter(UIWidget):
    """
    Based on the example progress bar on arcade's website.
    Link: https://api.arcade.academy/en/stable/programming_guide/gui/own_widgets.html#example-progressbar
    """

    value = Property(0.0)

    def __init__(self, hp: int = 40, max_hp: int = 100):
        super().__init__(
            width=144,
            height=18,
            size_hint=None
        )

        self.with_background(color=arcade.color.DARK_RED)

        self.hp = hp
        self.max_hp = max_hp

        self.value = self.hp / self.max_hp
        self.color = arcade.color.NEON_GREEN

        # trigger a render when the value changes
        bind(self, "value", self.trigger_render)

    def do_render(self, surface: arcade.gui.Surface) -> None:
        self.prepare_render(surface)

        arcade.draw_lbwh_rectangle_filled(
            0,
            0,
            self.content_width * self.value,
            self.content_height,
            self.color,
        )


class BattleHUDHPMeterLayout(UIBoxLayout):
    """
    Contains the HP meter and its associated HP label.
    """
    def __init__(self):
        super().__init__(
            width=200,
            children=[
                BattleHUDHPLabel(),
                BattleHUDHPMeter()
            ],
            vertical=False,
            space_between=8
        )


class BattleHUDHPData(UIBoxLayout):
    """
    Contains all of the HP data on the character's battle HUD card.
    """
    def __init__(self):
        super().__init__(
            width=200,
            children=[
                BattleHUDCharacterHP(),
                BattleHUDHPMeterLayout()
            ],
            vertical=True,
            align="right"
        )


class BattleHUDCharacterIcon(UIImage):
    """
    Contains the character icon in the character's battle HUD card.
    """

    def __init__(self, texture_path: str = "assets/sprites/player_characters/kris/battle_hud/kris_hud_default_face_icon.png"):
        """
        The widget for the textbox portrait that displays character portraits when they talk.
        :param texture_path: The path to the image file of the character portrait.
        :param dimensions: A tuple/list containing the x, y, width, and height dimensions of the portrait, respectively
        """

        image = Image.open(texture_path)
        texture = arcade.Texture(arcade.load_image(texture_path).resize(image.size, Image.Resampling.NEAREST))

        super().__init__(
            texture=texture,
            width=64,
            height=48
        )


class BattleHUDCharacterName(UILabel):
    """
    Contains the name of the character in the character's battle HUD card.
    """
    def __init__(self, name: str = "Kris"):
        super().__init__(
            width=150,
            height=48,
            text=name.upper(),
            font_name="""Roarin'""",
            font_size=48
        )


class BattleHUDCharacterIconAndName(UIBoxLayout):
    """
    Layout for both the character icon and name.
    """

    def __init__(self):
        super().__init__(
            width=220,
            children=[
                BattleHUDCharacterIcon(),
                BattleHUDCharacterName()
            ],
            vertical=False,
            space_between=18,
            align="right"
        )


class BattleHUDCharacterData(UIBoxLayout):
    """
    Card containing the character icon, name, and HP data.
    """

    def __init__(self, border_color: Color = Color(0, 255, 0, 255)):
        super().__init__(
            width=380,
            height=72,
            children=[
                BattleHUDCharacterIconAndName(),
                BattleHUDHPData()
            ],
            vertical=False,
            space_between=24
        )

        #self.with_background(color=Color(0, 0, 0, 255))
        #self.with_border(width=3, color=border_color)


class BattleHUDCharacterClamshell(UIBoxLayout):
    """
    Card containing the player battle HUD data and buttons.
    Built to automatically display the
    """
    def __init__(self, border_color: Color = Color(0, 255, 0, 255)):
        super().__init__(
            children=[
                BattleHUDCharacterData(),
                BattleHUDButtonLayout()
            ],
            width=360,
            height=144,
            vertical=True
        )

        self.with_background(color=Color(0, 0, 0, 255))
        self.with_border(width=3, color=border_color)

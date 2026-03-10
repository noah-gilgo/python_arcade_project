import arcade
from PIL import Image
from arcade.gui import UITextureButton, UIBoxLayout, UIWidget, UILabel, UIImage, bind, Property, UIGridLayout, \
    UIKeyPressEvent, UIKeyEvent, Surface
from arcade.gui.widgets import FocusMode
from arcade.shape_list import create_line
from arcade.types.color import Color

import player_character
import settings
from spells import Spell


class BattleHUDButton(UITextureButton):
    def __init__(self,
                 name="default",
                 button_unselected_texture_path: str = "assets/textures/gui_graphics/battle/character_battle_buttons/battle_buttons_13.png",
                 button_selected_texture_path: str = "assets/textures/gui_graphics/battle/character_battle_buttons/battle_buttons_1.png"):

        self.button_unselected_image = Image.open(button_unselected_texture_path).convert('RGBA')
        self.texture_unfocused = arcade.Texture(self.button_unselected_image.resize(self.button_unselected_image.size,
                                                                                    Image.Resampling.NEAREST))

        self.button_selected_image = Image.open(button_selected_texture_path).convert('RGBA')
        self.texture_focused = arcade.Texture(self.button_selected_image.resize(self.button_selected_image.size,
                                                                                Image.Resampling.NEAREST))

        super().__init__(
            width=self.button_unselected_image.size[0] * 2,
            height=self.button_unselected_image.size[1] * 2,
            texture=self.texture_unfocused,
            texture_hovered=self.texture_focused
        )

        self.name = name
        self.focus_mode = FocusMode(2)

    """
    def focus(self):
        # Highlights the selected button.
        self.texture = self.texture_focused

    def unfocus(self):
        # De-highlights the selected button.
        self.texture = self.texture_unfocused
    """

    def do_render_focus(self, surface: Surface):
        pass


class BattleHUDButtonLayout(UIBoxLayout):
    def __init__(self, character: player_character.PlayerCharacter):
        if character.knows_magic:
            buttons = [
                BattleHUDButton("FIGHT",
                                "assets/textures/gui_graphics/battle/character_battle_buttons/battle_buttons_13.png",
                                "assets/textures/gui_graphics/battle/character_battle_buttons/battle_buttons_1.png"),
                BattleHUDButton("MAGIC",
                                "assets/textures/gui_graphics/battle/character_battle_buttons/battle_buttons_18.png",
                                "assets/textures/gui_graphics/battle/character_battle_buttons/battle_buttons_6.png"),
                BattleHUDButton("ITEM",
                                "assets/textures/gui_graphics/battle/character_battle_buttons/battle_buttons_15.png",
                                "assets/textures/gui_graphics/battle/character_battle_buttons/battle_buttons_3.png"),
                BattleHUDButton("SPARE",
                                "assets/textures/gui_graphics/battle/character_battle_buttons/battle_buttons_16.png",
                                "assets/textures/gui_graphics/battle/character_battle_buttons/battle_buttons_4.png"),
                BattleHUDButton("DEFEND",
                                "assets/textures/gui_graphics/battle/character_battle_buttons/battle_buttons_17.png",
                                "assets/textures/gui_graphics/battle/character_battle_buttons/battle_buttons_5.png")
            ]
        else:
            buttons = [
                BattleHUDButton("FIGHT",
                                "assets/textures/gui_graphics/battle/character_battle_buttons/battle_buttons_13.png",
                                "assets/textures/gui_graphics/battle/character_battle_buttons/battle_buttons_1.png"),
                BattleHUDButton("ACT",
                                "assets/textures/gui_graphics/battle/character_battle_buttons/battle_buttons_14.png",
                                "assets/textures/gui_graphics/battle/character_battle_buttons/battle_buttons_2.png"),
                BattleHUDButton("ITEM",
                                "assets/textures/gui_graphics/battle/character_battle_buttons/battle_buttons_15.png",
                                "assets/textures/gui_graphics/battle/character_battle_buttons/battle_buttons_3.png"),
                BattleHUDButton("SPARE",
                                "assets/textures/gui_graphics/battle/character_battle_buttons/battle_buttons_16.png",
                                "assets/textures/gui_graphics/battle/character_battle_buttons/battle_buttons_4.png"),
                BattleHUDButton("DEFEND",
                                "assets/textures/gui_graphics/battle/character_battle_buttons/battle_buttons_17.png",
                                "assets/textures/gui_graphics/battle/character_battle_buttons/battle_buttons_5.png")
            ]

        super().__init__(
            width=380,
            height=60,
            vertical=False,
            space_between=2,
            align="bottom",
            children=buttons
        )

        self.focus_mode = FocusMode(0)

        self.with_background(color=Color(0, 0, 0, 255))
        # self.with_border(width=3, color=character.battle_ui_color)
        self.with_padding(left=33, right=33)

        self._selected_button_index = 0

        # self.children[0].focused = True
        # for i in range(1, len(self.children)):
        #     self.children[i].focused = False

    """
    def on_event(self, event):
        if isinstance(event, UIKeyPressEvent):
            print("key press event detected")
            if event.symbol == arcade.key.RIGHT:
                print("event fired")
                for i in range(len(self.children)):
                    if self.children[i].focused:
                        self.children[i].focused = False
                        self.children[int((i + 1) % len(self.children))].focused = True
                        return

            if event.symbol == arcade.key.LEFT:
                for i in range(len(self.children)):
                    if self.children[i].focused:
                        self.children[i].focused = False
                        self.children[int((i - 1) % len(self.children))].focused = True
                        return
    """


class BattleHUDCharacterHPText(UILabel):
    def __init__(self, character: player_character.PlayerCharacter):
        super().__init__(
            width=180,
            height=21,
            text=str(character.hp),
            font_name="3x5 font",
            font_size=21,
            multiline=False
        )
        self.focus_mode = FocusMode(0)

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
        self.focus_mode = FocusMode(0)


class BattleHUDCharacterMaxHPText(UILabel):
    def __init__(self, character: player_character.PlayerCharacter):
        super().__init__(
            width=180,
            height=21,
            text=str(character.max_hp),
            font_name="3x5 font",
            font_size=21,
            multiline=False
        )
        self.focus_mode = FocusMode(0)

    def set_max_hp_on_character_card(self, hp: int):
        self.text = str(hp)


class BattleHUDCharacterHP(UIBoxLayout):
    def __init__(self, character: player_character.PlayerCharacter):
        super().__init__(
            children=[
                BattleHUDCharacterHPText(character),
                BattleHUDCharacterSlashText(),
                BattleHUDCharacterMaxHPText(character)
            ],
            vertical=False,
            align="top",
            space_between=4,
            width=200
        )
        self.focus_mode = FocusMode(0)


class BattleHUDHPLabel(UIImage):
    def __init__(self):
        image = Image.open("assets/textures/gui_graphics/battle/hp_graphics/hp.png")
        texture = arcade.Texture(
            arcade.load_image("assets/textures/gui_graphics/battle/hp_graphics/hp.png").resize(image.size,
                                                                                               Image.Resampling.NEAREST))

        super().__init__(
            texture=texture,
            width=28,
            height=18
        )
        self.focus_mode = FocusMode(0)


class BattleHUDHPMeter(UIWidget):
    """
    Based on the example progress bar on arcade's website.
    Link: https://api.arcade.academy/en/stable/programming_guide/gui/own_widgets.html#example-progressbar
    """

    value = Property(0.0)

    def __init__(self, character: player_character.PlayerCharacter):
        super().__init__(
            width=140,
            height=18,
            size_hint=None
        )
        self.focus_mode = FocusMode(0)

        self.with_background(color=arcade.color.DARK_RED)

        self.hp = character.hp
        self.max_hp = character.max_hp

        self.value = self.hp / self.max_hp
        self.color = character.battle_ui_color

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
    def __init__(self, character: player_character.PlayerCharacter):
        super().__init__(
            width=187,
            height=80,
            children=[
                BattleHUDHPLabel(),
                BattleHUDHPMeter(character)
            ],
            vertical=False,
            space_between=8,
            align="center"
        )
        self.focus_mode = FocusMode(0)


class BattleHUDHPData(UIBoxLayout):
    """
    Contains all of the HP data on the character's battle HUD card.
    """
    def __init__(self, character: player_character.PlayerCharacter):
        super().__init__(
            width=220,
            height=80,
            children=[
                BattleHUDCharacterHP(character),
                BattleHUDHPMeterLayout(character)
            ],
            vertical=True,
            align="right"
        )
        self.focus_mode = FocusMode(0)


class BattleHUDCharacterIcon(UIImage):
    """
    Contains the character icon in the character's battle HUD card.
    """

    def __init__(self, character: player_character.PlayerCharacter):
        """
        The widget for the textbox portrait that displays character portraits when they talk.
        :param texture_path: The path to the image file of the character portrait.
        :param dimensions: A tuple/list containing the x, y, width, and height dimensions of the portrait, respectively
        """

        texture_path = "assets/sprites/player_characters/" + character.sprite_folder_name + "/battle_hud/hud_default_face_icon.png"

        image = Image.open(texture_path)
        texture = arcade.Texture(arcade.load_image(texture_path).resize(image.size, Image.Resampling.NEAREST))

        super().__init__(
            texture=texture,
            width=64,
            height=48
        )
        self.focus_mode = FocusMode(0)


class BattleHUDCharacterName(UILabel):
    """
    Contains the name of the character in the character's battle HUD card.
    """
    def __init__(self, character: player_character.PlayerCharacter):
        super().__init__(
            width=200,
            height=80,
            text=character.name.upper(),
            font_name="""Roarin'""",
            font_size=48,
            align="center"
        )
        self.focus_mode = FocusMode(0)


class BattleHUDCharacterIconAndName(UIBoxLayout):
    """
    Layout for both the character icon and name.
    """

    def __init__(self, character: player_character.PlayerCharacter):
        super().__init__(
            width=164,
            height=80,
            children=[
                BattleHUDCharacterIcon(character),
                BattleHUDCharacterName(character)
            ],
            vertical=False,
            space_between=18,
            align="center"
        )
        self.focus_mode = FocusMode(0)


class BattleHUDCharacterData(UIBoxLayout):
    """
    Card containing the character icon, name, and HP data.
    """

    def __init__(self, character: player_character.PlayerCharacter):
        super().__init__(
            width=408,
            height=96,
            children=[
                BattleHUDCharacterIconAndName(character),
                BattleHUDHPData(character)
            ],
            vertical=False,
            space_between=24,
            align="center"
        )
        self.focus_mode = FocusMode(0)

        #self.with_background(color=Color(0, 0, 0, 255))
        self.with_border(width=3, color=character.battle_ui_color)
        self.with_padding(top=8, left=12, bottom=8, right=12)


class BattleHUDCharacterClamshell(UIBoxLayout):
    """
    Card containing the player battle HUD data and buttons.
    Built to automatically display the character data.
    """
    def __init__(self, character: player_character.PlayerCharacter):
        # This is the default data for a newly created clamshell. All of the child components of the clamshell
        # will read from this data and render themselves in accordance with it.
        self.player_character = character
        self._color = character.battle_ui_color
        self._character_icon_path = "assets/sprites/player_characters/" + character.sprite_folder_name + "/battle_hud/hud_default_face_icon.png"
        self._character_name = character.name
        self._hp = character.hp
        self._max_hp = character.max_hp

        super().__init__(
            children=[
                BattleHUDCharacterData(character),
                BattleHUDButtonLayout(character)
            ],
            width=408,
            height=240,
            vertical=True
        )
        self.focus_mode = FocusMode(0)

        self.with_background(color=Color(0, 0, 0, 255))
        #self.with_border(width=3, color=character.battle_ui_color)
        #self.with_padding(top=2, right=8, bottom=0, left=8)


class BattleHUDCharacterClamshellDisplay(UIGridLayout):
    """
    The part of the screen that renders the character data clamshells.
    """
    def __init__(self, player_characters: list[player_character]):

        self._horizontal_spacing = 10
        self._clamshell_width = BattleHUDCharacterClamshell(player_characters[0]).width
        width = (self._clamshell_width * len(player_characters)) + (self._horizontal_spacing * (len(player_characters) - 1))
        x_offset = int((settings.WINDOW_WIDTH - width) / 2)

        super().__init__(
            children=[],
            x=x_offset,
            y=int(settings.WINDOW_HEIGHT / 4.5),
            width=width,
            align_vertical="center",
            align_horizontal="center",
            horizontal_spacing=self._horizontal_spacing,
            row_count=1,
            column_count=len(player_characters)
        )
        self.focus_mode = FocusMode(0)

        self.center_x = int(settings.WINDOW_WIDTH / 2)

        self.x = int(self.center_x - (self.width / 2))
        self.y = int(self.center_y - (self.height / 2))

        self.player_characters = player_characters

        col_index = 0
        for character in player_characters:
            self.add(
                BattleHUDCharacterClamshell(character),
                column=col_index,
                row=0
            )
            col_index += 1

    """
    def draw(self):
        for character in self.player_characters:
            line = create_line(
                start_x=self.x,
                start_y=self.y,
                end_x=self.x,
                end_y=self.y + self.height,
                color=(character.battle_ui_color.r,
                       character.battle_ui_color.g,
                       character.battle_ui_color.b,
                       character.battle_ui_color.a),
                line_width=3
            )

            line.draw()
    """


class SpellListOption(UILabel):
    def __init__(self, spell: Spell, color: Color = arcade.color.WHITE):
        super().__init__(
            text=spell.name,
            height=64,
            font_name="8bitoperator JVE",
            font_size=48,
            text_color=color
        )

        self.focus_mode = FocusMode(2)
        self.soul_texture = arcade.load_texture("assets/sprites/soul/soul.png")

    """
    def do_render_focus(self, surface: arcade.gui.Surface):
        # surface is provided by Arcade
        x = self.left - 20
        y = self.center_y

        # draw the texture on the widget’s surface
        arcade.draw_texture_rect(
            self.soul_texture,
            arcade.LBWH(
                x,
                y - 8,
                16,
                16
            )
        )
    """


class SpellListLayout(UIGridLayout):
    def __init__(self, character: player_character.PlayerCharacter):
        super().__init__(
            x=72,
            y=-32,
            width=(2 * settings.WINDOW_WIDTH) / 3,
            height=int(settings.WINDOW_HEIGHT / 4),
            row_count=3,
            column_count=2,
            align_horizontal="left",
            horizontal_spacing=100
        )

        action_color = Color.from_iterable([
            int((character.battle_ui_color.r + 255) / 2),
            int((character.battle_ui_color.g + 255) / 2),
            int((character.battle_ui_color.b + 255) / 2),
            int(character.battle_ui_color.a)
        ])

        if character.spells:
            self.add(
                SpellListOption(
                    Spell(
                        name=character.name[0].upper() + "-Action"
                    ),
                    color=action_color
                ),
                column=0,
                row=0
            )

            spell_index = 1
            for spell in character.spells:
                row_index = spell_index // 2
                col_index = spell_index % 2
                self.add(
                    SpellListOption(spell),
                    column=col_index,
                    row=row_index
                )
                spell_index += 1


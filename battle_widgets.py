import math

import arcade
import pyglet.clock
from PIL import Image, ImageChops
from PIL.Image import Resampling
from arcade import LBWH
from arcade.gui import UITextureButton, UIBoxLayout, UIWidget, UILabel, UIImage, bind, Property, UIGridLayout, \
    UIKeyPressEvent, UIKeyEvent, Surface, UIAnchorLayout
from arcade.gui.widgets import FocusMode, UISpace, UILayout
from arcade.shape_list import create_line
from arcade.types.color import Color

import non_player_character
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
        self.player_character = character
        if self.player_character.knows_magic:
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
            width=420,
            height=72,
            vertical=False,
            space_between=2,
            align="center",
            children=buttons
        )

        self.focus_mode = FocusMode(0)

        self.with_background(color=Color(0, 0, 0, 255))
        # self.with_border(width=3, color=character.battle_ui_color)
        self.with_padding(left=50, right=50)

        self.delta_time = 0
        self.lines_coming_from_left = []
        self.lines_coming_from_right = []
        self.character_color_r = self.player_character.battle_ui_color.r
        self.character_color_g = self.player_character.battle_ui_color.g
        self.character_color_b = self.player_character.battle_ui_color.b
        self.line_lifetime = 2
        self.velocity_magnifier = 0.1
        self.alpha_loss_magnifier = 4

        for i in range(6):
            time = (self.line_lifetime * ((i + 1) / 5))
            distance = (time ** 2) * (self.width * self.velocity_magnifier)
            start_x = distance
            end_x = distance
            alpha = min(255, int(max(255 - (distance * self.alpha_loss_magnifier), 0)))
            self.lines_coming_from_left.append(
                [start_x, 0, end_x, self.height,
                 [self.character_color_r, self.character_color_g, self.character_color_b, alpha], 5, time]
            )

        self.lines_coming_from_left.pop(2)

        for i in range(6):
            time = (self.line_lifetime * ((i + 1) / 5))
            distance = self.width - ((time ** 2) * (self.width * self.velocity_magnifier))
            start_x = distance
            end_x = distance
            alpha = min(255, int(max(255 - ((self.width - distance) * self.alpha_loss_magnifier), 0)))
            self.lines_coming_from_right.append(
                [start_x, 0, end_x, self.height,
                 [self.character_color_r, self.character_color_g, self.character_color_b, alpha], 5, time]
            )

        self.lines_coming_from_right.pop(2)

    def on_update(self, dt):
        self.delta_time = dt
        self.trigger_render()

    def do_render(self, surface: Surface):
        super().do_render(surface)
        arcade.draw_rect_filled(
            rect=self.rect,
            color=[0, 0, 0]
        )

        arcade.draw_line(0, 0, 0, self.height,
                         [self.character_color_r, self.character_color_g, self.character_color_b, 255], 8)

        arcade.draw_line(self.width, 0, self.width, self.height,
                         [self.character_color_r, self.character_color_g, self.character_color_b, 255], 8)

        for line in self.lines_coming_from_left:
            # Check if the line is older than the max line lifetime
            if line[6] >= self.line_lifetime:
                # Set line back to initial conditions
                line[0] = 0
                line[2] = 0
                line[4][3] = 255
                line[6] -= self.line_lifetime
            else:
                # Progress the line animation
                line[6] += self.delta_time
                distance = (line[6] ** 2) * (self.width * self.velocity_magnifier)
                line[0] = distance
                line[2] = distance
                line[4][3] = min(255, int(max(255 - (distance * self.alpha_loss_magnifier), 0)))
            arcade.draw_line(line[0], line[1], line[2], line[3], line[4], line[5])
            # print("start x = " + str(line[0]) + ", end x = " + str(line[2]) + ", time = " + str(line[6]))

        for line in self.lines_coming_from_right:
            # Check if the line is older than the max line lifetime
            if line[6] >= self.line_lifetime:
                # Set line back to initial conditions
                line[0] = self.width
                line[2] = self.width
                line[4][3] = 255
                line[6] -= self.line_lifetime
            else:
                # Progress the line animation
                line[6] += self.delta_time
                distance = self.width - ((line[6] ** 2) * (self.width * self.velocity_magnifier))
                line[0] = distance
                line[2] = distance
                line[4][3] = min(255, int(max(255 - ((self.width - distance) * self.alpha_loss_magnifier), 0)))
            arcade.draw_line(line[0], line[1], line[2], line[3], line[4], line[5])


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
            width=420,
            height=84,
            children=[
                BattleHUDCharacterIconAndName(character),
                BattleHUDHPData(character)
            ],
            vertical=False,
            space_between=24,
            align="center",
            size_hint=None
        )
        self.focus_mode = FocusMode(0)

        self.with_background(color=Color(0, 0, 0, 255))
        self.with_border(width=10, color=character.battle_ui_color)
        self.with_padding(top=8, left=12, bottom=8, right=12)


class BattleHUDCharacterClamshell(UILayout):
    """
    Card containing the player battle HUD data and buttons.
    Built to automatically display the character data.
    """
    def __init__(self, character: player_character.PlayerCharacter, is_focused: bool = False):
        # This is the default data for a newly created clamshell. All of the child components of the clamshell
        # will read from this data and render themselves in accordance with it.
        self.player_character = character
        self._color = character.battle_ui_color
        self._character_icon_path = "assets/sprites/player_characters/" + character.sprite_folder_name + "/battle_hud/hud_default_face_icon.png"
        self._character_name = character.name
        self._hp = character.hp
        self._max_hp = character.max_hp
        self.battle_hud_character_data = BattleHUDCharacterData(character)
        self.battle_hud_button_layout = BattleHUDButtonLayout(character)

        super().__init__(
            children=[],
            x=0,
            width=420,
            height=180
        )

        self.add(self.battle_hud_button_layout)
        self.add(self.battle_hud_character_data)

        self.focus_mode = FocusMode(0)
        #self.with_border(width=3, color=character.battle_ui_color)
        #self.with_padding(top=2, right=8, bottom=0, left=8)

        self.is_focused = is_focused

        self.character_display_transition_time = 0
        self.hud_lowered_center_y = self.battle_hud_character_data.center_y
        self.distance_hud_raised = 78
        self.hud_raised_center_y = self.battle_hud_character_data.center_y + self.distance_hud_raised
        self.hud_raise_animation_time = 0.2
        self.inverse_of_hud_raise_animation_time = 1 / self.hud_raise_animation_time

        self.is_instantiated = False

    def on_update(self, dt):
        self.trigger_render()

    def do_layout(self):
        super().do_layout()

        rect = self.rect

        if not self.is_instantiated:
            if self.is_focused:
                self.battle_hud_character_data.center_y = rect.center_y + self.distance_hud_raised
                self.children[1].with_border(width=3, color=self.player_character.battle_ui_color)
            else:
                self.battle_hud_character_data.center_y = rect.center_y
                self.children[1].with_border(width=0, color=self.player_character.battle_ui_color)
            self.is_instantiated = True

        self.battle_hud_character_data.center_x = rect.center_x

        self.battle_hud_button_layout.center_x = rect.center_x
        self.battle_hud_button_layout.center_y = rect.center_y


    """
    def do_render_focus(self, surface: Surface):
        self.children[0].visible = False
    """

    def move_up_character_display_slightly(self, dt):
        self.character_display_transition_time += dt
        new_hud_center_y = self.hud_lowered_center_y + (-self.distance_hud_raised * (self.inverse_of_hud_raise_animation_time * self.character_display_transition_time) * ((self.inverse_of_hud_raise_animation_time * self.character_display_transition_time) - 2))
        self.battle_hud_character_data.center_y = new_hud_center_y
        if self.character_display_transition_time > self.hud_raise_animation_time:
            self.battle_hud_character_data.center_y = self.hud_raised_center_y
            self.character_display_transition_time = 0
            pyglet.clock.unschedule(self.move_up_character_display_slightly)

    def move_up_character_data_display(self):
        if self.is_focused:
            self.hud_raised_center_y = self.battle_hud_character_data.center_y
            self.hud_lowered_center_y = self.battle_hud_character_data.center_y - self.distance_hud_raised
        else:
            self.hud_lowered_center_y = self.battle_hud_character_data.center_y
            self.hud_raised_center_y = self.battle_hud_character_data.center_y + self.distance_hud_raised

        pyglet.clock.schedule_interval(self.move_up_character_display_slightly, 1/60)

    def focus(self):
        """ Moves the character data display up so the buttons can be shown. """
        self.move_up_character_data_display()
        self.is_focused = True
        self.battle_hud_character_data.with_border(width=3, color=self.player_character.battle_ui_color)

    def move_down_character_display_slightly(self, dt):
        self.character_display_transition_time += dt
        new_hud_center_y = self.hud_raised_center_y - (-self.distance_hud_raised * (self.inverse_of_hud_raise_animation_time * self.character_display_transition_time) * ((self.inverse_of_hud_raise_animation_time * self.character_display_transition_time) - 2))
        self.battle_hud_character_data.center_y = new_hud_center_y
        if self.character_display_transition_time > self.hud_raise_animation_time:
            self.battle_hud_character_data.center_y = self.hud_lowered_center_y
            self.character_display_transition_time = 0
            pyglet.clock.unschedule(self.move_down_character_display_slightly)

    def move_down_character_data_display(self):
        if self.is_focused:
            self.hud_raised_center_y = self.battle_hud_character_data.center_y
            self.hud_lowered_center_y = self.battle_hud_character_data.center_y - self.distance_hud_raised
        else:
            self.hud_lowered_center_y = self.battle_hud_character_data.center_y
            self.hud_raised_center_y = self.battle_hud_character_data.center_y + self.distance_hud_raised

        pyglet.clock.schedule_interval(self.move_down_character_display_slightly, 1/60)

    def unfocus(self):
        """ Moves the character data display up so the buttons can be shown. """
        self.move_down_character_data_display()
        self.is_focused = False
        self.battle_hud_character_data.with_border(width=0, color=self.player_character.battle_ui_color)


class BattleHUDCharacterClamshellDisplay(UIBoxLayout):
    """
    The part of the screen that renders the character data clamshells.
    """
    def __init__(self, player_characters: list[player_character]):

        self._horizontal_spacing = 0
        self._clamshell_width = BattleHUDCharacterClamshell(player_characters[0]).width
        width = (self._clamshell_width * len(player_characters)) + (self._horizontal_spacing * (len(player_characters) - 1))
        x_offset = int((settings.WINDOW_WIDTH - width) / 2)

        super().__init__(
            children=[],
            x=x_offset,
            y=int(settings.WINDOW_HEIGHT / 5.1) - 2,
            width=width,
            align="center",
            space_between=self._horizontal_spacing,
            vertical=False,
            size_hint=None
        )
        self.focus_mode = FocusMode(0)

        self.center_x = int(settings.WINDOW_WIDTH / 2)

        self.x = int(self.center_x - (self.width / 2))
        self.y = int(self.center_y - (self.height / 2))

        self.player_characters = player_characters

        is_clamshell_focused = True

        for character in player_characters:
            clamshell = BattleHUDCharacterClamshell(character, is_clamshell_focused)
            self.add(clamshell)
            is_clamshell_focused = False

    def do_layout(self):
        self.center_x = int(settings.WINDOW_WIDTH / 2)
        super().do_layout()

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
            text="     " + spell.name,
            width=400,
            height=64,
            font_name="8bitoperator JVE",
            font_size=48,
            text_color=color,
            size_hint=None
        )

        self.spell = spell
        self.focus_mode = FocusMode(2)
        self.soul_sprite = arcade.Sprite(path_or_texture="assets/sprites/soul/soul.png", scale=1.0)

    def do_render_focus(self, surface: arcade.gui.Surface):
        x = self.left - 20
        y = self.center_y

        self.prepare_render(surface)

        arcade.draw_sprite_rect(
            self.soul_sprite,
            arcade.XYWH(
                16,
                32,
                32,
                32
            ),
            pixelated=True
        )


class SpellList(UIGridLayout):
    def __init__(self, character: player_character.PlayerCharacter):
        super().__init__(
            x=36,
            y=0,
            width=(2 * settings.WINDOW_WIDTH) / 3,
            height=int(settings.WINDOW_HEIGHT / 4) - 30,
            row_count=3,
            column_count=2,
            align_horizontal="left",
            alight_vertical="center",
            horizontal_spacing=100,
            size_hint=None
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


class SpellDescriptionLabel(UILabel):
    def __init__(self, spell_description: str = ""):
        super().__init__(
            size_hint=(None, None),
            width=400,
            height=140,
            font_name="8bitoperator JVE",
            font_size=48,
            text_color=arcade.color.GRAY,
            text=spell_description,
            multiline=True
        )


class SpellTPCostLabel(UILabel):
    def __init__(self, tp_cost: int = 0):
        super().__init__(
            width=400,
            height=60,
            font_name="8bitoperator JVE",
            font_size=48,
            text_color=arcade.color.NEON_CARROT,
            text="" if not tp_cost else str(tp_cost) + "% TP"
        )


class SpellDescriptionAndTPCost(UIBoxLayout):
    def __init__(self, spell: Spell = None):
        super().__init__(
            width=400,
            height=300,
            children=[
                SpellDescriptionLabel("" if not spell or not spell.description else spell.description),
                SpellTPCostLabel(0 if not spell or not spell.tp_cost else spell.tp_cost)
            ],
            align="left"
        )

    def update_spell_data(self, spell: Spell = None):
        """ Updates the spell data shown in the layout. """
        self.children[0].text = "" if not spell or not spell.description else spell.description
        self.children[1].text = "" if not spell or not spell.tp_cost else str(spell.tp_cost) + "% TP"


class SpellSelect(UIBoxLayout):
    def __init__(self, character: player_character.PlayerCharacter):
        view_width = settings.WINDOW_WIDTH - 40

        spell_list = SpellList(character)
        spell_description = SpellDescriptionAndTPCost()

        self.space_between = view_width - (spell_list.width + spell_description.width)

        super().__init__(
            x=36,
            y=0,
            width=view_width,
            height=int(settings.WINDOW_HEIGHT / 4),
            vertical=False,
            space_between=self.space_between,
            children=[
                SpellList(character),
                SpellDescriptionAndTPCost()
            ],
            align="center"
        )
        self.center_x = int(settings.WINDOW_WIDTH / 2)

    def update_spell_data(self, spell: Spell = None):
        """ Updates the spell data shown in the layout. """
        self.children[1].update_spell_data(spell)

    def calculate_space_between(self):
        """ Calculate the space between the spell list and the spell description card. """
        view_width = self.width

        spell_list = self.children[0]
        spell_description = self.children[1]

        self.space_between = view_width - (spell_list.width + spell_description.width)

    def do_layout(self):
        self.center_x = int(settings.WINDOW_WIDTH / 2)

        super().do_layout()


class EnemySelectInstanceName(UILabel):
    def __init__(self, enemy: non_player_character.NonPlayerCharacter):
        text_color = arcade.color.WHITE
        if enemy.tired >= 100:
            text_color = Color(0, 178, 255)
        if enemy.mercy >= 100:
            text_color = arcade.color.YELLOW

        super().__init__(
            text="     " + enemy.name,
            width=240,
            height=56,
            font_name="8bitoperator JVE",
            font_size=48,
            text_color=text_color,
            size_hint=None,
        )


class EnemySelectInstanceIcons(UIBoxLayout):
    def __init__(self, enemy: non_player_character.NonPlayerCharacter):
        spare_icon_texture = arcade.load_texture("assets/textures/gui_graphics/battle/icons/spare_icon.png")
        tired_icon_texture = arcade.load_texture("assets/textures/gui_graphics/battle/icons/tired_icon.png")

        spare_icon = UIImage(texture=spare_icon_texture, width=32, height=32)
        tired_icon = UIImage(texture=tired_icon_texture, width=32, height=32)
        tired_label = UILabel(
            text="(Tired)",
            width=100,
            height=52,
            font_name="8bitoperator JVE",
            font_size=48,
            text_color=arcade.color.GRAY)

        spare_icon.visible = False
        tired_icon.visible = False
        tired_label.visible = False

        if enemy.mercy >= 100:
            spare_icon.visible = True
        if enemy.tired >= 100:
            tired_icon.visible = True
            tired_label.visible = True

        super().__init__(
            width=400,
            height=64,
            children=[spare_icon, tired_icon, tired_label],
            align="center",
            vertical=False,
            size_hint=None,
            space_between=8
        )


class EnemySelectInstanceHPMeter(UIWidget):
    value = Property(0.0)

    def __init__(self, enemy: non_player_character.NonPlayerCharacter):
        super().__init__(
            width=180,
            height=36,
            size_hint=None
        )
        self.enemy = enemy
        self.focus_mode = FocusMode(0)

        self.with_background(color=arcade.color.DARK_RED)

        self.hp = enemy.hp
        self.max_hp = enemy.max_hp

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

        super().do_render(surface)

        text_sprite = arcade.create_text_sprite(
            text=" " + self.enemy.get_hp_percentage_as_string(),
            color=arcade.color.WHITE,
            font_name="8bitoperator JVE",
            font_size=36
        )

        arcade.draw_sprite_rect(
            sprite=text_sprite,
            rect=LBWH(
                0,
                -4,
                width=text_sprite.width * 1.4,
                height=self.content_height + 8
            ),
            pixelated=True
        )


class EnemySelectInstanceMercyMeter(UIWidget):
    value = Property(0.0)

    def __init__(self, enemy: non_player_character.NonPlayerCharacter):
        self.enemy = enemy

        super().__init__(
            width=180,
            height=36,
            size_hint=None
        )

        self.with_background(color=arcade.color.ORANGE)

        self.mercy = enemy.mercy

        self.value = self.mercy / 100
        self.color = arcade.color.YELLOW

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

        super().do_render(surface)

        text_sprite = arcade.create_text_sprite(
            text=" " + self.enemy.get_mercy_percentage_as_string(),
            color=arcade.color.DARK_RED,
            font_name="8bitoperator JVE",
            font_size=36
        )

        arcade.draw_sprite_rect(
            sprite=text_sprite,
            rect=LBWH(
                0,
                -4,
                width=text_sprite.width * 1.4,
                height=self.content_height + 8
            ),
            pixelated=True
        )


class EnemySelectInstance(UIBoxLayout):
    def __init__(self, enemy: non_player_character.NonPlayerCharacter):
        super().__init__(
            width=int(settings.WINDOW_WIDTH - 40),
            height=40,
            vertical=False,
            children=[
                EnemySelectInstanceName(enemy),
                EnemySelectInstanceIcons(enemy),
                EnemySelectInstanceHPMeter(enemy),
                EnemySelectInstanceMercyMeter(enemy)
            ],
            space_between=40
        )
        self.enemy = enemy

        self.focus_mode = FocusMode(2)
        self.soul_sprite = arcade.Sprite(path_or_texture="assets/sprites/soul/soul.png", scale=1.0)

    def do_render_focus(self, surface: arcade.gui.Surface):
        x = self.left - 20
        y = self.center_y

        arcade.draw_sprite_rect(
            self.soul_sprite,
            arcade.XYWH(
                16,
                28,
                32,
                32
            ),
            pixelated=True
        )

"""
class EnemySelectInstanceWidget(UIWidget):
    def __init__(self, enemy: non_player_character.NonPlayerCharacter):
        super().__init__(
            width=int(settings.WINDOW_WIDTH * .9),
            height=40
        )

        self.enemy_select_instance = EnemySelectInstance(enemy)

        self.focus_mode = FocusMode(2)
        self.soul_sprite = arcade.Sprite(path_or_texture="assets/sprites/soul/soul.png", scale=1.0)

    def do_render(self, surface):
        self.enemy_select_instance.do_render(surface)

    def do_render_focus(self, surface: arcade.gui.Surface):
        x = self.left - 20
        y = self.center_y

        arcade.draw_sprite_rect(
            self.soul_sprite,
            arcade.XYWH(
                16,
                32,
                32,
                32
            ),
            pixelated=True
        )
"""


class EnemySelectMeterColumnLabel(UIWidget):
    def __init__(self, text: str):
        super().__init__(
            width=220,
            height=32,
            size_hint=None
        )
        self.text = text

    def do_render(self, surface: Surface):
        text_sprite = arcade.create_text_sprite(
            text=self.text.upper(),
            color=arcade.color.WHITE,
            font_name="8bitoperator JVE",
            font_size=36
        )

        arcade.draw_sprite_rect(
            sprite=text_sprite,
            rect=LBWH(
                0,
                0,
                width=text_sprite.width * 1.5,
                height=self.content_height + 8
            ),
            pixelated=True
        )


class EnemySelectMeterColumnLabels(UIBoxLayout):
    def __init__(self):
        super().__init__(
            children=[UISpace(width=860), EnemySelectMeterColumnLabel("HP"), EnemySelectMeterColumnLabel("MERCY")],
            width=1400,
            height=40,
            size_hint=None,
            vertical=False,
            align="bottom"
        )


class EnemySelectOptions(UIBoxLayout):
    def __init__(self, enemies: list[non_player_character.NonPlayerCharacter]):
        children = []

        for enemy in enemies:
            children.append(EnemySelectInstance(enemy))

        super().__init__(
            x=36,
            y=0,
            width=settings.WINDOW_WIDTH - 40,
            height=int(settings.WINDOW_HEIGHT / 4) - 80,
            vertical=True,
            children=children,
            align="center",
            size_hint=None
        )


class EnemySelect(UIBoxLayout):
    def __init__(self, enemies: list[non_player_character.NonPlayerCharacter]):
        super().__init__(
            x=36,
            y=0,
            width=settings.WINDOW_WIDTH,
            height=int(settings.WINDOW_HEIGHT / 4),
            children=[
                EnemySelectMeterColumnLabels(),
                EnemySelectOptions(enemies)
            ],
            vertical=True,
            align="left"
        )

        self.with_background(color=arcade.color.BLACK)

    """
    def do_render(self, surface):
        arcade.draw_rect_filled(
            arcade.LBWH(0, 0, self.width, self.height + 32),
            arcade.color.BLACK
        )

        super().do_render(surface)
    """

    def do_layout(self):
        self.center_x = int(settings.WINDOW_WIDTH / 2)
        self.height = int(settings.WINDOW_HEIGHT / 4)

        super().do_layout()


"""
class TPMeterGauge(UIImage):
    def __init__(self):
        super().__init__(
            width=25,
            height=196,
            texture=arcade.load_texture("assets/textures/gui_graphics/battle/tp_meter/tp_meter.png")
        )
"""

"""
class TPMeterMeter(UIWidget):
    
    #Based on the example progress bar on arcade's website.
    #Link: https://api.arcade.academy/en/stable/programming_guide/gui/own_widgets.html#example-progressbar
    

    value = Property(0.0)

    def __init__(self):
        super().__init__(
            width=50,
            height=392,
            size_hint=None
        )
        self.focus_mode = FocusMode(0)

        self.with_background(color=arcade.color.DARK_RED)

        self.tp = 40
        self.max_tp = 100

        self.value = self.tp / self.max_tp
        self.color = arcade.color.NEON_CARROT

        # trigger a render when the value changes
        bind(self, "value", self.trigger_render)

    def do_render(self, surface: arcade.gui.Surface) -> None:
        self.prepare_render(surface)

        self.with_background(color=arcade.color.DARK_RED)

        arcade.draw_lbwh_rectangle_filled(
            0,
            0,
            self.content_width,
            self.content_height * self.value,
            self.color,
        )


class TPMeterFrame(UIImage):
    def __init__(self):
        super().__init__(
            width=50,
            height=392,
            texture=arcade.load_texture("assets/textures/gui_graphics/battle/tp_meter/tp_meter_frame.png")
        )


class TPMeter(UILayout):
    def __init__(self):
        super().__init__(
            x=settings.WINDOW_HEIGHT / 2,
            y=40,
            width=50,
            height=392,
            children=[
                TPMeterMeter(),
                TPMeterFrame()
            ]
        )

    def do_layout(self):
        super().do_layout()
        for widget in self.children:
            widget.center_x = 65
            widget.center_y = settings.WINDOW_HEIGHT / 2 + 192
"""


class TPMeterImage:
    """
    Dynamically renders a TP meter texture based on a PIL image.
    """

    def __init__(self):
        self.width = 50
        self.height = 392

        self.image = Image.new(
            mode="RGBA",
            size=(self.width, self.height)
        )

        self.tp = 0
        self.max_tp = 100

        self.tp_meter_height = int(self.height * (self.tp / self.max_tp))

        tp_meter_frame = Image.open("assets/textures/gui_graphics/battle/tp_meter/tp_meter_frame.png")
        self.tp_meter_frame = tp_meter_frame.resize(
            size=(self.width, self.height),
            resample=Resampling.NEAREST
        )
        tp_meter_cutoff = Image.open("assets/textures/gui_graphics/battle/tp_meter/tp_meter_cutoff.png")
        self.tp_meter_cutoff = tp_meter_cutoff.resize(
            size=(self.width, self.height),
            resample=Resampling.NEAREST
        )
        self.tp_meter_frame.convert("L")
        self.tp_meter_color = (255, 163, 67, 255)
        self.tp_meter_background_color = (139, 0, 0, 255)

        self.tp_meter_background = Image.new(
            mode="RGBA",
            size=(self.width, self.height),
            color=self.tp_meter_background_color
        )

        self.tp_meter = Image.new(
            mode="RGBA",
            size=(self.width, self.tp_meter_height),
            color=self.tp_meter_color
        )

        self.update()

    def update(self):
        self.tp_meter_height = int(self.height * (self.tp / self.max_tp))
        self.tp_meter = Image.new(
            mode="RGBA",
            size=(self.width, self.tp_meter_height),
            color=self.tp_meter_color
        )

        self.image.paste(self.tp_meter_background)
        self.image.paste(self.tp_meter)
        self.image.paste(im=self.tp_meter_frame, mask=self.tp_meter_frame)
        self.image = ImageChops.subtract(self.image, self.tp_meter_cutoff)

    def get_image(self):
        return self.image


class TPMeterLabel(UIImage):
    def __init__(self):
        super().__init__(
            width=44,
            height=88,
            texture=arcade.load_texture("assets/textures/gui_graphics/battle/tp_meter/tp_meter_label.png"),
        )


class TPMeterNumber(UILabel):
    def __init__(self):
        super().__init__(
            width=44,
            height=40,
            font_name="8bitoperator JVE",
            font_size=48,
            text="0"
        )


class TPMeterPercentLabel(UILabel):
    def __init__(self):
        super().__init__(
            width=44,
            height=48,
            font_name="8bitoperator JVE",
            font_size=40,
            text="%"
        )


class TPMeterTextContainer(UIBoxLayout):
    def __init__(self):
        super().__init__(
            vertical=True,
            width=60,
            children=[
                TPMeterLabel(),
                TPMeterNumber(),
                TPMeterPercentLabel()
            ]
        )


class TPMeterGraphic(UIImage):
    def __init__(self):
        self.tp_meter_image = TPMeterImage()

        super().__init__(
            width=50,
            height=392,
            texture=arcade.Texture(self.tp_meter_image.get_image())
        )

        self.is_updating = False
        self.new_tp = 0.0

    def get_image_object(self):
        return self.tp_meter_image

    def update(self, tp: float = 0.0):
        self.tp_meter_image.tp = tp
        self.is_updating = True

    def on_update(self, delta_time):
        if self.is_updating:
            self.tp_meter_image.update()
            if self.tp_meter_image.tp >= self.new_tp:
                self.tp_meter_image.tp = self.new_tp
                self.is_updating = False


class TPMeter(UIBoxLayout):
    def __init__(self):
        super().__init__(
            x=40,
            y=settings.WINDOW_HEIGHT / 2,
            vertical=False,
            space_between=4,
            align="top",
            children=[
                TPMeterTextContainer(),
                TPMeterGraphic()
            ]
        )

    def update_tp_meter(self, tp: float = 0.0):
        tp_meter = self.children[1].get_image_object()
        tp_meter.update(tp)

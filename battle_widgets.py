import math

import arcade
import pyglet.clock
from PIL import Image, ImageChops
from PIL.Image import Resampling
from arcade import LBWH, Rect
from arcade.gui import UITextureButton, UIBoxLayout, UIWidget, UILabel, UIImage, bind, Property, UIGridLayout, \
    UIKeyPressEvent, UIKeyEvent, Surface, UIAnchorLayout
from arcade.gui.widgets import FocusMode, UISpace, UILayout
from arcade.shape_list import create_line
from arcade.types.color import Color

import non_player_character
import player_character
import settings
from graphics_methods import ease_out, make_texture_solid_color
from items import Item, ConsumableItem
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

        self.is_focused = False

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
        self.delta_time = min(dt, 1/60)
        if self.is_focused:
            self.trigger_render()

    def do_render(self, surface: Surface):
        self.with_background(color=arcade.color.BLACK)
        super().do_render(surface)

        arcade.draw_line(0, 0, 0, self.height,
                         [self.character_color_r, self.character_color_g, self.character_color_b, 255], 8)

        arcade.draw_line(self.width, 0, self.width, self.height,
                         [self.character_color_r, self.character_color_g, self.character_color_b, 255], 8)

        if self.is_focused:
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
        self.character = character
        super().__init__(
            width=180,
            height=21,
            text=str(self.character.hp),
            font_name="3x5 font",
            font_size=21,
            multiline=False
        )
        self.focus_mode = FocusMode(0)
        self.update_hp_on_character_card()

    def update_hp_on_character_card(self):
        self.text = str(self.character.hp)
        if 0 < self.character.hp < self.character.max_hp / 4:
            self.update_font(font_color=arcade.color.YELLOW)
        elif self.character.hp < 0:
            self.update_font(font_color=arcade.color.RED)
        else:
            self.update_font(font_color=arcade.color.WHITE)


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
        self.character = character
        super().__init__(
            width=180,
            height=21,
            text=str(self.character.max_hp),
            font_name="3x5 font",
            font_size=21,
            multiline=False
        )
        self.focus_mode = FocusMode(0)
        self.update_max_hp_on_character_card()

    def update_max_hp_on_character_card(self):
        self.text = str(self.character.max_hp)
        if 0 < self.character.hp < self.character.max_hp / 4:
            self.update_font(font_color=arcade.color.YELLOW)
        elif self.character.hp < 0:
            self.update_font(font_color=arcade.color.RED)
        else:
            self.update_font(font_color=arcade.color.WHITE)


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
        self.player_character = character

        super().__init__(
            width=140,
            height=18,
            size_hint=None
        )
        self.focus_mode = FocusMode(0)

        self.with_background(color=arcade.color.DARK_RED)

        self.hp = self.player_character.hp
        self.max_hp = self.player_character.max_hp

        self.value = self.player_character.hp / self.player_character.max_hp
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

    def update_hp(self):
        """ Updates the HP meter to accurately reflect the current HP of the player character. """
        self.value = self.player_character.hp / self.player_character.max_hp


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
        hurt_texture_path = "assets/sprites/player_characters/" + character.sprite_folder_name + "/battle_hud/hud_default_hurt_icon.png"

        image = Image.open(texture_path)
        hurt_image = Image.open(hurt_texture_path)
        self.normal_texture = arcade.Texture(arcade.load_image(texture_path).resize(image.size, Image.Resampling.NEAREST))
        self.hurt_texture = arcade.Texture(arcade.load_image(hurt_texture_path).resize(hurt_image.size, Image.Resampling.NEAREST))

        super().__init__(
            texture=self.normal_texture,
            width=64,
            height=48
        )
        self.focus_mode = FocusMode(0)

    def set_texture_to_normal(self, dt):
        """
        Sets the icon texture back to normal.
        :return:
        """
        self.texture = self.normal_texture

    def change_to_hurt_icon(self):
        """
        Temporarily changes the icon to the character's hurt icon.
        :return: None
        """
        if self.texture == self.normal_texture:
            self.texture = self.hurt_texture
            pyglet.clock.schedule_once(self.set_texture_to_normal, 1.0)


class BattleHUDCharacterName(UILabel):
    """
    Contains the name of the character in the character's battle HUD card.
    """
    def __init__(self, character: player_character.PlayerCharacter):
        super().__init__(
            width=108,
            height=48,
            text=character.name.upper(),
            font_name="""Roarin'""",
            font_size=48,
            align="left",
            size_hint=None
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
            space_between=16,
            align="left"
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
        self.character_icon_path = "assets/sprites/player_characters/" + character.sprite_folder_name + "/battle_hud/hud_default_face_icon.png"
        self._character_name = character.name
        self._hp = character.hp
        self._max_hp = character.max_hp
        self.battle_hud_character_data = BattleHUDCharacterData(character)
        self.battle_hud_button_layout = BattleHUDButtonLayout(character)

        super().__init__(
            children=[self.battle_hud_button_layout,
                      self.battle_hud_character_data],
            x=0,
            width=420,
            height=180
        )

        self.focus_mode = FocusMode(0)

        self.is_focused = is_focused

        battle_hud_button_layout = self.children[0]
        battle_hud_button_layout.is_focused = self.is_focused

        self.character_display_transition_time = 0
        self.hud_lowered_center_y = self.battle_hud_character_data.center_y
        self.distance_hud_raised = 78
        self.hud_raised_center_y = self.battle_hud_character_data.center_y + self.distance_hud_raised
        self.hud_raise_animation_time = 0.2
        self.inverse_of_hud_raise_animation_time = 1 / self.hud_raise_animation_time

        self.is_instantiated = False

        self.is_character_display_rising = False
        self.is_character_display_lowering = False
        self.trigger_render()

    def on_update(self, dt):
        if self.is_character_display_rising or self.is_character_display_lowering:
            self.trigger_render()

        if self.is_character_display_rising:
            self.move_up_character_display_slightly(dt)
        elif self.is_character_display_lowering:
            self.move_down_character_display_slightly(dt)

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

    def move_up_character_display_slightly(self, dt):
        self.character_display_transition_time += dt
        new_hud_center_y = self.hud_lowered_center_y + (-self.distance_hud_raised * (self.inverse_of_hud_raise_animation_time * self.character_display_transition_time) * ((self.inverse_of_hud_raise_animation_time * self.character_display_transition_time) - 2))
        self.battle_hud_character_data.center_y = new_hud_center_y
        if self.character_display_transition_time > self.hud_raise_animation_time:
            self.battle_hud_character_data.center_y = self.hud_raised_center_y
            self.character_display_transition_time = 0
            self.is_character_display_rising = False

    def move_up_character_data_display(self):
        self.character_display_transition_time = 0

        if self.is_focused:
            self.hud_raised_center_y = self.battle_hud_character_data.center_y
            self.hud_lowered_center_y = self.battle_hud_character_data.center_y - self.distance_hud_raised
        else:
            self.hud_lowered_center_y = self.battle_hud_character_data.center_y
            self.hud_raised_center_y = self.battle_hud_character_data.center_y + self.distance_hud_raised

        self.is_character_display_rising = True
        self.is_character_display_lowering = False

    def focus(self):
        """ Moves the character data display up so the buttons can be shown. """
        if self.is_focused:
            return
        self.move_up_character_data_display()
        self.is_focused = True
        self.battle_hud_character_data.with_border(width=3, color=self.player_character.battle_ui_color)
        battle_hud_button_layout = self.children[0]
        battle_hud_button_layout.is_focused = True

    def move_down_character_display_slightly(self, dt):
        self.character_display_transition_time += dt
        new_hud_center_y = self.hud_raised_center_y - (-self.distance_hud_raised * (self.inverse_of_hud_raise_animation_time * self.character_display_transition_time) * ((self.inverse_of_hud_raise_animation_time * self.character_display_transition_time) - 2))
        self.battle_hud_character_data.center_y = new_hud_center_y
        if self.character_display_transition_time > self.hud_raise_animation_time:
            self.battle_hud_character_data.center_y = self.hud_lowered_center_y
            self.character_display_transition_time = 0
            self.is_character_display_lowering = False

    def move_down_character_data_display(self):
        self.character_display_transition_time = 0

        if self.is_focused:
            self.hud_raised_center_y = self.battle_hud_character_data.center_y
            self.hud_lowered_center_y = self.battle_hud_character_data.center_y - self.distance_hud_raised
        else:
            self.hud_lowered_center_y = self.battle_hud_character_data.center_y
            self.hud_raised_center_y = self.battle_hud_character_data.center_y + self.distance_hud_raised

        self.is_character_display_lowering = True
        self.is_character_display_rising = False

    def unfocus(self):
        """ Moves the character data display up so the buttons can be shown. """
        if not self.is_focused:
            return
        self.move_down_character_data_display()
        self.is_focused = False
        self.battle_hud_character_data.with_border(width=0, color=self.player_character.battle_ui_color)
        battle_hud_button_layout = self.children[0]
        battle_hud_button_layout.is_focused = False

    def change_icon(self, icon_path: str = ""):
        """
        Changes the icon on the current clamshell to the one with the provided path.
        Icons located at assets/textures/gui_graphics/action_icons.
        If no path is provided, resets the icon to the character's default icon.
        :return: None
        """
        icon_color = self.player_character.battle_ui_icon_color

        if icon_path:
            icon_texture_path = icon_path
            icon_texture = make_texture_solid_color(arcade.load_texture(icon_texture_path), icon_color)
        else:
            # Since Ralsei has a multicolor icon, the default icons are loaded without making them solid color
            icon_texture_path = self.character_icon_path
            icon_texture = arcade.load_texture(icon_texture_path)

        self.children[1].children[0].children[0].texture = icon_texture


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


    def do_layout(self):
        self.center_x = int(settings.WINDOW_WIDTH / 2)
        self.height = int(settings.WINDOW_HEIGHT / 4)

        super().do_layout()


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

        # Used for animating the bar.
        self.visual_tp = 0

        self.tp_meter_height = int(self.height * (self.tp / self.max_tp))

        self.tp_meter_spritesheet = arcade.load_spritesheet("assets/textures/gui_graphics/battle/tp_meter/tp_meter_spritesheet.png")

        self.tp_meter_background = self.tp_meter_spritesheet.get_image(arcade.LRBT(left=0, right=48, bottom=0, top=392), y_up=True)
        self.tp_meter = None

        self.render()

    def render(self):
        self.tp_meter_height = int(self.height * (self.visual_tp / self.max_tp))
        self.tp_meter = self.tp_meter_spritesheet.get_image(arcade.LRBT(left=100, right=147, bottom=0, top=self.tp_meter_height), y_up=True)

        self.image.paste(self.tp_meter_background)
        self.image.paste(self.tp_meter, (0, self.height - self.tp_meter_height), self.tp_meter)

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

        arcade.enable_timings()

    def do_render(self, surface: Surface):
        super().do_render(surface)
        self.text = str(int(arcade.get_fps()))


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

        self.elapsed_time = 0.0
        self.starting_tp = 0.0
        self.ending_tp = 0.0
        self.animation_duration = 0.5

    def get_image_object(self):
        return self.tp_meter_image

    def update(self, tp: float = 0.0):
        self.elapsed_time = 0.0
        if tp > 1.0 or tp < -1.0:
            self.tp_meter_image.visual_tp = self.tp_meter_image.tp
            self.tp_meter_image.tp = min(self.tp_meter_image.tp + tp, 100.0)
            self.starting_tp = self.tp_meter_image.visual_tp
            self.ending_tp = self.tp_meter_image.tp
            self.is_updating = True
        else:
            self.tp_meter_image.tp = min(self.tp_meter_image.tp + tp, 100.0)
            self.tp_meter_image.visual_tp = self.tp_meter_image.tp
            self.tp_meter_image.render()

    def on_update(self, delta_time):
        if self.is_updating:
            self.elapsed_time += delta_time
            normalized_time = min(self.elapsed_time / self.animation_duration, 1.0)
            eased_time = ease_out(normalized_time)
            self.tp_meter_image.visual_tp = self.starting_tp + ((self.ending_tp - self.starting_tp) * eased_time)
            self.tp_meter_image.render()
            self.texture = arcade.Texture(self.tp_meter_image.get_image())
            if self.elapsed_time >= self.animation_duration:
                self.tp_meter_image.visual_tp = self.tp_meter_image.tp
                self.is_updating = False
                self.elapsed_time = 0


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
        tp_meter = self.children[1]
        tp_meter.update(tp)


class ItemOption(UILabel):
    def __init__(self, item: ConsumableItem, index: int):
        super().__init__(
            text="     " + item.name,
            width=400,
            height=64,
            font_name="8bitoperator JVE",
            font_size=48,
            text_color=arcade.color.WHITE,
            size_hint=None
        )

        self.item = item
        self.index = index

        self.focus_mode = FocusMode(2)
        self.soul_sprite = arcade.Sprite(path_or_texture="assets/sprites/soul/soul.png", scale=1.0)

    def do_render_focus(self, surface: arcade.gui.Surface):
        arcade.draw_sprite_rect(
            self.soul_sprite,
            arcade.XYWH(
                32,
                32,
                32,
                32
            ),
            pixelated=True
        )

        if self.index > 5:
            self.parent.make_six_items_invisible(True)
        else:
            self.parent.make_six_items_invisible(False)


class ItemDescriptionLabel(UILabel):
    def __init__(self, item_description: str = ""):
        super().__init__(
            size_hint=(None, None),
            width=400,
            height=settings.WINDOW_HEIGHT / 4.4,
            font_name="8bitoperator JVE",
            font_size=48,
            text_color=arcade.color.GRAY,
            text=item_description,
            multiline=True
        )

    def update_item_data(self, item: ConsumableItem = None):
        """ Updates the spell data shown in the layout. """
        self.text = "" if not item or not item.battle_description else item.battle_description


class ItemOptionsList(UIGridLayout):
    """
    Contains, at max, 6 item options in a 2x3 grid.
    """
    def __init__(self, items: list[ConsumableItem]):
        row_count = (len(items) // 2) + 1
        column_count = 2 if len(items) > 1 else 1

        super().__init__(
            x=36,
            y=0,
            width=(2 * settings.WINDOW_WIDTH) / 3,
            height=196, # int(settings.WINDOW_HEIGHT / 4) - 30,
            row_count=row_count,
            column_count=column_count,
            align_horizontal="left",
            alight_vertical="center",
            horizontal_spacing=100,
            size_hint=None
        )

        current_item_index = 0

        for item in items:
            item_option = ItemOption(item, current_item_index)
            if current_item_index > 5:
                item_option.height = 1
            self.add(
                item_option,
                column=current_item_index % 2,
                row=current_item_index // 2
            )
            current_item_index += 1

    def make_six_items_invisible(self, make_first_six_items_invisible: bool = True):
        """
        Makes 6 of the items invisible to create the illusion that the user is scrolling down the item list.
        :param make_first_six_items_invisible: whether or not to make the first six items invisible.
        :return:
        """
        current_item_index = 0
        if make_first_six_items_invisible:
            for child in self.children:
                if current_item_index <= 5:
                    child.height = 0.01
                else:
                    child.height = 64
                current_item_index += 1
        else:
            for child in self.children:
                if current_item_index <= 5:
                    child.height = 64
                else:
                    child.height = 0.01
                current_item_index += 1
        self.parent.make_arrow_invisible(make_first_six_items_invisible)


class ItemArrow(UIImage):
    """
    The up and down arrows shown by the ITEM inventory.
    """
    def __init__(self, is_up: bool = True):
        texture = arcade.load_texture("assets/textures/gui_graphics/battle/item_menu_down_arrow.png")
        if is_up:
            texture = texture.flip_vertically()

        super().__init__(
            texture=texture,
            height=32,
            width=26
        )


class ItemArrowContainer(UIBoxLayout):
    """
    The containers that the up and down arrows for the items menu are in.
    """
    def __init__(self):
        super().__init__(
            height=settings.WINDOW_HEIGHT / 5,
            vertical=True,
            children=[
                ItemArrow(True),
                ItemArrow(False)
            ],
            space_between=settings.WINDOW_HEIGHT / 8.0,
            size_hint=None
        )

        self.time = 0
        self.flag1 = True  # arrows are close
        self.flag2 = True  # arrows are drifting apart
        self.flag3 = True  # arrows are far apart
        self.flag4 = True  # arrows are drifting closer


    def on_update(self, dt):
        self.time += dt

        if self.time < 0.2 and self.flag1:
            self._space_between += 6
            self.height += 6
            self.flag1 = False
            self.do_layout()
        elif 0.2 <= self.time < 1 and self.flag2:
            self._space_between += 6
            self.height += 6
            self.flag2 = False
            self.do_layout()
        elif 1 <= self.time < 1.2 and self.flag3:
            self._space_between -= 6
            self.height -= 6
            self.flag3 = False
            self.do_layout()
        elif 1.2 <= self.time < 2 and self.flag4:
            self._space_between -= 6
            self.height -= 6
            self.flag4 = False
            self.do_layout()
        elif self.time >= 2:
            self.time -= 2
            self.flag1 = True
            self.flag2 = True
            self.flag3 = True
            self.flag4 = True


class ItemSelect(UIBoxLayout):
    """
    The item select container allowing the user to select an item in battle.
    """
    def __init__(self, items: list[ConsumableItem]):
        item_options_list = ItemOptionsList(items)
        item_arrow_container = ItemArrowContainer()
        item_description_label = ItemDescriptionLabel()

        self.space_between = settings.WINDOW_WIDTH - (item_options_list.width + item_description_label.width)

        super().__init__(
            x=0,
            y=0,
            width=settings.WINDOW_WIDTH,
            height=settings.WINDOW_HEIGHT / 4,
            vertical=False,
            children=[item_options_list, item_arrow_container, item_description_label],
            align="center",
            space_between=(self.space_between / 2) - item_arrow_container.width
        )

    def make_arrow_invisible(self, make_down_arrow_invisible: bool):
        """ Make one of the arrows invisible depending on the focused item. """
        if make_down_arrow_invisible:
            self.children[1].children[0].visible = True
            self.children[1].children[1].visible = False
        else:
            self.children[1].children[0].visible = False
            self.children[1].children[1].visible = True


    def update_item_data(self, item: ConsumableItem = None):
        """ Updates the spell data shown in the layout. """
        self.children[2].update_item_data(item)


class PlayerSelectInstanceNameLabel(UILabel):
    """
    Contains the name of the player to be selected in the player select menu.
    """
    def __init__(self, player_name: str):
        super().__init__(
            text="    " + player_name,
            width=400,
            height=64,
            font_name="8bitoperator JVE",
            font_size=48,
            text_color=arcade.color.WHITE,
            size_hint=None
        )


class PlayerSelectInstanceHPMeter(UIWidget):
    value = Property(0.0)

    def __init__(self, hp: int, max_hp: int):
        super().__init__(
            width=220,
            height=36,
            size_hint=None
        )
        self.focus_mode = FocusMode(0)

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

        super().do_render(surface)


class PlayerSelectInstance(UIBoxLayout):
    def __init__(self, player: player_character.PlayerCharacter):
        self.player = player


        player_label = PlayerSelectInstanceNameLabel(self.player.name)
        player_hp_meter = PlayerSelectInstanceHPMeter(self.player.hp, self.player.max_hp)

        self.space_between = settings.WINDOW_WIDTH - (player_label.width + player_hp_meter.width) - 400
        super().__init__(
            width=int(settings.WINDOW_WIDTH - 40),
            height=40,
            vertical=False,
            children=[
                player_label,
                player_hp_meter
            ],
            space_between=self.space_between
        )

        self.focus_mode = FocusMode(2)
        self.soul_sprite = arcade.Sprite(path_or_texture="assets/sprites/soul/soul.png", scale=1.0)

    def do_render_focus(self, surface: arcade.gui.Surface):
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


class PlayerSelect(UIBoxLayout):
    def __init__(self, players: list[player_character.PlayerCharacter]):

        super().__init__(
            x=0,
            y=0,
            width=settings.WINDOW_WIDTH,
            height=settings.WINDOW_HEIGHT / 4.2,
            vertical=True,
            align="center",
            size_hint=None
        )

        for player in players:
            self.add(PlayerSelectInstance(player))

        self.with_background(color=arcade.color.BLACK)

    def do_layout(self):
        self.center_x = int(settings.WINDOW_WIDTH / 2)
        self.height = int(settings.WINDOW_HEIGHT / 4.2)

        super().do_layout()

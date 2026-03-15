import math

import arcade
import pyglet.clock
from PIL import Image
from arcade import LBWH
from arcade.gui import UITextureButton, UIBoxLayout, UIWidget, UILabel, UIImage, bind, Property, UIGridLayout, \
    UIKeyPressEvent, UIKeyEvent, Surface
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

        self.with_background(color=Color(0, 0, 0, 255))
        self.with_border(width=3, color=character.battle_ui_color)
        self.with_padding(top=8, left=12, bottom=8, right=12)


class BattleHUDCharacterClamshell(UILayout):
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
        self.battle_hud_character_data = BattleHUDCharacterData(character)
        self.battle_hud_button_layout = BattleHUDButtonLayout(character)

        super().__init__(
            children=[],
            width=420,
            height=160,
            space_between=2,
            vertical=True
        )

        self.add(self.battle_hud_button_layout)
        self.add(self.battle_hud_character_data)

        self.focus_mode = FocusMode(0)

        self.with_background(color=Color(0, 0, 0, 255))
        #self.with_border(width=3, color=character.battle_ui_color)
        #self.with_padding(top=2, right=8, bottom=0, left=8)

        self.character_display_transition_time = 0
        self.hud_lowered_center_y = self.battle_hud_character_data.center_y
        self.distance_hud_raised = 40
        self.hud_raised_center_y = self.battle_hud_character_data.center_y + self.distance_hud_raised
        self.hud_raise_animation_time = 0.5

    def do_layout(self):
        super().do_layout()

        rect = self.rect

        self.battle_hud_character_data.center_x = rect.center_x
        self.battle_hud_character_data.center_y = rect.center_y

        self.battle_hud_button_layout.center_x = rect.center_x
        self.battle_hud_button_layout.center_y = rect.center_y

    """
    def do_render_focus(self, surface: Surface):
        self.children[0].visible = False
    """

    def move_up_character_display_slightly(self, dt):
        self.character_display_transition_time += dt
        new_hud_center_y = self.hud_lowered_center_y + (self.distance_hud_raised * math.cos((1 / self.hud_raise_animation_time) * self.character_display_transition_time * (math.pi / 2)))
        self.battle_hud_character_data.center_y = new_hud_center_y
        if self.character_display_transition_time > self.hud_raise_animation_time:
            pyglet.clock.unschedule(self.move_up_character_display_slightly)

    def move_up_character_data_display(self):
        pyglet.clock.schedule_interval(self.move_up_character_display_slightly, 0.05)

    def show_buttons(self):
        """ Moves the character data display up so the buttons can be shown. """
        pass


class BattleHUDCharacterClamshellDisplay(UIBoxLayout):
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
            y=int(settings.WINDOW_HEIGHT / 4.5) + 12,
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

        for character in player_characters:
            clamshell = BattleHUDCharacterClamshell(character)
            self.add(clamshell)

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

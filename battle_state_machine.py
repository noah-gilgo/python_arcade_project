from enum import Enum, auto
import command

import arcade.key
import pyglet
from arcade import SpriteList
from arcade.gui import UILayout, UIWidget, UIManager

import battle_widgets
import character
import non_player_character
import player_character
from actions import SpellAction
from battle_widgets import SpellList, SpellSelect, EnemySelectOptions, EnemySelect
from focus_stack import FocusStackMember, FocusStack
from graphics_objects import MultiSpriteAnimation
from player_character import PlayerCharacter

"""
This architecture is my attempt at replicating the state architecture recommended by Robert Nystrom in his book
Game Programming Patterns. The guide I followed can be found here:
https://gameprogrammingpatterns.com/state.html
"""


class BattleState(Enum):
    PLAYER_COMMAND = auto()
    PLAYER_ATTACK_SELECT = auto()
    PLAYER_ACT_ENEMY_SELECT = auto()
    PLAYER_MAGIC_ENEMY_SELECT = auto()
    PLAYER_ACT_SELECT = auto()
    PLAYER_ITEM_SELECT = auto()
    PLAYER_MAGIC_SELECT = auto()
    PLAYER_SPARE_SELECT = auto()
    PLAYER_TARGET = auto()
    EXECUTE_QUEUED_PLAYER_COMMANDS = auto()
    DIALOGUE = auto()
    ENEMY_ATTACK = auto()
    VICTORY = auto()
    DEFEAT = auto()


"""
class CommandInput:
    def __init__(self, battle):
        self.battle = battle

        self.command_menu = battle.battle_player_character_cards

        # Track the current state of what key is pressed
        self.left_pressed = False
        self.right_pressed = False
        self.up_pressed = False
        self.down_pressed = False


    def update_player_speed(self, soul):
        # Calculate speed based on the keys pressed
        self.soul.change_x = 0
        self.soul.change_y = 0

        if self.up_pressed and not self.down_pressed:
            self.soul.change_y = character.MOVEMENT_SPEED
        elif self.down_pressed and not self.up_pressed:
            self.soul.change_y = -character.MOVEMENT_SPEED
        if self.left_pressed and not self.right_pressed:
            self.soul.change_x = -character.MOVEMENT_SPEED
        elif self.right_pressed and not self.left_pressed:
            self.soul.change_x = character.MOVEMENT_SPEED


    def handle_key(self, key):
        # Handles user inputs made during the battle.
        match key:
            case arcade.key.Z:
                self.battle.confirm_command()
            case arcade.key.RIGHT:
                print("right key pressed")
                self.battle.right_command()
            case arcade.key.LEFT:
                self.battle.left_command()

        # Selecting one of the fight action buttons (FIGHT, ACT, MAGIC, SPARE, etc.)
        if self.battle.state == BattleState.PLAYER_COMMAND:
            if key == arcade.key.LEFT:
                self.battle.ui.command_menu.move(-1)
            elif key == arcade.key.RIGHT:
                self.battle.ui.command_menu.move(1)
            elif key == arcade.key.C:
                self.battle.confirm_command()

        # Selecting one of the acts after selecting the ACT button.
        elif self.battle.state == BattleState.PLAYER_ACT_SELECT:
            if key == arcade.key.LEFT:
                self.battle.ui.command_menu.move(-1, 0)
            elif key == arcade.key.RIGHT:
                self.battle.ui.command_menu.move(1, 0)
            elif key == arcade.key.UP:
                self.battle.ui.command_menu.move(0, -1)
            elif key == arcade.key.DOWN:
                self.battle.ui.command_menu.move(0, 1)
            elif key == arcade.key.C:
                self.battle.confirm_command()

        # Selecting one of the spells after selecting the MAGIC button.
        elif self.battle.state == BattleState.PLAYER_MAGIC_SELECT:
            if key == arcade.key.LEFT:
                self.battle.ui.command_menu.move(-1, 0)
            elif key == arcade.key.RIGHT:
                self.battle.ui.command_menu.move(1, 0)
            elif key == arcade.key.UP:
                self.battle.ui.command_menu.move(0, -1)
            elif key == arcade.key.DOWN:
                self.battle.ui.command_menu.move(0, 1)
            elif key == arcade.key.C:
                self.battle.confirm_command()

        # Selecting one of the items after selecting the ITEM button.
        elif self.battle.state == BattleState.PLAYER_ITEM_SELECT:
            if key == arcade.key.LEFT:
                self.battle.ui.command_menu.move(-1, 0)
            elif key == arcade.key.RIGHT:
                self.battle.ui.command_menu.move(1, 0)
            elif key == arcade.key.UP:
                self.battle.ui.command_menu.move(0, -1)
            elif key == arcade.key.DOWN:
                self.battle.ui.command_menu.move(0, 1)
            elif key == arcade.key.C:
                self.battle.confirm_command()

        elif self.battle.state == BattleState.PLAYER_TARGET:
            if key == arcade.key.UP:
                self.battle.ui.command_menu.move(-1)
            elif key == arcade.key.DOWN:
                self.battle.ui.command_menu.move(1)

        elif self.battle.state == BattleState.DIALOGUE:
            if key == arcade.key.C:
                self.battle.confirm_command()

        
        elif self.battle.state == BattleState.ENEMY_ATTACK:
            if key == arcade.key.UP:
                self.up_pressed = True
                self.soul.update_player_speed()
            elif key == arcade.key.DOWN:
                self.down_pressed = True
                self.soul.update_player_speed()
            elif key == arcade.key.LEFT:
                self.left_pressed = True
                self.soul.update_player_speed()
            elif key == arcade.key.RIGHT:
                self.right_pressed = True
                self.soul.update_player_speed()
        
"""


class BattleController:
    def __init__(self, ui_manager: UIManager, battle_textbox: UIWidget,
                 player_characters: list[player_character.PlayerCharacter],
                 enemies: list[non_player_character.NonPlayerCharacter],
                 spell_animations_sprite_list: SpriteList,
                 spell_animations: list[MultiSpriteAnimation]):
        self.battle_textbox = battle_textbox
        self.ui_manager = ui_manager
        self.player_characters = player_characters
        self.enemies = enemies

        self.state = BattleState.PLAYER_COMMAND
        self.turn = 0
        self.selected_command = None
        self.selected_target = None

        # References to all of the battle buttons and their indexes
        self.battle_player_character_cards = battle_widgets.BattleHUDCharacterClamshellDisplay(self.player_characters)

        # The focus stack for the battle GUI.
        self.focus_stack = FocusStack(self.ui_manager)

        self.focus_stack.push(
            self.battle_player_character_cards,
            self.battle_player_character_cards.children[0].children[1],
            self.state
        )

        # Loads menu sounds
        self.menu_move_sound = arcade.load_sound("assets/audio/gui/snd_menumove.wav", False)
        self.menu_select_sound = arcade.load_sound("assets/audio/gui/snd_select.wav", False)

        # The queue of actions selected by the player for each character.
        self.actions_queue = []

        # Sprite lists that need to be accessed for animations.
        self.spell_animations_sprite_list = spell_animations_sprite_list
        self.spell_animations = spell_animations

    def execute_actions_queue(self):
        for action in self.actions_queue:
            action.execute()

    def confirm_command(self):
        SelectCommand(self).execute()

    def cancel_command(self):
        CancelCommand(self).execute()

    def right_command(self):
        RightCommand(self).execute()

    def left_command(self):
        LeftCommand(self).execute()

    def up_command(self):
        UpCommand(self).execute()

    def down_command(self):
        DownCommand(self).execute()

    def handle_key(self, key):
        """ Handles user inputs made during the battle. """

        match key:
            case arcade.key.Z:
                self.confirm_command()
            case arcade.key.X:
                self.cancel_command()
            case arcade.key.RIGHT:
                self.right_command()
            case arcade.key.LEFT:
                self.left_command()
            case arcade.key.UP:
                self.up_command()
            case arcade.key.DOWN:
                self.down_command()


class Command:
    """ The default command object. Represents the Command design pattern. """

    def __init__(self, controller):
        self.controller = controller

    def execute(self):
        pass


class SelectCommand(Command):
    """ A command object representing the user selecting (usually pressing Z in the original game.) """

    def execute(self):
        match self.controller.state:
            case BattleState.PLAYER_COMMAND:
                # TODO: add functions to open UIs, set character animations
                self.controller.menu_select_sound.play()
                match self.controller.focus_stack.get_highest_member().focused_widget_index:
                    case 0:  # user selects ATTACK button
                        self.controller.state = BattleState.PLAYER_ATTACK_SELECT
                        # TODO: include code to open an enemy select UI
                        return
                    case 1:  # user selects ACT/MAGIC button
                        if self.controller.focus_stack.get_highest_member().get_focused_widget().name == "ACT":  # ACT button
                            self.controller.state = BattleState.PLAYER_ACT_ENEMY_SELECT
                            # TODO: include code to open an enemy select UI
                            return
                        else:  # MAGIC button
                            self.controller.state = BattleState.PLAYER_MAGIC_SELECT
                            spell_list_full_layout = SpellSelect(self.controller.focus_stack.get_highest_member().get_interactive_ui_layout().player_character)
                            spell_list_interactive_layout = spell_list_full_layout.children[0]
                            self.controller.focus_stack.push(spell_list_full_layout, spell_list_interactive_layout, self.controller.state, 2)
                            return
                    case 2:  # user selects the ITEM button
                        self.controller.state = BattleState.PLAYER_ITEM_SELECT
                        # TODO: include code to open the ITEM menu
                        return
                    case 3:  # user selects the SPARE button
                        self.controller.state = BattleState.PLAYER_SPARE_SELECT
                        # TODO: include code to open the SPARE menu
                        return
                    case 4:  # user selects the DEFEND button
                        # TODO: include functions to give the current character TP and set their animation to defend
                        self.controller.move_to_next_player_card()
                        return

            case BattleState.PLAYER_ATTACK_SELECT:
                # TODO: Make the current player character enter the attack state, queue the attack
                self.controller.move_to_next_player_card()
                return

            case BattleState.PLAYER_ACT_ENEMY_SELECT:
                # TODO: select the focused enemy, open the ACT menu for the selected enemy
                return

            case BattleState.PLAYER_ACT_SELECT:
                # TODO: select the focused act, animate the player character, queue the act
                self.controller.move_to_next_player_card()
                return

            case BattleState.PLAYER_MAGIC_SELECT:
                # TODO: animate the player character, queue the act
                self.controller.state = BattleState.PLAYER_MAGIC_ENEMY_SELECT
                enemy_list_full_layout = EnemySelect(self.controller.enemies)
                enemy_list_interactive_layout = enemy_list_full_layout.children[1]
                self.controller.focus_stack.push(enemy_list_full_layout, enemy_list_interactive_layout,
                                                 self.controller.state, 1)
                self.controller.menu_select_sound.play()
                return

            case BattleState.PLAYER_MAGIC_ENEMY_SELECT:
                selected_target_enemy = self.controller.focus_stack.get_highest_member().get_focused_widget().enemy
                self.controller.focus_stack.pop()
                selected_spell = self.controller.focus_stack.get_highest_member().get_focused_widget().spell
                self.controller.focus_stack.pop()
                current_player_character = self.controller.focus_stack.get_highest_member().get_interactive_ui_layout().player_character

                self.controller.actions_queue.append(
                    SpellAction(
                        actor=current_player_character,
                        targets=[selected_target_enemy],
                        spell=selected_spell,
                        controller=self.controller
                    )
                )

                self.controller.state = BattleState.PLAYER_COMMAND

                if self.controller.focus_stack.get_highest_member().get_focused_widget_index() + 1 < self.controller.focus_stack.get_highest_member().get_full_layout_length():
                    self.controller.state = BattleState.PLAYER_COMMAND
                else:
                    self.controller.state = BattleState.EXECUTE_QUEUED_PLAYER_COMMANDS
                    self.controller.execute_actions_queue()
                return

            case BattleState.PLAYER_ITEM_SELECT:
                # TODO: select the focused item, animate the player character, queue the act
                return

            case BattleState.PLAYER_SPARE_SELECT:
                # TODO: select the focused enemy, animate the player character, queue the act
                return


class CancelCommand(Command):
    """ A command object representing the user canceling (usually pressing X in the original game.) """

    def execute(self):
        focus_stack_member = self.controller.focus_stack.pop()
        if focus_stack_member:
            self.controller.state = self.controller.focus_stack.get_highest_member().state
            self.controller.menu_move_sound.play()


class RightCommand(Command):
    """ A command object representing the user pressing right (usually pressing -> in the original game.) """

    def execute(self):
        if self.controller.focus_stack.get_highest_member().move_right():
            self.controller.menu_move_sound.play()
            if self.controller.state == BattleState.PLAYER_MAGIC_SELECT:
                self.controller.focus_stack.get_highest_member().full_ui_layout.update_spell_data(
                    self.controller.focus_stack.get_highest_member().get_focused_widget().spell
                )


class LeftCommand(Command):
    """ A command object representing the user pressing left (usually pressing <- in the original game.) """

    def execute(self):
        if self.controller.focus_stack.get_highest_member().move_left():
            self.controller.menu_move_sound.play()
            if self.controller.state == BattleState.PLAYER_MAGIC_SELECT:
                self.controller.focus_stack.get_highest_member().full_ui_layout.update_spell_data(
                    self.controller.focus_stack.get_highest_member().get_focused_widget().spell
                )


class UpCommand(Command):
    """ A command object representing the user pressing up (usually pressing the up arrow key in the original game.) """

    def execute(self):
        if self.controller.focus_stack.get_highest_member().move_up():
            self.controller.menu_move_sound.play()
            if self.controller.state == BattleState.PLAYER_MAGIC_SELECT:
                self.controller.focus_stack.get_highest_member().full_ui_layout.update_spell_data(
                    self.controller.focus_stack.get_highest_member().get_focused_widget().spell
                )


class DownCommand(Command):
    """
    A command object representing the user pressing down (usually pressing the down arrow key in the original game.)
    """

    def execute(self):
        if self.controller.focus_stack.get_highest_member().move_down():
            self.controller.menu_move_sound.play()
            if self.controller.state == BattleState.PLAYER_MAGIC_SELECT:
                self.controller.focus_stack.get_highest_member().full_ui_layout.update_spell_data(
                    self.controller.focus_stack.get_highest_member().get_focused_widget().spell
                )

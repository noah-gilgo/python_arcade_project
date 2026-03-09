from enum import Enum, auto
import command

import arcade.key
from arcade.gui import UILayout, UIWidget, UIManager

import character
from battle_widgets import SpellListLayout
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
    PLAYER_ACT_SELECT = auto()
    PLAYER_ITEM_SELECT = auto()
    PLAYER_MAGIC_SELECT = auto()
    PLAYER_SPARE_SELECT = auto()
    PLAYER_TARGET = auto()
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


def move(array, current_member, index, dx):
    """
    Abstract function for moving between different members of a one-dimensional array.
    Returns the new focused member of the array as well as it's associated index.
    """
    index = (index + dx) % len(array)
    current_member = array[index]
    return current_member, index


class BattleController:
    def __init__(self, ui_manager: UIManager, battle_textbox: UIWidget, battle_player_character_cards: UILayout):
        self.battle_textbox = battle_textbox
        self.ui_manager = ui_manager

        # References to all of the battle buttons and their indexes
        self.battle_player_character_cards = battle_player_character_cards.children
        self.current_player_character_card = self.battle_player_character_cards[0]
        self.current_player_character_card_index = 0
        self.current_player_button_layout = self.current_player_character_card.children[1].children
        self.current_player_character_card_focused_button = self.current_player_button_layout[0]
        self.current_player_character_card_focused_button.focus()
        self.current_player_character_card_focused_button_index = 0
        self.open_menus = []

        self.state = BattleState.PLAYER_COMMAND
        self.turn = 0
        self.selected_command = None
        self.selected_target = None

        # Loads menu sounds
        self.menu_move_sound = arcade.load_sound("assets/audio/gui/battle/snd_menumove.wav", False)

    def move_to_next_player_card(self):
        """ Moves self.current_player_character_card to the next card. """
        if self.current_player_character_card_index < len(self.battle_player_character_cards) - 1:
            self.current_player_character_card_index += 1
        else:  # if the player is already on the last player card
            self.current_player_character_card_index = 0
            # TODO: add code to execute player character actions in lieu of enemy attack
        self.current_player_character_card = self.battle_player_character_cards[
            self.current_player_character_card_index]

    def move_between_player_action_buttons(self, dx):
        self.current_player_character_card_focused_button.unfocus()
        self.current_player_character_card_focused_button, self.current_player_character_card_focused_button_index = \
            move(self.current_player_button_layout,
                 self.current_player_character_card_focused_button,
                 self.current_player_character_card_focused_button_index,
                 dx)
        self.menu_move_sound.play()
        self.current_player_character_card_focused_button.focus()

    def confirm_command(self):
        SelectCommand(self).execute()

    def cancel_command(self):
        SelectCommand(self).execute()

    def right_command(self):
        RightCommand(self).execute()

    def left_command(self):
        LeftCommand(self).execute()

    def handle_key(self, key):
        """ Handles user inputs made during the battle. """

        match key:
            case arcade.key.Z:
                self.confirm_command()
            case arcade.key.RIGHT:
                self.right_command()
            case arcade.key.LEFT:
                self.left_command()


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
                match self.controller.current_player_character_card_focused_button_index:
                    case 0:  # user selects ATTACK button
                        self.controller.state = BattleState.PLAYER_ATTACK_SELECT
                        # TODO: include code to open an enemy select UI
                        return
                    case 1:  # user selects ACT/MAGIC button
                        if self.controller.current_player_character_card_focused_button.name == "ACT":  # ACT button
                            self.controller.state = BattleState.PLAYER_ACT_ENEMY_SELECT
                            # TODO: include code to open an enemy select UI
                            return
                        else:  # MAGIC button
                            self.controller.state = BattleState.PLAYER_MAGIC_SELECT
                            self.controller.ui_manager.add(SpellListLayout(self.controller.current_player_character_card.player_character))
                            print("spell list layout added")
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
                # TODO: select the focused spell, animate the player character, queue the act
                return

            case BattleState.PLAYER_ITEM_SELECT:
                # TODO: select the focused item, animate the player character, queue the act
                return

            case BattleState.PLAYER_SPARE_SELECT:
                # TODO: select the focused enemy, animate the player character, queue the act
                return


class RightCommand(Command):
    """ A command object representing the user selecting (usually pressing Z in the original game.) """

    def execute(self):
        match self.controller.state:
            case BattleState.PLAYER_COMMAND:
                self.controller.move_between_player_action_buttons(1)


class LeftCommand(Command):
    """ A command object representing the user selecting (usually pressing Z in the original game.) """

    def execute(self):
        match self.controller.state:
            case BattleState.PLAYER_COMMAND:
                self.controller.move_between_player_action_buttons(-1)

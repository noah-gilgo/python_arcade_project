from enum import Enum, auto
import command

import arcade.key
import pyglet
from arcade import SpriteList
from arcade.gui import UILayout, UIWidget, UIManager
from arcade.types import Color

import battle_widgets
import character
import items
import non_player_character
import player_character
from actions import SpellAction, SpareAction, ActionsQueue, Action, DefendAction, ItemAction
from animations.battle_animations import NumberBounceAnimation, HealAnimation
from animations.common_animations import FadeInFadeOutColorAnimation, ShakeAnimation, SparkleAnimation
from battle_widgets import SpellList, SpellSelect, EnemySelectOptions, EnemySelect
from dialogue_box import TextBoxDialog
from focus_stack import FocusStackMember, FocusStack
from graphics_objects import MultiSpriteAnimation
from items import Item, ConsumableItem
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
    PLAYER_ITEM_PLAYER_SELECT = auto()
    PLAYER_MAGIC_SELECT = auto()
    PLAYER_SPARE_SELECT = auto()
    PLAYER_TARGET = auto()
    EXECUTING_QUEUED_PLAYER_COMMANDS = auto()
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
    def __init__(self, ui_manager: UIManager,
                 battle_player_character_cards: UILayout,
                 battle_textbox: UIWidget,
                 player_characters: list[player_character.PlayerCharacter],
                 enemies: list[non_player_character.NonPlayerCharacter],
                 effects_sprite_list: SpriteList,
                 effects_list: list,
                 tp_meter: battle_widgets.TPMeter):
        self.battle_player_character_cards = battle_player_character_cards
        self.battle_textbox = battle_textbox
        self.ui_manager = ui_manager
        self.tp_meter = tp_meter
        self.player_characters = player_characters
        self.enemies = enemies

        self.current_player_index = 0

        self.state = BattleState.PLAYER_COMMAND
        self.turn = 0
        self.selected_command = None
        self.selected_target = None

        # References to all of the battle buttons and their indexes
        # self.battle_player_character_cards = battle_widgets.BattleHUDCharacterClamshellDisplay(self.player_characters)
        # self.ui_manager.add(self.battle_player_character_cards)

        self.ui_manager.execute_layout()

        # The focus stack for the battle GUI.
        self.focus_stack = FocusStack(self.ui_manager)

        self.focus_stack.push(
            self.battle_player_character_cards,
            self.battle_player_character_cards.children[self.current_player_index].children[0],
            self.state,
            5
        )

        # Loads menu sounds
        self.menu_move_sound = arcade.load_sound("assets/audio/gui/snd_menumove.wav", False)
        self.menu_select_sound = arcade.load_sound("assets/audio/gui/snd_select.wav", False)
        self.hurt_sound = arcade.load_sound("assets/audio/battle/player_character/common/snd_hurt1.wav", False)
        self.heal_sound = arcade.load_sound("assets/audio/battle/player_character/common/snd_power.wav", False)
        self.mercy_add_sound = arcade.load_sound("assets/audio/battle/player_character/common/snd_mercyadd.wav", False)
        self.spare_sound = arcade.load_sound("assets/audio/battle/player_character/common/snd_spare.wav")
        self.tp_add_sound = arcade.load_sound("assets/audio/battle/player_character/common/snd_cardrive.wav")

        # The queue of actions selected by the player for each character.
        self.actions_queue = ActionsQueue()
        self.sorted_actions_queue = {}

        # Sprite lists that need to be accessed for animations.
        self.effects_sprite_list = effects_sprite_list
        self.effects_list = effects_list

        self.items = items.initialize_default_items()

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

    def add_tp_to_meter(self, amount: float = 0.0):
        """
        Adds TP to the TP meter. Negative values should also work.
        :param amount: The amount of TP to add to the meter.
        :return: None
        """
        self.tp_meter.update_tp_meter(amount)

    def move_to_next_player_card(self, action: Action):
        """
        Moves to the next player card in the HUD.
        :return:
        """
        self.actions_queue.push(action)
        if self.current_player_index + 1 < self.focus_stack.get_highest_member().get_full_layout_length():
            self.state = BattleState.PLAYER_COMMAND
            self.focus_stack.pop()
            self.battle_player_character_cards.children[self.current_player_index].unfocus()
            self.current_player_index += 1
            self.battle_player_character_cards.children[self.current_player_index].focus()
            self.focus_stack.push(
                self.battle_player_character_cards,
                self.battle_player_character_cards.children[self.current_player_index].children[0],
                self.state,
                5
            )
            self.menu_select_sound.play()
        else:
            self.battle_player_character_cards.children[self.current_player_index].unfocus()
            self.focus_stack.pop()
            self.state = BattleState.EXECUTING_QUEUED_PLAYER_COMMANDS
            self.initialize_sorted_action_queue()
            self.execute_queued_player_action()

    def move_to_previous_player_card(self):
        """
        Move to the previous player card.
        :return: None
        """
        if self.current_player_index > 0:
            self.battle_player_character_cards.children[self.current_player_index].unfocus()
            self.current_player_index -= 1
            self.battle_player_character_cards.children[
                self.current_player_index].focus()
            self.focus_stack.push(
                self.battle_player_character_cards,
                self.battle_player_character_cards.children[
                    self.current_player_index].children[0],
                self.state,
                5
            )
            if len(self.actions_queue) > 0:
                self.actions_queue.pop()
            self.menu_move_sound.play()
            self.battle_player_character_cards.children[
                self.current_player_index].change_icon()


    def use_consumable_item_on_targets(self, item: ConsumableItem, actor: player_character.PlayerCharacter,
                                       targets: list[character.Character]):
        """
        Uses a consumable item on a list of targets. Probably going to be used by the action queue. Probably.
        :param item: the item being used.
        :param actor: the actor using the item.
        :param targets: the targets that the actor is giving the item to.
        :return: None
        """

        actor.set_animation_state("battle_idle")
        arcade.play_sound(self.heal_sound)

        for target in targets:
            damage_healt = 0
            if item.is_revive_item:
                if target.hp < 0:
                    previous_target_hp = target.hp
                    target.hp = 1
                    damage_healt += target.hp - previous_target_hp
                if item.is_relative_healing_item:
                    amount_healed_by_percent = min(target.hp + (target.max_hp * item.hp_percentage_restored), target.max_hp)
                    target.hp = amount_healed_by_percent
                    damage_healt += amount_healed_by_percent
                else:
                    amount_healed_by_absolute = min(target.hp + item.hp_restored, target.max_hp)
                    target.hp += amount_healed_by_absolute
                    damage_healt += amount_healed_by_absolute
            else:
                if item.is_relative_healing_item:
                    amount_healed_by_percent = min(target.hp + (target.max_hp * item.hp_percentage_restored), target.max_hp)
                    target.hp += amount_healed_by_percent
                    damage_healt += amount_healed_by_percent
                else:
                    target.hp += item.hp_restored
                    damage_healt += item.hp_restored

            if target.hp > target.max_hp:
                target.hp = target.max_hp


            damage_healed_color = arcade.color.WHITE
            if damage_healt > 0:
                damage_healed_color = Color(0, 214, 0, 255)
                color_filter_animation = FadeInFadeOutColorAnimation(
                    sprite=target,
                    color=arcade.color.WHITE,
                    total_duration=0.3
                )
                self.effects_list.append(color_filter_animation)
                self.effects_sprite_list.append(color_filter_animation.filter_sprite)

                sparkle_animation = HealAnimation(
                    target=target
                )

                self.effects_list.append(sparkle_animation)
                for sprite in sparkle_animation.get_sprites():
                    self.effects_sprite_list.append(sprite)

            elif damage_healt < 0:
                target.set_animation_state("battle_hurt")
                shake_animation = ShakeAnimation(
                    sprite=target
                )
                self.effects_list.append(shake_animation)
                pyglet.clock.schedule_once(lambda dt: target.set_animation_state("battle_idle"), 1.0)
                arcade.play_sound(self.hurt_sound)

            damage_healt_text = str(abs(damage_healt))
            if target.hp >= target.max_hp:
                damage_healt_text = "MAX"


            damage_healed_animation = NumberBounceAnimation(
                text=damage_healt_text,
                color=damage_healed_color,
                target=target
            )

            self.effects_list.append(damage_healed_animation)
            self.effects_sprite_list.append(damage_healed_animation.sprite)

    def open_enemy_select_menu(self):
        """
        Opens the enemy select menu.
        :return: None
        """
        enemy_list_full_layout = EnemySelect(self.enemies)
        enemy_list_interactive_layout = enemy_list_full_layout.children[1]
        self.focus_stack.push(enemy_list_full_layout, enemy_list_interactive_layout,
                                         self.state, 1)
        new_focus_animation = self.focus_stack.get_highest_member().get_focused_widget().enemy.focus()
        self.effects_list.append(new_focus_animation)
        self.effects_sprite_list.append(new_focus_animation.filter_sprite)

    def move_focus_between_enemies_in_enemy_select(self, previously_focused_widget, currently_focused_widget):
        """
        Used to animate the enemies being targeted in the enemy select screen.
        :param previously_focused_widget: The previously focused enemy's row in the enemy select.
        :param currently_focused_widget: The newly focused enemy's row in the enemy select.
        :return:
        """
        new_focus_animation = currently_focused_widget.enemy.focus()
        self.effects_list.append(new_focus_animation)
        self.effects_sprite_list.append(new_focus_animation.filter_sprite)
        previously_focused_widget.enemy.unfocus()

    def open_player_select_menu(self):
        """
        Opens the player select menu.
        :return: None
        """
        player_list_full_layout = battle_widgets.PlayerSelect(self.player_characters)
        player_list_interactive_layout = player_list_full_layout
        self.focus_stack.push(player_list_full_layout, player_list_interactive_layout,
                                         self.state, 1)
        new_focus_animation = self.focus_stack.get_highest_member().get_focused_widget().player.focus()
        self.effects_list.append(new_focus_animation)
        self.effects_sprite_list.append(new_focus_animation.filter_sprite)

    def move_focus_between_players_in_player_select(self, previously_focused_widget, currently_focused_widget):
        """
        Used to animate the enemies being targeted in the enemy select screen.
        :param previously_focused_widget: The previously focused enemy's row in the enemy select.
        :param currently_focused_widget: The newly focused enemy's row in the enemy select.
        :return:
        """
        new_focus_animation = currently_focused_widget.player.focus()
        self.effects_list.append(new_focus_animation)
        self.effects_sprite_list.append(new_focus_animation.filter_sprite)
        previously_focused_widget.player.unfocus()

    def initialize_sorted_action_queue(self):
        """
        Populates self.sorted_actions_queue with a sorted list of the queued player character actions.
        Meant to be executed after the player selects the action of the last party member in the battle.
        Clears the actions queue before the next round.
        :return:
        """
        self.sorted_actions_queue = self.actions_queue.sort_actions_queue()
        self.actions_queue.clear()

    def execute_queued_player_action(self):
        """
        Executes the highest priority player action.
        :return: A bool representing whether there are any player actions left to execute.
        """
        if len(self.sorted_actions_queue["complex_act_actions"]) > 0:
            self.sorted_actions_queue["act_actions"].pop().execute()
            return
        if len(self.sorted_actions_queue["simple_act_actions"]) > 0:
            act_texts = ""
            for action in self.sorted_actions_queue["simple_act_actions"]:
                act_text = self.sorted_actions_queue["simple_act_actions"].pop().execute()
                act_texts += "* " + act_text + "\n"
            self.battle_textbox.load_dialog(TextBoxDialog(act_texts))
            return
        elif len(self.sorted_actions_queue["magic_spare_item_actions"]) > 0:
            self.sorted_actions_queue["magic_spare_item_actions"].pop().execute()
            return
        elif len(self.sorted_actions_queue["fight_actions"]) > 0:
            self.sorted_actions_queue["fight_actions"].pop().execute()
            return
        else:
            self.state = BattleState.ENEMY_ATTACK
            # TODO: Add code here to initiate the enemy attack.

    def change_player_icon(self, icon_path: str = ""):
        """ Changes the icon of the current player to the icon at the given path. """
        self.battle_player_character_cards.children[self.current_player_index].change_icon(icon_path)


class Command:
    """ The default command object. Represents the Command design pattern. """

    def __init__(self, controller: BattleController):
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
                            self.controller.focus_stack.push(spell_list_full_layout, spell_list_interactive_layout,
                                                             self.controller.state, 2)
                            return
                    case 2:  # user selects the ITEM button
                        self.controller.state = BattleState.PLAYER_ITEM_SELECT
                        item_list_full_layout = battle_widgets.ItemSelect(self.controller.items)
                        item_list_interactive_layout = item_list_full_layout.children[0]
                        self.controller.focus_stack.push(item_list_full_layout, item_list_interactive_layout,
                                                         self.controller.state, 2)
                        self.controller.focus_stack.get_highest_member().full_ui_layout.update_item_data(
                            self.controller.focus_stack.get_highest_member().get_focused_widget().item
                        )
                        return
                    case 3:  # user selects the SPARE button
                        self.controller.state = BattleState.PLAYER_SPARE_SELECT
                        self.controller.open_enemy_select_menu()
                        return
                    case 4:  # user selects the DEFEND button
                        defending_player_character = self.controller.focus_stack.get_highest_member().get_interactive_ui_layout().player_character
                        defend_action = DefendAction(
                            actor = defending_player_character,
                            targets=[],
                            controller=self.controller
                        )
                        self.controller.move_to_next_player_card(defend_action)
                        return

            case BattleState.PLAYER_ATTACK_SELECT:
                # TODO: Make the current player character enter the attack state, queue the attack
                # self.controller.move_to_next_player_card()
                return

            case BattleState.PLAYER_ACT_ENEMY_SELECT:
                # TODO: select the focused enemy, open the ACT menu for the selected enemy
                return

            case BattleState.PLAYER_ACT_SELECT:
                # TODO: select the focused act, animate the player character, queue the act
                # self.controller.move_to_next_player_card()
                return

            case BattleState.PLAYER_MAGIC_SELECT:
                self.controller.state = BattleState.PLAYER_MAGIC_ENEMY_SELECT
                spell = self.controller.focus_stack.get_highest_member().get_focused_widget().spell
                self.controller.tp_meter.update_tp_meter(-spell.tp_cost)
                self.controller.open_enemy_select_menu()
                self.controller.menu_select_sound.play()
                return

            case BattleState.PLAYER_MAGIC_ENEMY_SELECT:
                selected_target_enemy = self.controller.focus_stack.get_highest_member().get_focused_widget().enemy
                selected_target_enemy.unfocus()
                self.controller.focus_stack.pop()
                selected_spell = self.controller.focus_stack.get_highest_member().get_focused_widget().spell
                self.controller.focus_stack.pop()
                current_player_character = self.controller.focus_stack.get_highest_member().get_interactive_ui_layout().player_character

                spell_action = SpellAction(
                    actor=current_player_character,
                    targets=[selected_target_enemy],
                    spell=selected_spell,
                    controller=self.controller
                )

                self.controller.move_to_next_player_card(spell_action)
                return

            case BattleState.PLAYER_ITEM_SELECT:
                item = self.controller.focus_stack.get_highest_member().get_focused_widget().item
                item_index = self.controller.focus_stack.get_highest_member().get_focused_widget_index()
                if item.tp_restored > 0 and item.hp_restored == 0:  # If item is TP item exclusively
                    self.controller.focus_stack.pop()
                    current_player_character = self.controller.focus_stack.get_highest_member().get_interactive_ui_layout().player_character
                    item_action = ItemAction(
                        actor=current_player_character,
                        targets=[],
                        controller=self.controller,
                        item=item,
                        item_index=item_index
                    )
                    self.controller.move_to_next_player_card(item_action)
                    return
                if item.heals_all_party_members:  # If item affects all party members
                    # TODO: queue an ItemAction with the item
                    self.controller.focus_stack.pop()
                    current_player_character = self.controller.focus_stack.get_highest_member().get_interactive_ui_layout().player_character
                    item_action = ItemAction(
                        actor=current_player_character,
                        targets=self.controller.player_characters,
                        controller=self.controller,
                        item=item,
                        item_index=item_index
                    )
                    self.controller.move_to_next_player_card(item_action)
                    return
                self.controller.state = BattleState.PLAYER_ITEM_PLAYER_SELECT
                self.controller.open_player_select_menu()
                self.controller.menu_select_sound.play()
                return

            case BattleState.PLAYER_ITEM_PLAYER_SELECT:
                targeted_player_character = self.controller.focus_stack.get_highest_member().get_focused_widget().player
                targeted_player_character.unfocus()
                self.controller.focus_stack.pop()
                item = self.controller.focus_stack.get_highest_member().get_focused_widget().item
                item_index = self.controller.focus_stack.get_highest_member().get_focused_widget_index()
                self.controller.focus_stack.pop()
                player_using_item = self.controller.focus_stack.get_highest_member().get_interactive_ui_layout().player_character
                item_action = ItemAction(
                    actor=player_using_item,
                    targets=[targeted_player_character],
                    controller=self.controller,
                    item=item,
                    item_index=item_index
                )
                self.controller.move_to_next_player_card(item_action)
                self.controller.menu_select_sound.play()


            case BattleState.PLAYER_SPARE_SELECT:
                # animate the player character, queue the act
                selected_target_enemy = self.controller.focus_stack.get_highest_member().get_focused_widget().enemy
                selected_target_enemy.unfocus()

                self.controller.focus_stack.pop()

                current_player_character = self.controller.focus_stack.get_highest_member().get_interactive_ui_layout().player_character

                self.controller.battle_player_character_cards.children[
                    self.controller.current_player_index].change_icon(
                    "assets/textures/gui_graphics/action_icons/spare_icon.png")

                spare_action = SpareAction(
                    actor=current_player_character,
                    target=selected_target_enemy,
                    controller=self.controller
                )

                self.controller.move_to_next_player_card(spare_action)
                return

            case BattleState.EXECUTING_QUEUED_PLAYER_COMMANDS:
                self.controller.execute_queued_player_action()


class CancelCommand(Command):
    """ A command object representing the user canceling (usually pressing X in the original game.) """

    def execute(self):
        match self.controller.state:
            case BattleState.PLAYER_COMMAND:
                self.controller.move_to_previous_player_card()
                previous_player = self.controller.focus_stack.get_highest_member().get_interactive_ui_layout().player_character
                previous_player.set_animation_state("battle_idle")
            case BattleState.PLAYER_MAGIC_SELECT:
                self.backup_out_of_focus_stack()
            case BattleState.PLAYER_MAGIC_ENEMY_SELECT:
                focused_enemy = self.controller.focus_stack.get_highest_member().get_focused_widget().enemy
                focused_enemy.unfocus()
                self.backup_out_of_focus_stack()
            case BattleState.PLAYER_SPARE_SELECT:
                focused_enemy = self.controller.focus_stack.get_highest_member().get_focused_widget().enemy
                focused_enemy.unfocus()
                self.backup_out_of_focus_stack()
            case BattleState.PLAYER_ITEM_SELECT:
                self.backup_out_of_focus_stack()
            case BattleState.PLAYER_ITEM_PLAYER_SELECT:
                focused_player = self.controller.focus_stack.get_highest_member().get_focused_widget().player
                focused_player.unfocus()
                self.backup_out_of_focus_stack()

    def backup_out_of_focus_stack(self):
        """
        Used to back out of loaded battle UI elements while updating self.controller.state and the focus stack.
        Used a lot in CancelCommand.execute().
        :return: None
        """
        focus_stack_member = self.controller.focus_stack.pop()
        if focus_stack_member:
            self.controller.state = self.controller.focus_stack.get_highest_member().state
        self.controller.menu_move_sound.play()


class RightCommand(Command):
    """ A command object representing the user pressing right (usually pressing -> in the original game.) """

    def execute(self):
        if self.controller.focus_stack.get_highest_member().move_right():
            self.controller.menu_move_sound.play()
            match self.controller.state:
                case BattleState.PLAYER_MAGIC_SELECT:
                    self.controller.focus_stack.get_highest_member().full_ui_layout.update_spell_data(
                        self.controller.focus_stack.get_highest_member().get_focused_widget().spell
                    )
                case BattleState.PLAYER_ITEM_SELECT:
                    self.controller.focus_stack.get_highest_member().full_ui_layout.update_item_data(
                        self.controller.focus_stack.get_highest_member().get_focused_widget().item
                    )


class LeftCommand(Command):
    """ A command object representing the user pressing left (usually pressing <- in the original game.) """

    def execute(self):
        if self.controller.focus_stack.get_highest_member().move_left():
            self.controller.menu_move_sound.play()
            match self.controller.state:
                case BattleState.PLAYER_MAGIC_SELECT:
                    self.controller.focus_stack.get_highest_member().full_ui_layout.update_spell_data(
                        self.controller.focus_stack.get_highest_member().get_focused_widget().spell
                    )
                case BattleState.PLAYER_ITEM_SELECT:
                    self.controller.focus_stack.get_highest_member().full_ui_layout.update_item_data(
                        self.controller.focus_stack.get_highest_member().get_focused_widget().item
                    )


class UpCommand(Command):
    """ A command object representing the user pressing up (usually pressing the up arrow key in the original game.) """

    def execute(self):
        previously_focused_widget = self.controller.focus_stack.get_highest_member().get_focused_widget()
        if self.controller.focus_stack.get_highest_member().move_up():
            currently_focused_widget = self.controller.focus_stack.get_highest_member().get_focused_widget()
            self.controller.menu_move_sound.play()
            match self.controller.state:
                case BattleState.PLAYER_MAGIC_SELECT:
                    self.controller.focus_stack.get_highest_member().full_ui_layout.update_spell_data(
                        self.controller.focus_stack.get_highest_member().get_focused_widget().spell
                    )
                case BattleState.PLAYER_MAGIC_ENEMY_SELECT:
                    self.controller.move_focus_between_enemies_in_enemy_select(previously_focused_widget,
                                                                               currently_focused_widget)
                case BattleState.PLAYER_SPARE_SELECT:
                    self.controller.move_focus_between_enemies_in_enemy_select(previously_focused_widget,
                                                                               currently_focused_widget)
                case BattleState.PLAYER_ITEM_SELECT:
                    self.controller.focus_stack.get_highest_member().full_ui_layout.update_item_data(
                        self.controller.focus_stack.get_highest_member().get_focused_widget().item
                    )
                case BattleState.PLAYER_ITEM_PLAYER_SELECT:
                    self.controller.move_focus_between_players_in_player_select(previously_focused_widget,
                                                                               currently_focused_widget)


class DownCommand(Command):
    """
    A command object representing the user pressing down (usually pressing the down arrow key in the original game.)
    """

    def execute(self):
        previously_focused_widget = self.controller.focus_stack.get_highest_member().get_focused_widget()
        if self.controller.focus_stack.get_highest_member().move_down():
            currently_focused_widget = self.controller.focus_stack.get_highest_member().get_focused_widget()
            self.controller.menu_move_sound.play()
            match self.controller.state:
                case BattleState.PLAYER_MAGIC_SELECT:
                    self.controller.focus_stack.get_highest_member().full_ui_layout.update_spell_data(
                        self.controller.focus_stack.get_highest_member().get_focused_widget().spell
                    )
                case BattleState.PLAYER_MAGIC_ENEMY_SELECT:
                    self.controller.move_focus_between_enemies_in_enemy_select(previously_focused_widget,
                                                                               currently_focused_widget)
                case BattleState.PLAYER_SPARE_SELECT:
                    self.controller.move_focus_between_enemies_in_enemy_select(previously_focused_widget,
                                                                               currently_focused_widget)
                case BattleState.PLAYER_ITEM_SELECT:
                    self.controller.focus_stack.get_highest_member().full_ui_layout.update_item_data(
                        self.controller.focus_stack.get_highest_member().get_focused_widget().item
                    )
                case BattleState.PLAYER_ITEM_PLAYER_SELECT:
                    self.controller.move_focus_between_players_in_player_select(previously_focused_widget,
                                                                                currently_focused_widget)

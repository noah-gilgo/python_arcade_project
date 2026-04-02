from enum import Enum, auto

import arcade.color
import pyglet
from arcade import SpriteList
from arcade.gui import UIManager

import character
import non_player_character
import player_character
from animations.battle_animations import NumberBounceAnimation, EnemySparedAnimation, TPGainAnimation
from animations.common_animations import FadeInFadeOutColorAnimation
from dialogue_box import TextBoxDialog
from items import ConsumableItem
from spells import Spell

"""
This file contains the Action objects created when the user selects specific actions for player characters.
These seem identical to me to Command objects, but I'm calling them "action" objects to differentiate them from the
Command objects in battle_state_machine.py that are triggered by user inputs.
"""

class ActionType(Enum):
    FIGHT = auto()
    ACT = auto()
    SPELL = auto()
    ITEM = auto()
    SPARE = auto()
    DEFEND = auto()


class Action:
    def __init__(self, actor: player_character.PlayerCharacter = None,
                 targets: list[character.Character] = None,
                 controller = None,
                 is_immediate: bool = False):
        self.actor = actor
        self.targets = targets
        self.controller = controller
        self.is_immediate = is_immediate  # If "action" done immediately when selected (ex. TensionBit consumed)

    def execute(self):
        # Stub for the execute method used by child classes.
        pass

    def ready_act(self):
        # Performs code meant to be executed after selecting an act.
        pass

    def cancel_act(self):
        # Performs code meant to be executed after canceling an act.
        pass


class ActionsQueue:
    """
    When the player selects an action for a player character, it is added to this queue.
    """
    def __init__(self):
        self.actions = []

    def __len__(self):
        return len(self.actions)

    def push(self, action: Action):
        """
        Adds an action to the end of the actions queue.
        :param action: The action to be added.
        :return: None
        """
        self.actions.append(action)
        action.ready_act()

    def pop(self) -> Action:
        """
        Removes and returns the action at the end of the actions queue
        :return: the last action in the actions queue
        """
        action = self.actions.pop()
        action.cancel_act()
        return action

    def sort_actions_queue(self) -> dict[str, list[Action]]:
        """
        Returns the actions queue sorted in order of action priority.
        The returned list dict is passed into the BattleController, which will iterate through every action.
        :return: None
        """
        complex_act_actions = []
        simple_act_actions = []
        magic_spare_item_actions = []
        fight_actions = []

        for action in self.actions:
            if not action.is_immediate:
                if type(action) == ComplexActAction:
                    complex_act_actions.insert(0, action)
                elif type(action) == SimpleActAction:
                    complex_act_actions.insert(0, action)
                elif type(action) == SpellAction or type(action) == SpareAction or type(action) == ItemAction:
                    magic_spare_item_actions.insert(0, action)
                elif type(action) == FightAction:
                    fight_actions.insert(0, action)

        return {
            "complex_act_actions": complex_act_actions,
            "simple_act_actions": simple_act_actions,
            "magic_spare_item_actions": magic_spare_item_actions,
            "fight_actions": fight_actions
        }

    def clear(self):
        """ Empties the actions queue. """
        self.actions.clear()


class FightAction(Action):
    def __init__(self, actor: player_character.PlayerCharacter,
                 targets: list[character.Character],
                 controller):
        super().__init__(actor, targets, controller)

    def execute(self):
        pass
        # TODO: Add FIGHT action logic.


class SpellAction(Action):
    def __init__(self, actor: player_character.PlayerCharacter,
                 targets: list[character.Character],
                 spell: Spell,
                 controller):
        super().__init__(actor, targets, controller)
        self.spell = spell
        self.sprite_list = self.controller.effects_sprite_list
        self.animation_list = self.controller.effects_list

    def execute(self):
        # Casts the spell.
        targeted_enemies = []
        for target in self.targets:
            if target in self.controller.enemies:
                targeted_enemies.append(target)

        # If the spellcasters initial target leaves the battle before they can cast the spell, target another enemy.
        if len(self.targets) == 1 and len(targeted_enemies) == 0:
            targeted_enemies.append(self.controller.enemies[0])

        if len(targeted_enemies) > 0:
            self.actor.set_animation_state("battle_magic")
            self.controller.battle_textbox.load_dialog(TextBoxDialog(
                text="* " + self.actor.name + " cast " + self.spell.name + "!",
                rate_of_text=0.03
            ))
            pyglet.clock.schedule_once(lambda dt: self.spell.animate_spell(targeted_enemies, self.sprite_list, self.animation_list), 0.5)
            pyglet.clock.schedule_once(lambda dt: self.spell.affect_targets_with_spell(self.actor, targeted_enemies, self.controller), 1.0)
            pyglet.clock.schedule_once(lambda dt: self.actor.set_animation_state("battle_idle"), 0.7)
        else:
            self.actor.set_animation_state("battle_idle")

    def ready_act(self):
        self.actor.set_animation_state("battle_magic_ready")

        self.controller.change_player_icon("assets/textures/gui_graphics/action_icons/magic_icon.png")

    def cancel_act(self):
        self.controller.add_tp_to_meter(self.spell.tp_cost)

"""
class ImmediateAction(Action):
    # This is a class for special actions that execute immediately when the player

    def __init__(self, actor: player_character.PlayerCharacter, targets: list[character.Character], controller):
        super().__init__(actor, targets, controller)
        #TODO: build the rest of this out

    def execute(self):
        pass
        # TODO: Add immediate action logic.
"""

class SimpleActAction(Action):
    def __init__(self, actor: player_character.PlayerCharacter, targets: list[character.Character], controller,
                 flavor_text: str = "", spare_percentage: int = 10):
        super().__init__(actor, targets, controller)
        #TODO: build the rest of this out
        self.spare_percentage = spare_percentage
        self.flavor_text = ""
        if flavor_text:
            self.flavor_text = flavor_text
        else:
            self.flavor_text = actor.name + " did something to " + targets[0].name + "!"

    def execute(self):
        # TODO: Add ACT action logic.
        return self.flavor_text


class ComplexActAction(Action):
    def __init__(self, actor: player_character.PlayerCharacter, targets: list[character.Character], controller):
        super().__init__(actor, targets, controller)
        #TODO: build the rest of this out

    def execute(self):
        pass
        # TODO: Add ACT action logic.


class ItemAction(Action):
    def __init__(self, actor: player_character.PlayerCharacter, targets: list[character.Character], controller,
                 item: ConsumableItem, item_index: int = 0):
        super().__init__(actor, targets, controller)
        self.item = item
        self.item_index = item_index

    def execute(self):
        pass
        self.actor.set_animation_state("battle_item")
        item_text = "* " + self.actor.name + " used the " + self.item.name.upper() + "!"
        self.controller.battle_textbox.load_dialog(TextBoxDialog(text=item_text))
        pyglet.clock.schedule_once(
            lambda dt: self.controller.use_consumable_item_on_targets(self.item, self.actor, self.targets), 0.5)

    def ready_act(self):
        if self.item.tp_restored > 0 and self.item.hp_restored == 0:  # If item is TP item exclusively
            self.is_immediate = True
            self.controller.tp_meter.update_tp_meter(self.item.tp_restored)
            self.controller.tp_add_sound.play()
            tp_gain_sparkles_animation = TPGainAnimation(
                target=self.actor
            )
            color_filter_animation = FadeInFadeOutColorAnimation(
                sprite=self.actor,
                color=arcade.color.WHITE,
                total_duration=0.3
            )

            self.controller.effects_list.append(tp_gain_sparkles_animation)
            for sprite in tp_gain_sparkles_animation.get_sprites():
                self.controller.effects_sprite_list.append(sprite)

            self.controller.effects_list.append(color_filter_animation)
            self.controller.effects_sprite_list.append(color_filter_animation.filter_sprite)

        else:
            self.actor.set_animation_state("battle_item_ready")
        if self.item.is_consumable:
            self.controller.items.remove(self.item)

        self.controller.change_player_icon("assets/textures/gui_graphics/action_icons/item_icon.png")

    def cancel_act(self):
        if self.item.tp_restored > 0 and self.item.hp_restored == 0:  # If item is TP item exclusively
            # In the event that the item is a TP item exclusively, reduce the TP in the TP meter by the provided amount.
            self.controller.tp_meter.update_tp_meter(-self.item.tp_restored)
        if self.item.is_consumable:
            self.controller.items.insert(self.item_index, self.item)


class SpareAction(Action):
    def __init__(self, actor: player_character.PlayerCharacter, target: non_player_character.NonPlayerCharacter, controller):
        super().__init__(actor=actor, controller=controller)
        self.target = target

    def ready_act(self):
        self.actor.set_animation_state("battle_spare_ready")

        self.controller.change_player_icon("assets/textures/gui_graphics/action_icons/spare_icon.png")

    def cancel_act(self):
        self.actor.set_animation_state("battle_idle")

    def execute(self):
        # Makes the provided actor attempt to spare the focused enemy.
        self.actor.set_animation_state("battle_spare")
        spare_message = "* " + self.actor.name + " spared " + self.target.name + "! "

        if self.target.mercy < 100:
            # Add mercy to the targets mercy meter.
            self.target.mercy = min(self.target.mercy + 10, 100)

            if self.target.mercy == 100:
                pyglet.clock.schedule_once(
                    lambda dt: self.target.set_animation_state("battle_spared"), 0.5)

            # Append a message telling the user that the enemy wasn't spared to the spare message.
            spare_message += "\n    But it's name wasn't YELLOW..."

            # Animate the spare percent number bounce and the yellow fade in fade out animation on the spared enemy.
            fade_in_out_animation = FadeInFadeOutColorAnimation(
                sprite=self.target,
                color=arcade.color.YELLOW,
                max_alpha=128,
                total_duration=0.6
            )

            spare_percent_number_animation = NumberBounceAnimation(
                target=self.target,
                text="+10%",
                color=arcade.color.GOLD
            )

            pyglet.clock.schedule_once(
                lambda dt: self.controller.effects_list.append(fade_in_out_animation), 0.5)
            pyglet.clock.schedule_once(
                lambda dt: self.controller.effects_sprite_list.append(fade_in_out_animation.filter_sprite), 0.5)

            pyglet.clock.schedule_once(
                lambda dt: self.controller.effects_list.append(spare_percent_number_animation), 0.55)
            pyglet.clock.schedule_once(
                lambda dt: self.controller.effects_sprite_list.append(spare_percent_number_animation.sprite), 0.55)
            pyglet.clock.schedule_once(
                lambda dt: self.controller.mercy_add_sound.play(), 0.55)
        else:
            # Animate the enemy being spared.
            spare_animation = EnemySparedAnimation(target=self.target)
            spare_animation_sprites = spare_animation.get_sprites()

            pyglet.clock.schedule_once(
                lambda dt: self.controller.effects_list.append(spare_animation), 0.5)
            for spare_animation_sprite in spare_animation_sprites:
                pyglet.clock.schedule_once(
                    lambda dt, sprite=spare_animation_sprite: self.controller.effects_sprite_list.append(sprite), 0.5)

            # Play the spare sound.
            pyglet.clock.schedule_once(
                lambda dt: self.controller.spare_sound.play(), 0.5)

            # Remove the enemy from the battle.
            self.controller.enemies.remove(self.target)

        self.controller.battle_textbox.load_dialog(TextBoxDialog(
            text=spare_message,
            rate_of_text=0.03
        ))

        pyglet.clock.schedule_once(lambda dt: self.actor.set_animation_state("battle_idle"), 0.7)


class DefendAction(Action):
    def __init__(self, actor: player_character.PlayerCharacter, targets: list[character.Character], controller):
        super().__init__(actor, targets, controller)
        self.is_immediate = True

    def ready_act(self):
        self.controller.add_tp_to_meter(16.0)
        self.actor.defend()
        self.controller.change_player_icon("assets/textures/gui_graphics/action_icons/defend_icon.png")

    def cancel_act(self):
        self.controller.add_tp_to_meter(-16.0)
        self.actor.undefend()

from enum import Enum, auto

import arcade.color
import pyglet
from arcade import SpriteList
from arcade.gui import UIManager

import character
import non_player_character
import player_character
from animations.battle_animations import NumberBounceAnimation, EnemySparedAnimation
from animations.common_animations import FadeInFadeOutColorAnimation
from dialogue_box import TextBoxDialog
from spells import Spell


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
                 controller = None):
        self.actor = actor
        self.targets = targets
        self.controller = controller

    def execute(self):
        pass
        # TODO: Add FIGHT action logic.


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

    def pop(self) -> Action:
        """
        Removes and returns the action at the end of the actions queue
        :return: the last action in the actions queue
        """
        return self.actions.pop()

    def sort_actions_queue(self) -> dict[str, list[Action]]:
        """
        Returns the actions queue sorted in order of action priority.
        The returned list dict is passed into the BattleController, which will iterate through every action.
        :return: None
        """
        immediate_actions = []
        act_actions = []
        magic_spare_item_actions = []
        fight_actions = []
        unknown_type_actions = []

        for action in self.actions:
            if type(action) == ImmediateAction:
                immediate_actions.append(action)
            elif type(action) == ActAction:
                act_actions.append(action)
            elif type(action) == SpellAction or type(action) == SpareAction or type(action) == ItemAction:
                magic_spare_item_actions.append(action)
            elif type(action) == FightAction:
                fight_actions.append(action)
            else:
                unknown_type_actions.append(action)

        return {
            "act_actions": act_actions,
            "magic_spare_item_actions": magic_spare_item_actions,
            "fight_actions": fight_actions,
            "unknown_type_actions": unknown_type_actions
        }

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
        self.actor.set_animation_state("battle_magic")
        self.controller.battle_textbox.load_dialog(TextBoxDialog(
            text="* " + self.actor.name + " cast " + self.spell.name + "!",
            rate_of_text=0.03
        ))
        pyglet.clock.schedule_once(lambda dt: self.spell.animate_spell(self.targets, self.sprite_list, self.animation_list), 0.5)
        pyglet.clock.schedule_once(lambda dt: self.spell.affect_targets_with_spell(self.actor, self.targets, self.controller), 1.0)
        pyglet.clock.schedule_once(lambda dt: self.actor.set_animation_state("battle_idle"), 0.7)


class ImmediateAction(Action):
    """
    This is a class for special actions that execute immediately when the player
    """
    def __init__(self, actor: player_character.PlayerCharacter, targets: list[character.Character], controller):
        super().__init__(actor, targets, controller)
        #TODO: build the rest of this out

    def execute(self):
        pass
        # TODO: Add immediate action logic.


class ActAction(Action):
    def __init__(self, actor: player_character.PlayerCharacter, targets: list[character.Character], controller):
        super().__init__(actor, targets, controller)
        #TODO: build the rest of this out

    def execute(self):
        pass
        # TODO: Add ACT action logic.


class ItemAction(Action):
    def __init__(self, actor: player_character.PlayerCharacter, targets: list[character.Character], controller):
        super().__init__(actor, targets, controller)
        #TODO: build the rest of this out

    def execute(self):
        pass
        # TODO: Add ITEM action logic.


class SpareAction(Action):
    def __init__(self, actor: player_character.PlayerCharacter, target: non_player_character.NonPlayerCharacter, controller):
        super().__init__(actor=actor, controller=controller)
        self.target = target

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

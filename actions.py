from enum import Enum, auto

import arcade.color
import pyglet
from arcade import SpriteList
from arcade.gui import UIManager

import character
import non_player_character
import player_character
from animations.battle_animations import NumberBounceAnimation
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


class ItemAction(Action):
    def __init__(self, actor: player_character.PlayerCharacter, targets: list[character.Character], controller):
        super().__init__(actor, targets, controller)
        #TODO: build the rest of this out


class SpareAction(Action):
    def __init__(self, actor: player_character.PlayerCharacter, target: non_player_character.NonPlayerCharacter, controller):
        super().__init__(actor=actor, controller=controller)
        self.target = target

    def execute(self):
        # Makes the provided actor attempt to spare the focused enemy.
        self.actor.set_animation_state("battle_spare")
        spare_message = "* " + self.actor.name + " spared " + self.target.name + "! "
        self.target.mercy = min(self.target.mercy + 10, 100)

        if self.target.mercy < 100:
            # Append a message telling the user that the enemy wasn't spared to the spare message.
            spare_message += "\n    But it's name wasn't YELLOW..."
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
                lambda dt: self.controller.effects_list.append(spare_percent_number_animation), 0.55)
            pyglet.clock.schedule_once(
                lambda dt: self.controller.effects_sprite_list.append(spare_percent_number_animation.sprite), 0.55)

            pyglet.clock.schedule_once(
                lambda dt: self.controller.effects_list.append(fade_in_out_animation), 0.5)
            pyglet.clock.schedule_once(
                lambda dt: self.controller.effects_sprite_list.append(fade_in_out_animation.filter_sprite), 0.5)
        else:
            # TODO: Add the animations for sparing the enemy and removing them from the battle.
            pass

        self.controller.battle_textbox.load_dialog(TextBoxDialog(
            text=spare_message,
            rate_of_text=0.03
        ))

        pyglet.clock.schedule_once(lambda dt: self.actor.set_animation_state("battle_idle"), 0.7)

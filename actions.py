from enum import Enum, auto

import pyglet
from arcade import SpriteList
from arcade.gui import UIManager

import character
import non_player_character
import player_character
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
    def __init__(self, actor: player_character.PlayerCharacter,
                 targets: list[character.Character],
                 controller):
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
            rate_of_text=0.04
        ))
        pyglet.clock.schedule_once(lambda dt: self.spell.animate_spell(self.targets, self.sprite_list, self.animation_list), 0.5)
        pyglet.clock.schedule_once(lambda dt: self.spell.affect_targets_with_spell(self.actor, self.targets, self.controller), 1.0)
        pyglet.clock.schedule_once(lambda dt: self.actor.set_animation_state("battle_idle"), 0.7)

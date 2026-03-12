from enum import Enum, auto

import pyglet
from arcade import SpriteList

import character
import non_player_character
import player_character
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
                 targets: list[character.Character]):
        self.actor = actor
        self.targets = targets


class FightAction(Action):
    def __init__(self, actor: player_character.PlayerCharacter,
                 targets: list[character.Character]):
        super().__init__(actor, targets)

    def execute(self):
        pass
        # TODO: Add FIGHT action logic.


class SpellAction(Action):
    def __init__(self, actor: player_character.PlayerCharacter,
                 targets: list[character.Character],
                 spell: Spell,
                 sprite_list: SpriteList,
                 animation_list: list):
        super().__init__(actor, targets)
        self.spell = spell
        self.sprite_list = sprite_list
        self.animation_list = animation_list

    def execute(self):
        # Casts the spell.
        print("Spell Action executed")
        self.actor.set_animation_state("battle_magic")
        pyglet.clock.schedule_once(lambda dt: self.spell.animate_spell(self.targets, self.sprite_list, self.animation_list), 0.5)
        pyglet.clock.schedule_once(lambda dt: self.spell.affect_targets_with_spell(self.actor, self.targets), 1.5)

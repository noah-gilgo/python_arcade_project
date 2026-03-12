from copy import copy, deepcopy

import pyglet.clock

import character
import default_data
import non_player_character
from character import Character
from elemental_pairs import ElementalPair
from graphics_objects import MultiSpriteAnimation


class Spell:
    """ Parent class for spells """
    def __init__(self, name: str = "Default Spell", description: str = "", tp_cost: int = 0, element_id: int = 0,
                 base_health_change: int = 0, is_friendly_spell: bool = False, is_healing_spell: bool = False,
                 is_pacifying_spell: bool = False, is_aoe_spell: bool = False, animation: MultiSpriteAnimation = None):
        self.name = name  # Name of the spell
        self.description = description
        self.tp_cost = tp_cost  # TP cost of the spell
        self.element_id = element_id  # elemental pair associated with the spell, if any
        self.base_health_change = base_health_change  # amount health changed by spell
        self.is_friendly_spell = is_friendly_spell  # True if the intended target is player characters
        self.is_healing_spell = is_healing_spell  # True if the spell is healing
        self.is_pacifying_spell = is_pacifying_spell  # True if the spell is meant to pacify the target
        self.is_aoe_spell = is_aoe_spell  # True if the spell affects all targets on the targeted side
        self.animation = animation

    def affect_targets_with_spell(self, caster, targets):
        """ Perform the calculations required after a spell is cast on a character. """
        # TODO: Maybe add percentages to elemental pairs to control how much damage is resisted/amplified?
        for target in targets:
            if self.is_friendly_spell:
                new_hp = target.hp + self.base_health_change
                if new_hp < target.max_hp:
                    target.hp = new_hp
                else:
                    target.hp = target.max_hp
            else:
                damage_dealt = self.base_health_change
                if self.element_id:
                    for element in default_data.ELEMENTAL_PAIRS:
                        if element.element_id == self.element_id:
                            if target.element_id in element.resistant_to:
                                damage_dealt *= 0.66
                            if target.element_id in element.weak_to:
                                damage_dealt *= 1.5

                target.hp -= int(damage_dealt)

    def animate_spell(self, targets: list[character.Character], spell_sprite_list, animation_list):
        """ Animate the spell being cast. """
        for target in targets:
            new_animation = self.animation.__class__(target.center_x, target.center_y)
            animation_list.append(new_animation)
            new_animation.center_x = target.center_x
            new_animation.center_y = target.center_y
            for animated_sprite in new_animation.sprites:
                spell_sprite_list.append(animated_sprite.sprite)


def generate_basic_spells():
    """ Generates some basic spells from Deltarune. """
    pass

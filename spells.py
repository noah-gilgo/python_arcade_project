import pyglet.clock

import default_data
from character import Character
from elemental_pairs import ElementalPair
from player_character import PlayerCharacter


class Spell:
    """ Parent class for spells """
    def __init__(self, name: str = "Default Spell", tp_cost: int = 0, element_id: int = 0,
                 base_health_change: int = 0, is_friendly_spell: bool = False, is_healing_spell: bool = False,
                 is_pacifying_spell: bool = False, is_aoe_spell: bool = False):
        self.name = name  # Name of the spell
        self.tp_cost = tp_cost  # TP cost of the spell
        self.element_id = element_id  # elemental pair associated with the spell, if any
        self.base_health_change = base_health_change  # amount health changed by spell
        self.is_friendly_spell = is_friendly_spell  # True if the intended target is player characters
        self.is_healing_spell = is_healing_spell  # True if the spell is healing
        self.is_pacifying_spell = is_pacifying_spell  # True if the spell is meant to pacify the target
        self.is_aoe_spell = is_aoe_spell  # True if the spell affects all targets on the targeted side

        # Used for the (spell)cast function
        self._caster = None
        self._targets = []

    def affect_targets_with_spell(self):
        """ Perform the calculations required after a spell is cast on a character. """
        # TODO: Maybe add percentages to elemental pairs to control how much damage is resisted/amplified?
        for target in self._targets:
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
                        if element["element_id"] == self.element_id:
                            if target.element_id in element.resistant_to:
                                damage_dealt *= 0.66
                            if target.element_id in element.weak_to:
                                damage_dealt *= 1.5

                target.hp -= int(damage_dealt)

    def animate_spell(self):
        """ Animate the spell being cast. """
        # TODO: Actually animate the spell.
        pyglet.clock.schedule_once(self.affect_targets_with_spell, 0.5)
        pass

    def cast(self, caster: PlayerCharacter, targets: list[Character]):
        """ Casts a spell originating from the caster at the supplied targets. """
        self._caster = caster
        self._targets = targets
        caster.set_animation_state("battle_magic")
        pyglet.clock.schedule_once(self.animate_spell, 0.5)



def generate_basic_spells():
    """ Generates some basic spells from Deltarune. """
    pass

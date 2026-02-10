from character import Character
from non_player_character import NonPlayerCharacter
from player_character import PlayerCharacter


class ElementalPair:
    """ Allows the user to assign an "element" to certain spells/attacks. """
    def __init__(self, element_id: int = 0, name: str = "None", resistant_to: list[int] = None,
                 weak_to: list[int] = None):
        self.element_id = element_id
        self.name = name
        self.resistant_to = resistant_to
        self.weak_to = weak_to


def generate_elemental_pairs():
    """
    Generates the default elemental pairs used in Deltarune.
    NOTE: some of these are non-canonical
    """
    return [
        ElementalPair(
            element_id=1,
            name="Holy/Electric",
            resistant_to=[1, 5, 7],
        ),
        ElementalPair(
            element_id=2,
            name="Life/Earth",
            resistant_to=[1, 2, 3],
            weak_to=[7, 8, 9]
        ),
        ElementalPair(
            element_id=3,
            name="Water/Night",
            resistant_to=[3, 8, 6],
            weak_to=[1]
        ),
        ElementalPair(
            element_id=4,
            name="Bird/Wind",
            resistant_to=[2, 4, 9],
            weak_to=[1, 7]
        ),
        ElementalPair(
            element_id=5,
            name="Dark/Star",
            resistant_to=[3, 5],
            weak_to=[1]
        ),
        ElementalPair(
            element_id=5,
            name="Dark/Star",
            resistant_to=[5],
            weak_to=[1, 9]
        ),
        ElementalPair(
            element_id=6,
            name="Puppet/Cat",
            resistant_to=[6],
            weak_to=[3]
        ),
        ElementalPair(
            element_id=7,
            name="System/Mouse",
            resistant_to=[5, 6, 7],
            weak_to=[1, 8]
        ),
        ElementalPair(
            element_id=8,
            name="Fire/Ice",
            resistant_to=[8],
            weak_to=[3]
        ),
        ElementalPair(
            element_id=9,
            name="Death/Scythe",
            resistant_to=[2, 8, 9],
            weak_to=[10]
        ),
        ElementalPair(
            element_id=10,
            name="Hopes/Dreams",
            resistant_to=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        )
    ]


class Spell:
    """ Parent class for spells """
    def __init__(self, tp_cost: int, element: ElementalPair, is_friendly_spell: bool = False,
                 is_healing_spell: bool = False, is_aoe_spell: bool = False):
        self.tp_cost = tp_cost
        self.element = element
        self.is_friendly_spell = is_friendly_spell  # True if the intended target is player characters
        self.is_healing_spell = is_healing_spell  # True if the spell is healing
        self.is_aoe_spell = is_aoe_spell  # True if the spell affects all targets on the targeted side

    def cast(self):
        """ Template for the function for casting spells. """
        pass

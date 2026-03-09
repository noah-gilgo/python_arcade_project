from elemental_pairs import ElementalPair

ELEMENTAL_PAIRS = [
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
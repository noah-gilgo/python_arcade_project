class Item:
    def __init__(self, name: str = "default item name", description: str = "this is the default item description."):
        self.id = None
        self.name = name
        self.description = description


class ConsumableItem(Item):
    def __init__(self, name: str = "default item name", description: str = "this is the default item description.",
                 id: int = None, hp_restored: int = 0, tp_restored: int = 0, is_revive_item: bool = False,
                 is_relative_healing_item: bool = False, hp_percentage_restored: float = 1.0):
        super().__init__(name, description)
        self.id = id
        self.hp_restored = hp_restored  # Amount of health healed with absolute healing
        self.tp_restored = tp_restored  # Amount of tension points restored
        self.is_revive_item = is_revive_item  # If true, heals the party member to at least 1 health
        self.is_relative_healing_item = is_relative_healing_item  # If true, heals a percentage of max health
        self.hp_percentage_restored = hp_percentage_restored  # Percentage of max health healed with relative healing


class ArmorItem(Item):
    def __init__(self, id: int = None, name: str = "default item name",
                 description: str = "this is the default item description.", attack_points: int = 1,
                 defense_points: int = 1, magic_points: int = 1):
        super().__init__(name, description)
        self.id = id
        self.attack_points = attack_points
        self.defense_points = defense_points
        self.magic_points = magic_points


class WeaponItem(Item):
    def __init__(self, id: int = None, name: str = "default item name",
                 description: str = "this is the default item description.", attack_points: int = 1,
                 defense_points: int = 1, magic_points: int = 1):
        super().__init__(name, description)
        self.id = id
        self.attack_points = attack_points
        self.defense_points = defense_points
        self.magic_points = magic_points


def initialize_default_items():
    """ Initializes some basic items. """

    consumables = [
        ConsumableItem(
            name="Dark Candy",
            description="Heals 40 HP. A red-and-black star that tastes like marshmallows.",
            hp_restored=40
        ),
        ConsumableItem(
            name="Revive Mint",
            description="Heals a fallen ally to MAX HP. A minty green crystal.",
            is_revive_item=True,
            is_relative_healing_item=True,
            hp_percentage_restored=1.0
        ),
        ConsumableItem(
            name="Tension Bit",
            description="Raises TP by 32% in battle.",
            tp_restored=32
        )
    ]

    consumable_id = 1
    for consumable in consumables:
        consumable.id = consumable_id
        consumable_id += 1

    return consumables

from items.items import Item


class ConsumableItem(Item):
    def __init__(self, name: str = "default item name", description: str = "this is the default item description.",
                 battle_description: str = "", id: int = None, hp_restored: int = 0, tp_restored: int = 0,
                 is_revive_item: bool = False, is_relative_healing_item: bool = False,
                 hp_percentage_restored: float = 1.0, heals_all_party_members: bool = False,
                 is_consumable: bool = True, time_before_player_can_advance_past_item: float = 1.4):
        super().__init__(name, description)
        self.id = id
        self.battle_description = battle_description
        self.hp_restored = hp_restored  # Amount of health healed with absolute healing
        self.tp_restored = tp_restored  # Amount of tension points restored
        self.heals_all_party_members = heals_all_party_members
        self.is_revive_item = is_revive_item  # If true, heals the party member to at least 1 health
        if self.is_revive_item:
            self.is_relative_healing_item = True  # Revive items only bring players up to 1 hp. the percent does the rest
        else:
            self.is_relative_healing_item = is_relative_healing_item  # If true, heals a percentage of max health
        self.hp_percentage_restored = hp_percentage_restored  # Percentage of max health healed with relative healing
        self.is_consumable = is_consumable  # If true, item will not be consumed when used in battle
        self.time_before_player_can_advance_past_item = time_before_player_can_advance_past_item  # If provided, the amount of time player input will be delayed while the item is being consumed


def initialize_default_consumable_items():
    """ Initializes some basic items. """

    consumables = [
        ConsumableItem(
            name="Glowshard",
            description="A shimmering shard. Its value increases each Chapter.",
            battle_description="Sell at shops",
            hp_restored=40,
            is_consumable=False
        ),
        ConsumableItem(
            name="Darker Candy",
            description="A candy that has grown sweeter with time. Said to taste like toasted marshmallow. +120HP",
            battle_description="Heals 120HP",
            hp_restored=120
        ),
        ConsumableItem(
            name="Scarlixir",
            description="A red brew with a sickeningly fruity taste. Recovers 160 HP.",
            battle_description="Heals 160HP",
            hp_restored=160
        ),
        ConsumableItem(
            name="Top Cake",
            description="This cake will make your taste buds spin! Heals 160HP to the team.",
            battle_description="Heals team 160HP",
            hp_restored=160,
            heals_all_party_members=True
        ),
        ConsumableItem(
            name="Revive Mint",
            description="Heals a fallen ally to MAX HP. A minty green crystal.",
            battle_description="Heal Downed Ally",
            is_revive_item=True,
            hp_percentage_restored=1.0
        ),
        ConsumableItem(
            name="Tension Bit",
            description="Raises TP by 32% in battle.",
            battle_description="Raises TP 32%",
            tp_restored=32
        ),
        ConsumableItem(
            name="S.POISON",
            description="A strange concoction made of colorful squares. Will poison you.",
            battle_description="Hurts party member",
            hp_restored=-40
        ),
        ConsumableItem(
            name="Bitter Tear",
            description="Bitter water that fell in droplets from the sky. Recovers all HP.",
            battle_description="Heals all HP",
            is_relative_healing_item=True,
            hp_percentage_restored=1.0
        ),
        ConsumableItem(
            name="FavSandwich",
            description="You'd think it tastes perfect.",
            battle_description="Heals 500 HP",
            hp_restored=500
        ),
        ConsumableItem(
            name="CD Bagel",
            description="A bagel with a reflective inside. Makes music with each bite. +80HP",
            battle_description="Heals 80 HP",
            hp_restored=80
        ),
        ConsumableItem(
            name="Tension Max",
            description="Raises TP to full in battle.",
            battle_description="Raises TP MAX",
            tp_restored=100
        ),
        ConsumableItem(
            name="BScotch Pie",
            description="A pie made by mom. Recovers all HP for all party members.",
            battle_description="Heals all team HP",
            is_relative_healing_item=True,
            hp_percentage_restored=1.0,
            heals_all_party_members=True
        ),
    ]

    consumable_id = 1
    for consumable in consumables:
        consumable.id = consumable_id
        consumable_id += 1

    return consumables


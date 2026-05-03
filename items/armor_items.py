from items.items import Item


class ArmorItem(Item):
    def __init__(self, id: int = None, name: str = "default item name",
                 description: str = "this is the default item description.", attack_points: int = 0,
                 defense_points: int = 0, magic_points: int = 0, element_id: int = 0):
        super().__init__(name, description)
        self.id = id
        self.attack_points = attack_points
        self.defense_points = defense_points
        self.magic_points = magic_points
        self.element_id = element_id


class WhiteRibbon(ArmorItem):
    def __init__(self):
        super().__init__(
            id=1,
            name="White Ribbon",
            description="A crinkly hair ribbon that slightly increases your defense.",
            defense_points=2,
        )


class ShadowMantle(ArmorItem):
    def __init__(self):
        super().__init__(
            id=2,
            name="Shadow Mantle",
            description="Shadows slip off like water. Greatly protects against Dark and Star attacks.",
            defense_points=4,
            magic_points=1,
            element_id=5
        )


class Jevilstail(ArmorItem):
    def __init__(self):
        super().__init__(
            id=3,
            name="Jevilstail",
            description="A J-shaped tail that gives you devilenergy.",
            attack_points=2,
            defense_points=2,
            magic_points=2,
            element_id=9
        )


class RoyalPin(ArmorItem):
    def __init__(self):
        super().__init__(
            id=4,
            name="RoyalPin",
            description="A brooch engraved with Queen's face. Careful of the sharp point.",
            defense_points=3,
            magic_points=1
        )


class TennaTie(ArmorItem):
    def __init__(self):
        super().__init__(
            id=5,
            name="TennaTie",
            description="A giant, heavy-duty, bullet-proof tie. How to even wear it...?",
            defense_points=5,
            magic_points=-2
        )


class WaferGuard(ArmorItem):
    def __init__(self):
        super().__init__(
            id=6,
            name="Waferguard",
            description="Although it looks brittle, it contains a magical energy that blunts damage on impact. +4DF",
            defense_points=4
        )


class MysticBand(ArmorItem):
    def __init__(self):
        super().__init__(
            id=7,
            name="MysticBand",
            description="A silver armlet stained with amber. Increases magic only. MAG +4",
            magic_points=4
        )


class PowerBand(ArmorItem):
    def __init__(self):
        super().__init__(
            id=8,
            name="PowerBand",
            description="A silver armlet stained with red essence. Increases strength only. ATK +4",
            attack_points=4
        )


class PrincessRbn(ArmorItem):
    def __init__(self):
        super().__init__(
            id=9,
            name="PrincessRBN",
            description="Elegant lace ribbon with gloves, delicate enough to see through. +4 DEF +2 ATK",
            attack_points=2,
            defense_points=4
        )

def initialize_default_armor_items():
    """ Initializes some basic armors. """
    return [
        WhiteRibbon(),
        ShadowMantle(),
        Jevilstail(),
        RoyalPin(),
        TennaTie(),
        WaferGuard(),
        MysticBand(),
        PowerBand(),
        PrincessRbn()
    ]

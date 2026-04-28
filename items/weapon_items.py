from items.items import Item

class WeaponItem(Item):
    def __init__(self, id: int = None, name: str = "default item name",
                 description: str = "this is the default item description.", attack_points: int = 0,
                 defense_points: int = 0, magic_points: int = 0, element_id: int = 0):
        super().__init__(name, description)
        self.id = id
        self.attack_points = attack_points
        self.defense_points = defense_points
        self.magic_points = magic_points
        self.element_id = element_id


class Sword(WeaponItem):
    """
    Represents sword weapons. Predominantly equippable by Kris in the main game.
    """
    def __init__(self, id: int = None, name: str = "default item name",
                 description: str = "this is the default item description.", attack_points: int = 0,
                 defense_points: int = 0, magic_points: int = 0):
        super().__init__(id, name, description, attack_points, defense_points, magic_points)


class Axe(WeaponItem):
    """
    Represents axe weapons. Predominantly equippable by Susie in the main game.
    """

    def __init__(self, id: int = None, name: str = "default item name",
                 description: str = "this is the default item description.", attack_points: int = 0,
                 defense_points: int = 0, magic_points: int = 0):
        super().__init__(id, name, description, attack_points, defense_points, magic_points)


class Scarf(WeaponItem):
    """
    Represents scarf weapons. Predominantly equippable by Ralsei in the main game.
    """

    def __init__(self, id: int = None, name: str = "default item name",
                 description: str = "this is the default item description.", attack_points: int = 0,
                 defense_points: int = 0, magic_points: int = 0):
        super().__init__(id, name, description, attack_points, defense_points, magic_points)


class Ring(WeaponItem):
    """
    Represents ring weapons. Predominantly equippable by Noelle in the main game.
    """

    def __init__(self, id: int = None, name: str = "default item name",
                 description: str = "this is the default item description.", attack_points: int = 0,
                 defense_points: int = 0, magic_points: int = 0):
        super().__init__(id, name, description, attack_points, defense_points, magic_points)


class JingleBlade(Sword):
    def __init__(self):
        super().__init__(
            id=1,
            name="JingleBlade",
            description="A lance-like sword with red-and-white stripes. Perfect for jousting.",
            attack_points=7,
            defense_points=1
        )


class JusticeAxe(Axe):
    def __init__(self):
        super().__init__(
            id=2,
            name="JusticeAxe",
            description="It has no special powers. However, in order to attain this item, you became much stronger!",
            attack_points=12
        )


class ScarfMark(Axe):
    def __init__(self):
        super().__init__(
            id=3,
            name="ScarfMark",
            description="A thin scarf with a deep sheen. Holy writing has been pressed into it, imbuing it with magic.",
            attack_points=4,
            defense_points=1,
            magic_points=1
        )


class SnowRing(Ring):
    def __init__(self):
        super().__init__(
            id=4,
            name="SnowRing",
            description="A ring with the emblem of the snowflake"
        )

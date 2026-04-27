class Item:
    def __init__(self, name: str = "default item name", description: str = "this is the default item description."):
        self.id = None
        self.name = name
        self.description = description


class WeaponItem(Item):
    def __init__(self, id: int = None, name: str = "default item name",
                 description: str = "this is the default item description.", attack_points: int = 1,
                 defense_points: int = 1, magic_points: int = 1):
        super().__init__(name, description)
        self.id = id
        self.attack_points = attack_points
        self.defense_points = defense_points
        self.magic_points = magic_points


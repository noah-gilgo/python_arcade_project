import character

NON_PLAYER_CHARACTER_SPRITES_FOLDER_PATH = "assets/sprites/non_player_characters/"


class NonPlayerCharacter(character.Character):
    def __init__(self, scale: float, center_x: float, center_y: float, angle: float,
                 sprite_folder_name: str, name: str, max_hp: int, attack: int, defense: int, magic: int,
                 tired: float, mercy: float):
        self._sprite_pack_path = NON_PLAYER_CHARACTER_SPRITES_FOLDER_PATH + sprite_folder_name

        super().__init__(scale=scale, center_x=center_x, center_y=center_y, angle=angle,
                         sprite_folder_name=sprite_folder_name, name=name, max_hp=max_hp, attack=attack,
                         defense=defense)

        self._tired = tired
        self._mercy = mercy

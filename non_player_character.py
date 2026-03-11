import character
import graphics_objects

NON_PLAYER_CHARACTER_SPRITES_FOLDER_PATH = "assets/sprites/non_player_characters/"


class NonPlayerCharacter(character.Character):
    def __init__(self, scale: float, center_x: float, center_y: float, angle: float,
                 sprite_folder_name: str, name: str, max_hp: int, attack: int, defense: int,
                 element_id: int = 0, tired: int = 0, mercy: int = 0):

        self._sprite_pack_path = NON_PLAYER_CHARACTER_SPRITES_FOLDER_PATH + sprite_folder_name

        super().__init__(scale=scale, center_x=center_x, center_y=center_y, angle=angle,
                         sprite_folder_name=sprite_folder_name, name=name, max_hp=max_hp, attack=attack,
                         defense=defense, element_id=element_id)

        self.tired = tired
        self.mercy = mercy

        self._animations_by_state.update({
            "overworld": graphics_objects.SimpleLoopAnimation(
                sprite_pack_path=self._sprite_pack_path + "/overworld",
                frame_duration=0.3,
                loop_animation=True
            ),

            "battle_idle": graphics_objects.SimpleLoopAnimation(
                sprite_pack_path=self._sprite_pack_path + "/battle_idle",
                frame_duration=0.15,
                loop_animation=True
            ),

            "battle_hurt": graphics_objects.SimpleLoopAnimation(
                sprite_pack_path=self._sprite_pack_path + "/battle_hurt",
                frame_duration=0.1,
                loop_animation=False
            ),

            "battle_spared": graphics_objects.SimpleLoopAnimation(
                sprite_pack_path=self._sprite_pack_path + "/battle_spared",
                frame_duration=0.2,
                loop_animation=True
            ),
        })

    def get_hp_percentage_as_string(self):
        """ Returns the whole number HP percentage of the NPC. """
        return str(int(self.hp / self.max_hp)) + "%"

    def get_mercy_percentage_as_string(self):
        """ Returns the whole number HP percentage of the NPC. """
        return str(self.mercy) + "%"

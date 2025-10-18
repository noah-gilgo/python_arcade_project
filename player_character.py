import character
import graphics_objects

PLAYER_CHARACTER_SPRITES_FOLDER_PATH = "assets/sprites/player_characters/"


class PlayerCharacter(character.Character):
    def __init__(self, scale: float, center_x: float, center_y: float, angle: float,
                 sprite_folder_name: str, name: str, max_hp: int, attack: int, defense: int, magic: int):

        self._sprite_pack_path = PLAYER_CHARACTER_SPRITES_FOLDER_PATH + sprite_folder_name

        super().__init__(scale=scale, center_x=center_x, center_y=center_y, angle=angle,
                         sprite_folder_name=sprite_folder_name, name=name, max_hp=max_hp, attack=attack,
                         defense=defense)

        self._magic = magic

        self._animations_by_state.update({
            "battle_idle": graphics_objects.SimpleLoopAnimation(
                sprite_pack_path=self._sprite_pack_path + "/battle_idle",
                frame_duration=0.15,
                loop_animation=True
            ),

            "battle_act": graphics_objects.SimpleLoopAnimation(
                sprite_pack_path=self._sprite_pack_path + "/battle_act",
                frame_duration=0.10,
                loop_animation=False
            ),

            "battle_attack": graphics_objects.SimpleLoopAnimation(
                sprite_pack_path=self._sprite_pack_path + "/battle_attack",
                frame_duration=0.10,
                loop_animation=False
            ),

            "battle_attack_ready": graphics_objects.SimpleLoopAnimation(
                sprite_pack_path=self._sprite_pack_path + "/battle_attack_ready",
                frame_duration=0.15,
                loop_animation=True
            ),

            "battle_defend": graphics_objects.SimpleLoopAnimation(
                sprite_pack_path=self._sprite_pack_path + "/battle_defend",
                frame_duration=0.10,
                loop_animation=False
            ),

            "battle_downed": graphics_objects.SimpleLoopAnimation(
                sprite_pack_path=self._sprite_pack_path + "/battle_downed",
                frame_duration=0.15,
                loop_animation=False
            ),

            "battle_hurt": graphics_objects.SimpleLoopAnimation(
                sprite_pack_path=self._sprite_pack_path + "/battle_hurt",
                frame_duration=0.6,
                loop_animation=False
            ),

            "battle_intro": graphics_objects.SimpleLoopAnimation(
                sprite_pack_path=self._sprite_pack_path + "/battle_intro",
                frame_duration=0.10,
                loop_animation=False
            ),

            "battle_item": graphics_objects.SimpleLoopAnimation(
                sprite_pack_path=self._sprite_pack_path + "/battle_item",
                frame_duration=0.10,
                loop_animation=False
            ),

            "battle_item_ready": graphics_objects.SimpleLoopAnimation(
                sprite_pack_path=self._sprite_pack_path + "/battle_item_ready",
                frame_duration=0.4,
                loop_animation=True
            ),

            "battle_spare": graphics_objects.SimpleLoopAnimation(
                sprite_pack_path=self._sprite_pack_path + "/battle_spare",
                frame_duration=0.10,
                loop_animation=False
            ),

            "battle_victory": graphics_objects.SimpleLoopAnimation(
                sprite_pack_path=self._sprite_pack_path + "/battle_victory",
                frame_duration=0.10,
                loop_animation=False
            )
        })

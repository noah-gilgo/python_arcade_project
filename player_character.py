import arcade
from PIL import Image
from arcade import Sprite, Texture
from arcade.types import Color

import character
import graphics_objects
from graphics_methods import make_texture_solid_color
from spells import Spell

PLAYER_CHARACTER_SPRITES_FOLDER_PATH = "assets/sprites/player_characters/"


class PlayerCharacter(character.Character):
    def __init__(self, scale: float, center_x: float, center_y: float, angle: float,
                 sprite_folder_name: str, name: str, max_hp: int, attack: int, defense: int, magic: int,
                 battle_ui_color: Color, battle_ui_icon_color: Color, fight_box_color: Color = arcade.color.GRAY,
                 fight_crit_box_color: Color = arcade.color.WHITE,
                 element_id: int = 0, knows_magic: bool = True, spells=list[Spell]):

        self._sprite_pack_path = PLAYER_CHARACTER_SPRITES_FOLDER_PATH + sprite_folder_name

        super().__init__(scale=scale, center_x=center_x, center_y=center_y, angle=angle,
                         sprite_folder_name=sprite_folder_name, name=name, max_hp=max_hp, attack=attack,
                         defense=defense, element_id=element_id)

        icon_texture_path = "assets/sprites/player_characters/" + self.sprite_folder_name + "/battle_hud/hud_default_face_icon.png"
        icon_hurt_texture_path = "assets/sprites/player_characters/" + self.sprite_folder_name + "/battle_hud/hud_default_hurt_icon.png"

        image = Image.open(icon_texture_path)
        hurt_image = Image.open(icon_hurt_texture_path)
        self.normal_icon_texture = arcade.Texture(
            arcade.load_image(icon_texture_path).resize(image.size, Image.Resampling.NEAREST))
        self.hurt_icon_texture = arcade.Texture(
            arcade.load_image(icon_hurt_texture_path).resize(hurt_image.size, Image.Resampling.NEAREST))

        self.knows_magic = knows_magic
        self.magic = magic
        self.battle_ui_color = battle_ui_color
        self.battle_ui_icon_color = battle_ui_icon_color if battle_ui_icon_color else battle_ui_color
        self.fight_box_color = fight_box_color
        self.fight_crit_box_color = fight_crit_box_color
        self.is_defending = False

        self._animations_by_state.update({
            "battle_idle": graphics_objects.SimpleLoopAnimation(
                sprite_pack_path=self._sprite_pack_path + "/battle_idle",
                frame_duration=0.15,
                loop_animation=True
            ),

            "battle_act_ready": graphics_objects.SimpleLoopAnimation(
                sprite_pack_path=self._sprite_pack_path + "/battle_act_ready",
                frame_duration=0.10,
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
                frame_duration=0.06,
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
                frame_duration=0.07,
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

            "battle_spare_ready": graphics_objects.SimpleLoopAnimation(
                sprite_pack_path=self._sprite_pack_path + "/battle_spare_ready",
                frame_duration=0.2,
                loop_animation=True
            ),

            "battle_victory": graphics_objects.SimpleLoopAnimation(
                sprite_pack_path=self._sprite_pack_path + "/battle_victory",
                frame_duration=0.10,
                loop_animation=False
            )
        })

        if self.knows_magic:
            self._animations_by_state.update(
                {
                    "battle_magic_ready": graphics_objects.SimpleLoopAnimation(
                        sprite_pack_path=self._sprite_pack_path + "/battle_magic_ready",
                        frame_duration=0.15,
                        loop_animation=True
                    ),

                    "battle_magic": graphics_objects.SimpleLoopAnimation(
                        sprite_pack_path=self._sprite_pack_path + "/battle_magic",
                        frame_duration=0.06,
                        loop_animation=False
                    )
                }
            )

            self.spells = spells

    def is_player_defending(self):
        """
        Returns whether or not the player is defending.
        :return: A bool representing whether or not the player is defending.
        """
        return self.is_defending

    def defend(self):
        """
        Sets the players state to a defending state.
        :return: None
        """
        self.is_defending = True
        if self._animations_by_state["battle_defend"]:
            self.set_animation_state("battle_defend")

    def undefend(self):
        """
        Returns the player from a defending state to an idle state.
        :return: None
        """
        self.is_defending = False
        if self._animations_by_state["battle_defend"]:
            self.set_animation_state("battle_idle")

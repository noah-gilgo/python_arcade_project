import arcade
from PIL import Image
from arcade import Sprite, Texture
from arcade.types import Color

import character
import graphics_objects
from animations.battle_animations import NumberBounceAnimation
from animations.common_animations import ShakeAnimation
from graphics_methods import make_texture_solid_color
from items.armor_items import ArmorItem
from spells import Spell
from sprites_and_effects_collection import SpritesAndEffectsCollection

PLAYER_CHARACTER_SPRITES_FOLDER_PATH = "assets/sprites/player_characters/"


class PlayerCharacter(character.Character):
    def __init__(self, sprites_and_effects_collection: SpritesAndEffectsCollection,
                 scale: float, center_x: float, center_y: float, angle: float,
                 sprite_folder_name: str, name: str, max_hp: int, attack: int, defense: int, magic: int,
                 battle_ui_color: Color, battle_ui_icon_color: Color, fight_box_color: Color = arcade.color.GRAY,
                 fight_crit_box_color: Color = arcade.color.WHITE,
                 element_id: int = 0, knows_magic: bool = True, spells: list[Spell] = []):

        self._sprite_pack_path = PLAYER_CHARACTER_SPRITES_FOLDER_PATH + sprite_folder_name

        super().__init__(sprites_and_effects_collection=sprites_and_effects_collection, scale=scale, center_x=center_x,
                         center_y=center_y, angle=angle, sprite_folder_name=sprite_folder_name, name=name,
                         max_hp=max_hp, attack=attack, defense=defense, element_id=element_id)

        icon_texture_path = "assets/sprites/player_characters/" + self.sprite_folder_name + "/battle_hud/hud_default_face_icon.png"
        icon_hurt_texture_path = "assets/sprites/player_characters/" + self.sprite_folder_name + "/battle_hud/hud_default_hurt_icon.png"

        self.player_hurt_sound = arcade.load_sound("assets/audio/battle/player_character/common/snd_hurt1.wav", False)

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

        # The equipment slots for the player character.
        self.weapon_slot = None
        self.armor_slot_1 = None
        self.armor_slot_2 = None


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
                frame_duration=0.1,
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

    def equip_armor_to_slot_1(self, armor: ArmorItem | None):
        """
        Equips the supplied armor to armor slot 1.
        :param armor: The armor being equipped.
        :return: The armor that was previously in the slot, if there was armor in said slot.
        """
        armor_previously_in_slot_1 = None
        if self.armor_slot_1:
            armor_previously_in_slot_1 = self.armor_slot_1
        self.armor_slot_1 = armor

        # If there was already armor in that slot, return it.
        return armor_previously_in_slot_1

    def equip_armor_to_slot_2(self, armor: ArmorItem | None):
        """
        Equips the supplied armor to armor slot 2.
        :param armor: The armor being equipped.
        :return: The armor that was previously in the slot, if there was armor in said slot.
        """
        armor_previously_in_slot_2 = None
        if self.armor_slot_2:
            armor_previously_in_slot_2 = self.armor_slot_2
        self.armor_slot_2 = armor

        # If there was already armor in that slot, return it.
        return armor_previously_in_slot_2


    def calculate_received_damage(self, base_damage: float, element_id: int = 0):
        """
        Takes the base damage of the attacker's attack and modifies it based on the characteristics of the receiver
        (ex. defense, element_id, etc.)
        Since player characters/non player characters are a bit different on the back end, this is just a stub.
        :param base_damage: The base damage of the attacker's attack. This function modifies this value
        :param element_id: The element ID of the attack.
        :return:
        """
        """
        if self.element_id:
            for element in default_data.ELEMENTAL_PAIRS:
                if element.element_id == actor.element_id:
                    if target.element_id in element.resistant_to:
                        damage_dealt *= 0.66
                    if target.element_id in element.weak_to:
                        damage_dealt *= 1.5
        """

    def damage(self, damage_dealt: float = 0, element_id: int = 0, play_hurt_sound: bool = True):
        """
        Damages the player character, removing some of their HP.
        :param damage_dealt: The base amount of damage dealt
        :param element_id: The element id of the attack
        :param play_hurt_sound: Controls whether to play the hurt sound
        :return: None
        """
        damage_dealt = int(damage_dealt)
        damage_dealt_text = str(damage_dealt)
        damage_dealt_color = arcade.color.WHITE
        previous_hp = int(self.hp)

        if damage_dealt <= 0:
            damage_dealt_text = "MISS"

        else:
            self.hp -= damage_dealt
            if play_hurt_sound:
                self.player_hurt_sound.play()

            # If the attack reduces the enemy HP to 0
            if self.hp <= 0:
                if previous_hp > 0:
                    damage_dealt_text = "DOWN"
                    damage_dealt_color = arcade.color.RED
                    self.set_animation_state("battle_downed")
                    self.hp = min(-self.max_hp / 2, -80)
            else:
                self.set_animation_to_not_idle(1.2, "battle_hurt")

                shake_animation = ShakeAnimation(
                    sprite=self
                )
                self.sprites_and_effects_collection.effects.append(shake_animation)

            damage_dealt_animation = NumberBounceAnimation(
                text=damage_dealt_text,
                color=damage_dealt_color,
                target=self
            )

            self.sprites_and_effects_collection.effects_sprites.append(damage_dealt_animation.sprite)
            self.sprites_and_effects_collection.effects.append(damage_dealt_animation)

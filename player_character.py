import arcade
from PIL import Image
from arcade import Sprite, Texture
from arcade.types import Color

import character
import default_data
import graphics_objects
from animations.battle_animations import NumberBounceAnimation
from animations.common_animations import ShakeAnimation
from graphics_methods import make_texture_solid_color
from items.armor_items import ArmorItem
from items.weapon_items import WeaponItem
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
        self.player_attack_sound = arcade.load_sound("assets/audio/battle/player_character/common/snd_laz_c.wav", False)

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

        # Set the animation state to battle_idle, if it exists
        if "battle_idle" in self._animations_by_state:
            self.set_animation_state("battle_idle")

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

    def equip_weapon(self, weapon: WeaponItem | None):
        """
        Equips the supplied weapon to the weapon slot.
        :param weapon: The weapon being equipped.
        :return: The weapon that was previously in the slot, if there was weapon in said slot.
        """
        weapon_previously_in_slot = None
        if self.weapon_slot:
            weapon_previously_in_slot = self.weapon_slot
        self.weapon_slot = weapon

        # If there was already armor in that slot, return it.
        return weapon_previously_in_slot

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
        damage_dealt = base_damage

        # Add the base player defense with their equipment defense to get their total defense
        player_defense = self.defense

        if self.weapon_slot:
            player_defense += self.weapon_slot.defense_points
        if self.armor_slot_1:
            player_defense += self.armor_slot_1.defense_points
        if self.armor_slot_2:
            player_defense += self.armor_slot_2.defense_points

        # Subtract a certain amount of damage from the base damage based on the defense stat.
        if base_damage >= self.max_hp / 5:
            damage_dealt -= player_defense * 3
        elif self.max_hp / 5 > base_damage > self.max_hp / 8:
            damage_dealt -= player_defense * 2
        else:
            damage_dealt -= player_defense

        # If the player character is defending, multiply their damage taken by 2/3
        if self.is_defending:
            damage_dealt = int((2 * damage_dealt)/3)

        # Apply elemental damage reductions
        for armor in self.armor_slot_1, self.armor_slot_2:
            if armor:
                if element_id and armor.element_id:
                    for element in default_data.ELEMENTAL_PAIRS:
                        if element.element_id == armor.element_id:
                            if element_id in element.resistant_to:
                                damage_dealt *= 0.66

                            #if element_id in element.weak_to:
                            #    damage_dealt *= 2.5

        # If, somehow, the enemy's attack damage gets reduced below 1, set it to 1.
        if damage_dealt < 1:
            damage_dealt = 1

        # Convert the damage dealt to an int before returning it.
        return int(damage_dealt)


    def attack_enemy(self, enemy, attack_damage_multiplier: float = 1.0):
        """
        Makes the player character attack the supplied non-player character.
        :param enemy: The enemy to be attacked.
        :param attack_damage_multiplier: The attack multiplier returned by the fight bar in the FIGHT act.
        :return: None
        """

        # Play the attack animation/sound
        self.set_animation_to_not_idle(animation_state="battle_attack", duration=1.0)

        attack = self.attack + self.weapon_slot.attack_points + self.armor_slot_1.attack_points + self.armor_slot_2.attack_points

        damage_dealt = int(attack * 20 * attack_damage_multiplier) # This is not exactly how it's calculated in the
        if self.weapon_slot.element_id:                            # original game, but it's close
            for element in default_data.ELEMENTAL_PAIRS:
                if element.element_id == self.weapon_slot.element_id:
                    if enemy.element_id in element.resistant_to:
                        damage_dealt *= 0.66
                    if enemy.element_id in element.weak_to:
                        damage_dealt *= 1.5

        return damage_dealt


    def receive_damage(self, damage_dealt: float = 0, element_id: int = 0, play_hurt_sound: bool = True):
        """
        Damages the player character, removing some of their HP.
        :param damage_dealt: The base amount of damage dealt
        :param element_id: The element id of the attack
        :param play_hurt_sound: Controls whether to play the hurt sound
        :return: None
        """
        damage_dealt = self.calculate_received_damage(damage_dealt, element_id)
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
                if not self.is_defending:
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

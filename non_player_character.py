import arcade
from arcade.types import Color

import character
import default_data
import graphics_objects
from animations.battle_animations import EnemyFleeingAnimation, StrikeEnemyAnimation, NumberBounceAnimation
from animations.common_animations import ShakeAnimation
from bullet_patterns import RainingDiamondBulletPattern
from enemy_attacks import EnemyIndividualAttack, DefaultAttack
from sprites_and_effects_collection import SpritesAndEffectsCollection

NON_PLAYER_CHARACTER_SPRITES_FOLDER_PATH = "assets/sprites/non_player_characters/"


class NonPlayerCharacter(character.Character):
    def __init__(self, sprites_and_effects_collection: SpritesAndEffectsCollection, scale: float, center_x: float,
                 center_y: float, angle: float, sprite_folder_name: str, name: str, hp: int, max_hp: int, attack: int,
                 defense: int, element_id: int = 0, tired: int = 0, mercy: int = 0,
                 attacks: list[EnemyIndividualAttack] = [], enemies_list: list = []):

        self._sprite_pack_path = NON_PLAYER_CHARACTER_SPRITES_FOLDER_PATH + sprite_folder_name

        super().__init__(sprites_and_effects_collection=sprites_and_effects_collection, scale=scale, center_x=center_x,
                         center_y=center_y, angle=angle, sprite_folder_name=sprite_folder_name, name=name,
                         max_hp=max_hp, attack=attack, defense=defense, element_id=element_id)

        self.enemies_list = enemies_list

        self.hp = hp
        self.tired = tired
        self.mercy = mercy
        self.attacks = attacks

        self.enemy_hit_sound = arcade.load_sound("assets/audio/battle/non_player_character/common/snd_damage.wav",
                                                 False)
        self.enemy_flee_sound = arcade.load_sound("assets/audio/battle/non_player_character/common/snd_defeatrun.wav",
                                                  False)

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

        # Meant to contain all of the random dialogue that non player characters say right before they do battle
        self.witty_banter = []

        # Set the animation state to battle_idle, if it exists
        if "battle_idle" in self._animations_by_state:
            self.set_animation_state("battle_idle")

    def get_hp_percentage_as_string(self):
        """ Returns the whole number HP percentage of the NPC. """
        return str(int((self.hp / self.max_hp) * 100)) + "%"

    def get_mercy_percentage_as_string(self):
        """ Returns the whole number HP percentage of the NPC. """
        return str(self.mercy) + "%"

    def execute_attack(self, frequency: float = 1.0):
        """
        Executes an attack depending on the number of other enemies in the battle.
        :param frequency: Can modify the frequency of the attack's bullet spawn rate.
        :return: None
        """
        pass

    def receive_damage(self, damage_dealt: float, attacker):
        damage_dealt_text = str(damage_dealt)
        damage_dealt_color = Color.from_iterable([
            int((attacker.battle_ui_color.r + 255) / 2),
            int((attacker.battle_ui_color.g + 255) / 2),
            int((attacker.battle_ui_color.b + 255) / 2),
            int(attacker.battle_ui_color.a)
        ])

        if self.element_id and attacker.weapon_slot.element_id:
            for element in default_data.ELEMENTAL_PAIRS:
                if element.element_id == self.element_id:
                    if attacker.weapon_slot.element_id in element.resistant_to:
                        damage_dealt *= 0.66
                    if attacker.weapon_slot.element_id in element.weak_to:
                        damage_dealt *= 1.5

        if damage_dealt <= 0:
            damage_dealt_text = "MISS"
            damage_dealt_color = arcade.color.WHITE

        else:
            self.enemy_hit_sound.play()

            # If the attack reduces the enemy HP to 0
            if self.hp <= 0:
                damage_dealt_text = "LOST"
                damage_dealt_color = arcade.color.RED
                self.enemy_flee_sound.play()
                enemy_fleeing_animation = EnemyFleeingAnimation(actor=self)
                self.sprites_and_effects_collection.effects.append(enemy_fleeing_animation)
                for sprite in enemy_fleeing_animation.get_sprites():
                    self.sprites_and_effects_collection.effects_sprites.append(sprite)
                self.enemies_list.remove(self)
            else:
                shake_animation = ShakeAnimation(
                    sprite=self
                )
                self.sprites_and_effects_collection.effects.append(shake_animation)
                strike_enemy_animation = StrikeEnemyAnimation(
                    actor=attacker,
                    target=self
                )
                self.sprites_and_effects_collection.effects.append(strike_enemy_animation)
                self.sprites_and_effects_collection.effects_sprites.append(strike_enemy_animation.sprite)
                self.set_animation_to_not_idle(1.5, "battle_hurt")

        self.hp -= damage_dealt

        damage_dealt_animation = NumberBounceAnimation(
            text=damage_dealt_text,
            color=damage_dealt_color,
            target=self
        )

        self.sprites_and_effects_collection.effects_sprites.append(damage_dealt_animation.sprite)
        self.sprites_and_effects_collection.effects.append(damage_dealt_animation)


class Rudinn(NonPlayerCharacter):
    def __init__(self, sprites_and_effects_collection: SpritesAndEffectsCollection, enemies_list: list,
                 center_x: float, center_y: float, scale: float = 4.0, angle: float = 0):
        super().__init__(
            sprites_and_effects_collection=sprites_and_effects_collection,
            center_x=center_x,
            center_y=center_y,
            scale=scale,
            angle=angle,
            sprite_folder_name="rudinn",
            name="Rudinn 1",
            hp=90,
            max_hp=90,
            attack=10,
            defense=2,
            element_id=0,
            attacks=[DefaultAttack],
            enemies_list=enemies_list
        )

    def execute_attack(self, frequency: float = 1.0):
        """
        Executes an attack depending on the number of other enemies in the battle.
        :param frequency: Can modify the frequency of the attack's bullet spawn rate.
        :return: None
        """


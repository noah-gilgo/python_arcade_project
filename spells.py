import random

import arcade.color
import pyglet.clock
from arcade import Sprite
from arcade.types import Color

import character
import default_data
from animations.battle_animations import NumberBounceAnimation, EnemyFleeingAnimation, HealAnimation, \
    EnemySparedAnimation
from animations.common_animations import ShakeAnimation, FadeInFadeOutColorAnimation
from graphics_objects import MultiSpriteAnimation
from animations.spell_animations import IceShockAnimation, FreezeAnimation, FireShockAnimation, BurnAnimation, \
    RudeBusterAnimation, SleepMistAnimation
from sprites_and_effects_collection import SpritesAndEffectsCollection


class Spell:
    """ Parent class for spells """
    def __init__(self, name: str = "Default Spell", description: str = "", tp_cost: int = 0, element_id: int = 0,
                 base_health_change: int = 0, is_friendly_spell: bool = False, is_healing_spell: bool = False,
                 is_pacifying_spell: bool = False, is_aoe_spell: bool = False, animation: MultiSpriteAnimation = None,
                 magic_color: Color = arcade.color.WHITE, ready_animation_state: str = "battle_magic_ready",
                 cast_animation_state: str = "battle_magic", time_before_animation_begins: float = None,
                 time_before_target_affected_by_spell: float = None, time_before_battle_idle: float = None,
                 time_before_player_can_advance_past_spell: float = 1.6):
        self.name = name  # Name of the spell
        self.description = description  # Description of the spell
        self.tp_cost = tp_cost  # TP cost of the spell
        self.element_id = element_id  # elemental pair associated with the spell, if any
        self.base_health_change = base_health_change  # amount health changed by spell
        self.is_friendly_spell = is_friendly_spell  # True if the intended target is player characters
        self.is_healing_spell = is_healing_spell  # True if the spell is healing
        self.is_pacifying_spell = is_pacifying_spell  # True if the spell is meant to pacify the target
        self.is_aoe_spell = is_aoe_spell  # True if the spell affects all targets on the targeted side
        self.animation = animation  # The animation that plays when casting the spell.
        self.magic_color = magic_color  # The color that the enemy flashes when hit with the spell.

        self.ready_animation_state = ready_animation_state  # The animation state given to the character when they've been told to cast the spell.
        self.cast_animation_state = cast_animation_state  # The animation state given to the character when they cast the spell.
        self.time_before_animation_begins = time_before_animation_begins  # The amount of time between when the spell is cast and when the spell animation begins.
        self.time_before_target_affected_by_spell = time_before_target_affected_by_spell # The amount of time between when the spell is cast and when the enemy is affected by it.
        self.time_before_battle_idle = time_before_battle_idle  # If provided, the amount of time that will pass before the casters animation state is returned to battle_idle.
        self.time_before_player_can_advance_past_spell = time_before_player_can_advance_past_spell # If provided, the amount of time player input will be delayed while the spell is being cast

        # Passed in during the cast spell call.
        self.caster = None
        self.targets = None
        self.controller = None
        self.sprites_and_effects_collection = None

        self.spare_sound = arcade.load_sound("assets/audio/battle/player_character/common/snd_spare.wav", False)

    def cast_spell(self, caster, targets, controller):
        """
        Casts the spell.
        :param caster: The PlayerCharacter casting the spell.
        :param targets: The targeted characters that the spell is being cast upon.
        :param controller: The battle controller.
        :return: None
        """
        self.caster = caster
        self.targets = targets
        self.controller = controller
        self.sprites_and_effects_collection = controller.sprites_and_effects_collection

        if self.cast_animation_state in caster.animations_by_state:
            caster.set_animation_state(self.cast_animation_state)
        else:
            caster.set_animation_state("battle_magic")

        if self.time_before_animation_begins is not None:
            pyglet.clock.schedule_once(lambda dt: self.animate_spell(caster, targets, controller.sprites_and_effects_collection), self.time_before_animation_begins)
        if self.time_before_target_affected_by_spell is not None:
            pyglet.clock.schedule_once(lambda dt: self.affect_targets_with_spell(), self.time_before_target_affected_by_spell)
        if self.time_before_battle_idle is not None:
            pyglet.clock.schedule_once(lambda dt: caster.set_animation_state("battle_idle"), self.time_before_battle_idle)

        # Tell the battle controller to postpone the player advancing their queued actions until the spell is complete.
        if self.time_before_player_can_advance_past_spell is not None:
            controller.delay_player_from_advancing_to_next_state(self.time_before_player_can_advance_past_spell)

    def spell_damage_function(self, caster, target) -> float:
        """
        Calculates the damage dealt by the spell depending on caster stats.
        :return:
        """
        return self.base_health_change * caster.magic

    def spell_healing_function(self, caster) -> float:
        """
        Calculates the damage healed by the spell depending on caster stats.
        :return:
        """
        return self.base_health_change * caster.magic

    def affect_targets_with_spell(self):
        """ Perform the calculations required after a spell is cast on a character. """
        # TODO: Maybe add percentages to elemental pairs to control how much damage is resisted/amplified?
        # TODO: Move all of the spell functions to the battle controller instead of using all these parameters, maybe
        if len(self.targets) == 0:
            return

        enemies_to_be_removed_by_pacify = []

        for target in self.targets:
            schedule_battle_idle = True
            if target not in self.targets:
                target = target[0]
            if self.is_pacifying_spell:

                if target.tired >= 100:
                    # Animate the enemy being spared.
                    target.set_animation_state("battle_spared")

                    spare_animation = EnemySparedAnimation(target=target)
                    spare_animation_sprites = spare_animation.get_sprites()

                    self.sprites_and_effects_collection.effects.append(spare_animation)
                    for spare_animation_sprite in spare_animation_sprites:
                        self.sprites_and_effects_collection.effects_sprites.append(spare_animation_sprite)

                    # Play the spare sound.
                    self.spare_sound.play()

                    # Remove the enemy from the battle.
                    enemies_to_be_removed_by_pacify.append(target)
            elif self.is_friendly_spell:
                target.modify_hp(self.spell_healing_function(self.caster))
            else:
                damage_dealt = self.spell_damage_function(self.caster, target)
                if self.element_id:
                    for element in default_data.ELEMENTAL_PAIRS:
                        if element.element_id == self.element_id:
                            if target.element_id in element.resistant_to:
                                damage_dealt *= 0.66
                            if target.element_id in element.weak_to:
                                damage_dealt *= 1.5

                target.hp -= int(damage_dealt)

                damage_dealt_text = str(damage_dealt)

                damage_dealt_color = Color.from_iterable([
                    int((self.caster.battle_ui_color.r + 255) / 2),
                    int((self.caster.battle_ui_color.g + 255) / 2),
                    int((self.caster.battle_ui_color.b + 255) / 2),
                    int(self.caster.battle_ui_color.a)
                ])

                # If the attack reduces the enemy HP to 0
                if target.hp <= 0:
                    self.controller.enemies_defeated_violently += 1
                    schedule_battle_idle = False
                    if self.element_id == 8: # Fire/Ice
                        if self.name.lower() == "iceshock":
                            damage_dealt_text = "FROZEN"
                            damage_dealt_color = arcade.color.WHITE
                            freeze_sound = arcade.load_sound("assets/audio/battle/player_character/spells/snd_petrify.wav", False)
                            freeze_sound.play()
                            target.non_idle_timer = 0
                            target.set_animation_state("battle_hurt")
                            freeze_animation = FreezeAnimation(target=target)
                            self.controller.sprites_and_effects_collection.effects.append(freeze_animation)
                            for sprite in freeze_animation.get_sprites():
                                self.controller.sprites_and_effects_collection.effects_sprites.append(sprite)
                            self.controller.enemies.remove(target)
                        elif self.name.lower() == "fireshock":
                            damage_dealt_text = "CHARRED"
                            damage_dealt_color = arcade.color.WHITE
                            target.non_idle_timer = 0
                            self.controller.enemies.remove(target)
                    else:
                        damage_dealt_text = "LOST"
                        damage_dealt_color = arcade.color.WHITE
                        self.controller.enemy_flee_sound.play()
                        enemy_fleeing_animation = EnemyFleeingAnimation(actor=target)
                        self.controller.sprites_and_effects_collection.effects.append(enemy_fleeing_animation)
                        for sprite in enemy_fleeing_animation.get_sprites():
                            self.controller.sprites_and_effects_collection.effects_sprites.append(sprite)
                        if target in self.controller.enemies:
                            self.controller.enemies.remove(target)

                damage_dealt_animation = NumberBounceAnimation(
                    text=damage_dealt_text,
                    color=damage_dealt_color,
                    target=target,
                    sprites_and_effects_collection=self.controller.sprites_and_effects_collection
                )

                shake_animation = ShakeAnimation(
                    sprite=target
                )

                color_filter_animation = FadeInFadeOutColorAnimation(
                    sprite=target,
                    color=self.magic_color
                )

                target.set_animation_state("battle_hurt")
                self.controller.sprites_and_effects_collection.effects_sprites_4.append(damage_dealt_animation.sprite)
                self.controller.sprites_and_effects_collection.effects.append(damage_dealt_animation)
                self.controller.sprites_and_effects_collection.effects.append(shake_animation)
                self.controller.sprites_and_effects_collection.effects.append(color_filter_animation)
                self.controller.sprites_and_effects_collection.effects_sprites.append(color_filter_animation.filter_sprite)
                if schedule_battle_idle:
                    pyglet.clock.schedule_once(lambda dt: target.set_animation_state("battle_idle"), 1.0)

            for enemy in enemies_to_be_removed_by_pacify:
                if enemy in self.controller.enemies:
                    self.controller.enemies.remove(enemy)

    def animate_spell(self, caster, targets: list[character.Character], sprites_and_effects_collection: SpritesAndEffectsCollection):
        """ Animate the spell being cast. """
        if self.animation:
            for target in targets:
                new_animation = self.animation.__class__(caster, target, sprites_and_effects_collection)
                sprites_and_effects_collection.effects.append(new_animation)
                new_animation.center_x = target.center_x
                new_animation.center_y = target.center_y
                if hasattr(new_animation, "sprites"):
                    for animated_sprite in new_animation.sprites:
                        if isinstance(animated_sprite, Sprite):
                            sprites_and_effects_collection.effects_sprites_3.append(animated_sprite)
                        else:
                            sprites_and_effects_collection.effects_sprites_3.append(animated_sprite.sprite)
                elif hasattr(new_animation, "get_sprites"):
                    for animated_sprite in new_animation.get_sprites():
                        if isinstance(animated_sprite, Sprite):
                            sprites_and_effects_collection.effects_sprites_3.append(animated_sprite)
                        else:
                            sprites_and_effects_collection.effects_sprites_3.append(animated_sprite.sprite)


class IceShock(Spell):
    def __init__(self):
        super().__init__(
            name="IceShock",
            description="Damage w/ ICE",
            tp_cost=16,
            element_id=8,
            base_health_change=100,
            is_friendly_spell=False,
            is_healing_spell=False,
            is_pacifying_spell=False,
            is_aoe_spell=False,
            animation=IceShockAnimation(),
            time_before_battle_idle=1.0,
            time_before_animation_begins=0.5,
            time_before_target_affected_by_spell=0.9,
            time_before_player_can_advance_past_spell=2.5
        )

    def spell_damage_function(self, caster, target) -> float:
        """ Calculates the damage dealt by the spell depending on caster stats.
        :return: None
        """

        return (max(caster.magic - 10, 1) * 30) + 90 + random.randint(1, 10)


class FireShock(Spell):
    def __init__(self):
        super().__init__(
            name="FireShock",
            description="Damage w/ FIRE",
            tp_cost=16,
            element_id=8,
            magic_color=arcade.color.ORANGE,
            base_health_change=100,
            is_friendly_spell=False,
            is_healing_spell=False,
            is_pacifying_spell=False,
            is_aoe_spell=False,
            animation=FireShockAnimation(),
            time_before_battle_idle=1.8,
            ready_animation_state="battle_magic_ready_fireshock",
            cast_animation_state="battle_magic_fireshock",
            time_before_animation_begins=0.5,
            time_before_target_affected_by_spell=0.9,
            time_before_player_can_advance_past_spell=2.5
        )

        self.burn_sound = arcade.load_sound("assets/audio/battle/player_character/spells/snd_petrify.wav",
                                            False)

    def spell_damage_function(self, caster, target) -> float:
        """ Calculates the damage dealt by the spell depending on caster stats.
        :return: None
        """

        return (max(caster.magic - 10, 1) * 30) + 90 + random.randint(1, 10)

    def affect_targets_with_spell(self):
        super().affect_targets_with_spell()
        # Spawn burn animation
        for target in self.targets:
            if target.hp < 0:
                self.burn_sound.play(speed=0.5)  # the speed modifier doesn't do anything for some reason
                burn_animation = BurnAnimation(target)
                for sprite in burn_animation.get_sprites():
                    if sprite not in self.sprites_and_effects_collection.effects_sprites:
                        self.sprites_and_effects_collection.effects_sprites_2.append(sprite)
                if burn_animation not in self.sprites_and_effects_collection.effects:
                    self.sprites_and_effects_collection.effects.append(burn_animation)


class HealPrayer(Spell):
    def __init__(self):
        super().__init__(
            name="Heal Prayer",
            description="Heal Ally",
            tp_cost=32,
            base_health_change=0,
            is_friendly_spell=True,
            is_healing_spell=True,
            is_pacifying_spell=False,
            is_aoe_spell=False,
            animation=HealAnimation(target=None),
            time_before_battle_idle=0.9,
            time_before_animation_begins=0.5,
            time_before_target_affected_by_spell=0.5,
            time_before_player_can_advance_past_spell=1.5
        )

    def spell_healing_function(self, caster) -> float:
        """
        Calculates the damage healed by the spell depending on caster stats.
        :return:
        """
        return 5 * caster.get_total_magic()


class RudeBuster(Spell):
    def __init__(self):
        super().__init__(
            name="Rude Buster",
            description="Rude Damage",
            tp_cost=50,
            element_id=5,
            base_health_change=0,
            is_friendly_spell=False,
            is_healing_spell=False,
            is_pacifying_spell=False,
            is_aoe_spell=False,
            animation=RudeBusterAnimation(caster=None, target=None),
            time_before_battle_idle=1.4,
            time_before_animation_begins=0.8,
            time_before_target_affected_by_spell=1.3,
            time_before_player_can_advance_past_spell=2.4
        )

        # This is the amount of additional damage that will be dealt by Rude Buster depending on the frame
        self.damage_addition_amount_list = [30, 28, 20, 13, 11, 10, 7]

        # This is the number of frames between the user pressing the Confirm key and Rude Buster impacting the target.
        self.frames_between_confirm_and_impact = 999

    def spell_damage_function(self, caster, target):
        if self.frames_between_confirm_and_impact < len(self.damage_addition_amount_list):
            confirm_damage = self.damage_addition_amount_list[self.frames_between_confirm_and_impact]
        else:
            confirm_damage = 0
        return (caster.get_total_attack() * 11) + (caster.get_total_magic() * 5) - (target.defense * 3) + confirm_damage

    def cast_spell(self, caster, targets, controller):
        """
        Casts the spell.
        :param caster: The PlayerCharacter casting the spell.
        :param targets: The targeted characters that the spell is being cast upon.
        :param controller: The battle controller.
        :return: None
        """
        self.caster = caster
        self.targets = targets
        self.controller = controller
        self.sprites_and_effects_collection = controller.sprites_and_effects_collection

        if self.cast_animation_state in caster.animations_by_state:
            caster.set_animation_state(self.cast_animation_state)
        else:
            caster.set_animation_state("battle_magic")

        if self.time_before_animation_begins is not None:
            pyglet.clock.schedule_once(lambda dt: self.animate_spell(caster, targets, controller.sprites_and_effects_collection), self.time_before_animation_begins)
        if self.time_before_battle_idle is not None:
            pyglet.clock.schedule_once(lambda dt: caster.set_animation_state("battle_idle"), self.time_before_battle_idle)

        # Tell the battle controller to postpone the player advancing their queued actions until the spell is complete.
        if self.time_before_player_can_advance_past_spell is not None:
            controller.delay_player_from_advancing_to_next_state(self.time_before_player_can_advance_past_spell)

    def animate_spell(self, caster, targets: list[character.Character], sprites_and_effects_collection: SpritesAndEffectsCollection):
        """ Animate the spell being cast. """
        if self.animation:
            target = targets[0]
            new_animation = self.animation.__class__(caster, target, sprites_and_effects_collection)
            sprites_and_effects_collection.effects.append(new_animation)
            new_animation.center_x = target.center_x
            new_animation.center_y = target.center_y
            if hasattr(new_animation, "sprites"):
                for animated_sprite in new_animation.sprites:
                    if isinstance(animated_sprite, Sprite):
                        sprites_and_effects_collection.effects_sprites_3.append(animated_sprite)
                    else:
                        sprites_and_effects_collection.effects_sprites_3.append(animated_sprite.sprite)
            elif hasattr(new_animation, "get_sprites"):
                for animated_sprite in new_animation.get_sprites():
                    if isinstance(animated_sprite, Sprite):
                        sprites_and_effects_collection.effects_sprites_3.append(animated_sprite)
                    else:
                        sprites_and_effects_collection.effects_sprites_3.append(animated_sprite.sprite)

            new_animation.parent_spell = self


class SleepMist(Spell):
    def __init__(self):
        super().__init__(
            name="Sleep Mist",
            description="Spare TIRED foes",
            tp_cost=32,
            base_health_change=0,
            is_friendly_spell=False,
            is_healing_spell=False,
            is_pacifying_spell=True,
            is_aoe_spell=True,
            animation=SleepMistAnimation(),
            time_before_battle_idle=2.0,
            ready_animation_state="battle_magic_ready_sleepmist",
            cast_animation_state="battle_magic_sleepmist",
            time_before_animation_begins=0.5,
            time_before_target_affected_by_spell=1.3,
            time_before_player_can_advance_past_spell=2.5
        )

        self.sleepmist_sound = arcade.load_sound("assets/audio/magic/snd_ghostappear.ogg")

    def cast_spell(self, caster, targets, controller):
        super().cast_spell(caster, targets, controller)
        if caster.name == "Ralsei":
            pyglet.clock.schedule_once(lambda dt: caster.set_scale(4.0), self.time_before_battle_idle)
        pyglet.clock.schedule_once(lambda dt: self.sleepmist_sound.play(), self.time_before_animation_begins)
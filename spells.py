from copy import copy, deepcopy

import arcade.color
import pyglet.clock
from arcade.types import Color

import character
import default_data
import non_player_character
from animations.battle_animations import DamageDealtAnimation
from animations.common_animations import ShakeAnimation, FadeInFadeOutColorAnimation
from character import Character
from elemental_pairs import ElementalPair
from graphics_objects import MultiSpriteAnimation


class Spell:
    """ Parent class for spells """
    def __init__(self, name: str = "Default Spell", description: str = "", tp_cost: int = 0, element_id: int = 0,
                 base_health_change: int = 0, is_friendly_spell: bool = False, is_healing_spell: bool = False,
                 is_pacifying_spell: bool = False, is_aoe_spell: bool = False, animation: MultiSpriteAnimation = None,
                 magic_color: Color = arcade.color.WHITE):
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

    def affect_targets_with_spell(self, caster, targets, controller):
        """ Perform the calculations required after a spell is cast on a character. """
        # TODO: Maybe add percentages to elemental pairs to control how much damage is resisted/amplified?
        # TODO: Move all of the spell functions to the battle controller instead of using all these parameters, maybe
        for target in targets:
            damage_dealt = 0
            if self.is_friendly_spell:
                new_hp = target.hp + self.base_health_change
                if new_hp < target.max_hp:
                    target.hp = new_hp
                else:
                    target.hp = target.max_hp
            else:
                damage_dealt = self.base_health_change
                if self.element_id:
                    for element in default_data.ELEMENTAL_PAIRS:
                        if element.element_id == self.element_id:
                            if target.element_id in element.resistant_to:
                                damage_dealt *= 0.66
                            if target.element_id in element.weak_to:
                                damage_dealt *= 1.5

                target.hp -= int(damage_dealt)

            damage_dealt_color = Color.from_iterable([
                int((caster.battle_ui_color.r + 255) / 2),
                int((caster.battle_ui_color.g + 255) / 2),
                int((caster.battle_ui_color.b + 255) / 2),
                int(caster.battle_ui_color.a)
            ])

            damage_dealt_animation = DamageDealtAnimation(
                damage_amount=damage_dealt,
                color=damage_dealt_color,
                target=target
            )

            shake_animation = ShakeAnimation(
                sprite=target
            )

            color_filter_animation = FadeInFadeOutColorAnimation(
                sprite=target,
                color=self.magic_color
            )

            target.set_animation_state("battle_hurt")
            controller.effects_sprite_list.append(damage_dealt_animation.sprite)
            controller.effects_list.append(damage_dealt_animation)
            controller.effects_list.append(shake_animation)
            controller.effects_list.append(color_filter_animation)
            controller.effects_sprite_list.append(color_filter_animation.filter_sprite)
            pyglet.clock.schedule_once(lambda dt: target.set_animation_state("battle_idle"), 1.0)

    def animate_spell(self, targets: list[character.Character], spell_sprite_list, animation_list):
        """ Animate the spell being cast. """
        if self.animation:
            for target in targets:
                new_animation = self.animation.__class__(target.center_x, target.center_y)
                animation_list.append(new_animation)
                new_animation.center_x = target.center_x
                new_animation.center_y = target.center_y
                for animated_sprite in new_animation.sprites:
                    spell_sprite_list.append(animated_sprite.sprite)


def generate_basic_spells():
    """ Generates some basic spells from Deltarune. """
    pass

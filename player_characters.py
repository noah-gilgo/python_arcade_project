from arcade.types import Color

import graphics_objects
from acts import RalseiRudinnAction1, NoelleRudinnAction1, SusieRudinnAction1
from player_character import PlayerCharacter
from spells import IceShock, Spell, FireShock, HealPrayer, RudeBuster, SleepMist


class Kris(PlayerCharacter):
    def __init__(self):
        super().__init__(
            sprite_folder_name="kris",
            name="Kris",
            max_hp=90,
            attack=10,
            defense=2,
            magic=0,
            battle_ui_color=Color(0, 255, 255, 255),
            battle_ui_icon_color=Color(0, 162, 232, 255),
            fight_box_color=Color(0, 0, 255, 255),
            fight_crit_box_color=Color(0, 162, 232, 255),
            knows_magic=False
        )


class Susie(PlayerCharacter):
    """ The violet tormentor. """
    def __init__(self):
        super().__init__(
            sprite_folder_name="susie",
            name="Susie",
            max_hp=110,
            attack=14,
            defense=2,
            magic=1,
            battle_ui_color=Color(255, 0, 255, 255),
            battle_ui_icon_color=Color(234, 121, 200, 255),
            fight_box_color=Color(128, 0, 128, 255),
            fight_crit_box_color=Color(234, 121, 200, 255),
            spells=[RudeBuster()]
        )

        self.magic_user_acts = [SusieRudinnAction1(self)]


class Ralsei(PlayerCharacter):
    def __init__(self):
        super().__init__(
            sprite_folder_name="ralsei",
            name="Ralsei",
            max_hp=70,
            attack=8,
            defense=2,
            magic=7,
            battle_ui_color=Color(0, 255, 0, 255),
            battle_ui_icon_color=Color(181, 230, 29, 255),
            fight_box_color=Color(0, 255, 0, 255),
            fight_crit_box_color=Color(181, 230, 29, 255),
            spells=[HealPrayer(), SleepMist(), FireShock()]
        )

        self.magic_user_acts = [RalseiRudinnAction1(self)]

        self.animations_by_state.update(
            {
                "battle_magic_ready_fireshock": graphics_objects.SimpleLoopAnimation(
                    sprite_pack_path=self._sprite_pack_path + "/battle_magic_ready_fireshock",
                    frame_duration=0.2,
                    loop_animation=True
                ),

                "battle_magic_fireshock": graphics_objects.SimpleLoopAnimation(
                    sprite_pack_path=self._sprite_pack_path + "/battle_magic_fireshock",
                    frame_duration=0.12,
                    loop_animation=False
                ),

                "battle_magic_ready_sleepmist": graphics_objects.SimpleLoopAnimation(
                    sprite_pack_path=self._sprite_pack_path + "/battle_magic_ready_sleepmist",
                    frame_duration=0.2,
                    loop_animation=True
                ),

                "battle_magic_sleepmist": graphics_objects.SimpleLoopAnimation(
                    sprite_pack_path=self._sprite_pack_path + "/battle_magic_sleepmist",
                    frame_duration=0.12,
                    loop_animation=False
                ),

            }
        )


class Noelle(PlayerCharacter):
    def __init__(self):
        super().__init__(
            sprite_folder_name="noelle",
            name="Noelle",
            max_hp=90,
            attack=3,
            defense=1,
            magic=11,
            battle_ui_color=Color(255, 255, 0, 255),
            battle_ui_icon_color=Color(255, 255, 0, 255),
            fight_box_color=Color(255, 255, 0, 255),
            fight_crit_box_color=Color(254, 254, 255, 255),
            spells=[
                SleepMist(),
                HealPrayer(),
                IceShock(),
                Spell(
                    name="SnowGrave",
                    description="Fatal",
                    tp_cost=200,
                    element_id=8,
                    base_health_change=1000,
                    is_friendly_spell=False,
                    is_healing_spell=False,
                    is_pacifying_spell=False,
                    is_aoe_spell=True
                )
            ]
        )

        self.magic_user_acts = [NoelleRudinnAction1(self)]


class December(PlayerCharacter):
    def __init__(self):
        super().__init__(
            sprite_folder_name="december",
            name="Dess",
            max_hp=120,
            attack=14,
            defense=2,
            magic=1,
            battle_ui_color=Color(255, 0, 0, 255),
            battle_ui_icon_color=Color(255, 64, 64, 255),
            fight_box_color=Color(255, 0, 0, 255),
            fight_crit_box_color=Color(255, 64, 64, 255),
            spells=[FireShock()]
        )

        self.magic_user_acts = [NoelleRudinnAction1(self)]

        self.animations_by_state["battle_idle"].set_frame_duration(0.25)

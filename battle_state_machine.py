from enum import Enum, auto

import arcade.key
import pyglet
from PIL import Image, ImageDraw
from arcade import SpriteList, Sprite, Texture
from arcade.gui import UILayout, UIWidget, UIManager
from arcade.types import Color

import battle_widgets
import character
import default_data
import items
import non_player_character
import player_character
import settings
from actions import SpellAction, SpareAction, ActionsQueue, Action, DefendAction, ItemAction, FightAction, ActAction
from animations.battle_animations import NumberBounceAnimation, HealAnimation, FightHitBar, CriticalHitSparkleAnimation, \
    StrikeEnemyAnimation, EnemyFleeingAnimation
from animations.common_animations import FadeInFadeOutColorAnimation, ShakeAnimation, SparkleAnimation
from battle_widgets import SpellList, SpellSelect, EnemySelectOptions, EnemySelect
from bullet_patterns import RainingDiamondBulletPattern
from dialog_exchange import DialogExchange
from dialogue_box import TextBoxDialog
from focus_stack import FocusStackMember, FocusStack
from items.consumable_items import ConsumableItem
from player_character import PlayerCharacter
from bullet_board import BulletBoard
from soul import Soul
from speech_bubble import SpeechBubbleDialog
from sprites_and_effects_collection import SpritesAndEffectsCollection

"""
This architecture is my attempt at replicating the state architecture recommended by Robert Nystrom in his book
Game Programming Patterns. The guide I followed can be found here:
https://gameprogrammingpatterns.com/state.html
"""

class BattleState(Enum):
    PLAYER_ATTACKING = auto()
    PLAYER_COMMAND = auto()
    PLAYER_ATTACK_SELECT = auto()
    PLAYER_ACT_ENEMY_SELECT = auto()
    PLAYER_MAGIC_ENEMY_SELECT = auto()
    PLAYER_ACT_SELECT = auto()
    PLAYER_ITEM_SELECT = auto()
    PLAYER_ITEM_PLAYER_SELECT = auto()
    PLAYER_MAGIC_SELECT = auto()
    PLAYER_SPARE_SELECT = auto()
    PLAYER_TARGET = auto()
    EXECUTING_QUEUED_PLAYER_COMMANDS = auto()
    DIALOGUE = auto()
    ENEMY_ATTACK = auto()
    VICTORY = auto()
    DEFEAT = auto()


class BattleController:
    def __init__(self, ui_manager: UIManager,
                 battle_player_character_cards: UILayout,
                 battle_textbox: UIWidget,
                 players: list[player_character.PlayerCharacter],
                 enemies: list[non_player_character.NonPlayerCharacter],
                 sprites_and_effects_collection: SpritesAndEffectsCollection,
                 tp_meter: battle_widgets.TPMeter,
                 bullet_board: BulletBoard):
        # TODO: move most of these parameters into the BattleController.

        # Sprite lists that need to be accessed for animations.
        self.sprites_and_effects_collection = sprites_and_effects_collection

        self.battle_player_character_cards = battle_player_character_cards
        self.battle_textbox = battle_textbox
        self.ui_manager = ui_manager
        self.tp_meter = tp_meter
        self.players = players
        self.enemies = enemies
        self.bullet_board = bullet_board

        # This variable controls whether the battle is scripted (typically a boss/miniboss battle).
        # Scripted battles typically have dialog that progresses each turn, while non-scripted battles have dialog that
        # is mostly random depending on player interaction.
        self.is_scripted_battle = False

        # If the battle is scripted, this array is meant to contain a sequence of DialogueExchange objects representing
        # the scripted dialog exchanges that occur before each turn.
        # One example of a dialog exchange in Deltarune is the following interaction:
        # Gerson: "But... there is one thing that can overwrite the dark."
        # Gerson: "A white pen, known as hope."
        # Gerson: "Miss! I believe... this is what you hold."
        # Susie: "Me? Nah, Kris has the pen."
        # Susie: "My weapon's like a hairbrush or something."
        # Gerson: "Geh-hahahahaha! Is that so? Is that SO???"
        # Susie: "Yep. Now shut up and give me that axe!"
        self.scripted_dialogue = [
            DialogExchange(
                battle_textbox=self.battle_textbox,
                sprites_and_effects_collection=self.sprites_and_effects_collection,
                dialog_instances=[
                    TextBoxDialog(
                        text="So...this is scripted dialog.",
                        portrait_texture_path="assets/sprites/player_characters/susie/dialog_portraits/susie_surveilling_the_current_situation.png",
                        text_sound_path="assets/audio/dialog/snd_txtsus.wav"
                    ),
                    SpeechBubbleDialog(
                        text="That would\nappear to be\nthe case, yes.",
                        row_count=3,
                        column_count=14,
                        actor=self.enemies[0]
                    ),
                    TextBoxDialog(
                        text="How does scripted dialog work?",
                        portrait_texture_path="assets/sprites/player_characters/susie/dialog_portraits/susie_looking_at_the_camera_curiously.png",
                        text_sound_path="assets/audio/dialog/snd_txtsus.wav"
                    ),
                    SpeechBubbleDialog(
                        text="You load instances of\nthe DialogExchange object\ninto self.scripted_dialog\nin the battle controller.",
                        row_count=4,
                        column_count=25,
                        actor=self.enemies[1]
                    ),
                    SpeechBubbleDialog(
                        text="In each DialogExchange instance, pass\ninstances of TextBoxDialog\nand SpeechBubble dialog objects\ninto the dialog_instances parameter.",
                        row_count=4,
                        column_count=37,
                        actor=self.enemies[1]
                    ),
                    SpeechBubbleDialog(
                        text="SpeechBubbleDialog instances\nspawn speech bubbles\nsuch as this one.",
                        row_count=3,
                        column_count=28,
                        actor=self.enemies[1]
                    ),
                    TextBoxDialog(
                        text="Ah, that makes sense, I think..?",
                        portrait_texture_path="assets/sprites/player_characters/susie/dialog_portraits/susie_surveilling_the_current_situation.png",
                        text_sound_path="assets/audio/dialog/snd_txtsus.wav"
                    ),
                    TextBoxDialog(
                        text="And TextBoxDialog instances create text boxes like this one?",
                        portrait_texture_path="assets/sprites/player_characters/susie/dialog_portraits/susie_looking_at_the_camera_curiously.png",
                        text_sound_path="assets/audio/dialog/snd_txtsus.wav"
                    ),
                    SpeechBubbleDialog(
                        text="That's correct!\nYour attunement to the\nmetaphysical properties\nof your universe is\ntruly on point.",
                        row_count=5,
                        column_count=23,
                        actor=self.enemies[2]
                    ),
                ]
            )
        ]

        # The current dialog exchange being loaded by the fight.
        self.current_dialog_exchange = None

        # Speech bubbles spawned during the fight can be placed in here to be automatically deleted at the start of the
        # enemy attack.
        self.active_speech_bubbles = []

        self.current_player_index = 0

        self.state = BattleState.PLAYER_COMMAND
        self.turn = 0
        self.selected_command = None
        self.selected_target = None

        # The amount of dark dollars that will be given to the player if they win the fight.
        self.dark_dollars_given_on_defeat = 0
        for enemy in self.enemies:
            self.dark_dollars_given_on_defeat += enemy.dark_dollars_given_on_defeat

        # The amount of enemies defeated through violent means.
        self.enemies_defeated_violently = 0

        self.ui_manager.execute_layout()

        # The focus stack for the battle GUI.
        self.focus_stack = FocusStack(self.ui_manager)

        self.focus_stack.push(
            self.battle_player_character_cards,
            self.battle_player_character_cards.children[self.current_player_index].children[0],
            self.state,
            5
        )

        # Loads menu sounds
        self.menu_move_sound = arcade.load_sound("assets/audio/gui/snd_menumove.wav", False)
        self.menu_select_sound = arcade.load_sound("assets/audio/gui/snd_select.wav", False)
        self.hurt_sound = arcade.load_sound("assets/audio/battle/player_character/common/snd_hurt1.wav", False)
        self.heal_sound = arcade.load_sound("assets/audio/battle/player_character/common/snd_power.wav", False)
        self.mercy_add_sound = arcade.load_sound("assets/audio/battle/player_character/common/snd_mercyadd.wav", False)
        self.spare_sound = arcade.load_sound("assets/audio/battle/player_character/common/snd_spare.wav", False)
        self.tp_add_sound = arcade.load_sound("assets/audio/battle/player_character/common/snd_cardrive.wav", False)
        self.player_attack_sound = arcade.load_sound("assets/audio/battle/player_character/common/snd_laz_c.wav", False)
        self.player_critical_hit_sound = arcade.load_sound("assets/audio/battle/player_character/common/snd_criticalswing.wav", False)
        self.enemy_hit_sound = arcade.load_sound("assets/audio/battle/non_player_character/common/snd_damage.wav", False)
        self.enemy_flee_sound = arcade.load_sound("assets/audio/battle/non_player_character/common/snd_defeatrun.wav", False)
        self.power_sound = arcade.load_sound("assets/audio/battle/snd_dtrans_lw.ogg", False)

        # The queue of actions selected by the player for each character.
        self.actions_queue = ActionsQueue()
        self.sorted_actions_queue = {}

        self.items = items.consumable_items.initialize_default_consumable_items()

        self.fight_box_sprites_array = []
        self.fight_crit_box_sprites_array = []
        self.icon_and_press_sprites_array = []
        self.blue_divider_lines_sprites_array = []
        self.press_texture = arcade.load_texture("assets/textures/gui_graphics/battle/fight_graphics/press.png")
        self.fight_hit_markers = []

        # All of the clocks used by the BattleController.
        # The clock used by the fight bars.
        self.fight_bar_clock = 0.0
        self.fight_bar_clock_is_updating = False

        # The timer used by the enemy attack.
        self.enemy_attack_time = 0.0
        self.enemy_attack_duration = 10.0
        self.enemy_is_attacking = False

        self.battle_idle_callback = None
        self.battle_idle_target = None
        self.enemy_hit_sound_player = None

        # The SOUL the player moves around during enemy attacks.
        self.soul = Soul(self.players[0], self)
        self.sprites_and_effects_collection.soul_sprites.append(self.soul)

        # A variable tracking whether the bullet board has been loaded for the current turn.
        # Used by logic in the HitBar class used to load an enemy attack after the player finishes the FIGHT act.
        self.load_bullet_board_called_for_this_turn = False

        # Tracks which keys are pressed down. Used for situations where controls requires multiple keys.
        self.z_pressed = False
        self.x_pressed = False
        self.c_pressed = False
        self.up_pressed = False
        self.down_pressed = False
        self.left_pressed = False
        self.right_pressed = False

    def add_key_pressed(self, key):
        """
        If a key is pressed, track that it is pressed.
        :param key: The key that was pressed.
        :return:
        """
        match key:
            case arcade.key.Z:
                self.z_pressed = True
                return
            case arcade.key.X:
                self.x_pressed = True
                return
            case arcade.key.C:
                self.c_pressed = True
                return
            case arcade.key.UP:
                self.up_pressed = True
                return
            case arcade.key.DOWN:
                self.down_pressed = True
                return
            case arcade.key.LEFT:
                self.left_pressed = True
                return
            case arcade.key.RIGHT:
                self.right_pressed = True
                return

    def remove_key_pressed(self, key):
        """
        If a key is released, track that it was released.
        :param key: The key that was pressed.
        :return:
        """
        match key:
            case arcade.key.Z:
                self.z_pressed = False
                return
            case arcade.key.X:
                self.x_pressed = False
                return
            case arcade.key.C:
                self.c_pressed = False
                return
            case arcade.key.UP:
                self.up_pressed = False
                return
            case arcade.key.DOWN:
                self.down_pressed = False
                return
            case arcade.key.LEFT:
                self.left_pressed = False
                return
            case arcade.key.RIGHT:
                self.right_pressed = False
                return

    def update_clocks(self, delta_time: float):
        """
        This is where any local clocks used by the battle controller are updated.
        :return: None
        """
        if self.fight_bar_clock_is_updating:
            self.fight_bar_clock += delta_time

        if self.enemy_is_attacking:
            self.enemy_attack_time += delta_time

            if self.enemy_attack_time > self.enemy_attack_duration:
                self.enemy_is_attacking = False
                self.end_enemy_attack()

    def start_fight_bar_clock(self):
        """
        Starts the clock used to move the attack bars used during the FIGHT act.
        :return: None
        """
        self.fight_bar_clock = 0.0
        self.fight_bar_clock_is_updating = True

    def stop_fight_bar_clock(self):
        """
        Stops the clock used to move the attack bars used during the FIGHT act.
        :return: None
        """
        self.fight_bar_clock_is_updating = False
        self.fight_bar_clock = 0.0

    def start_enemy_attack_clock(self):
        """
        Starts the clock used to track the elapsed time of the enemy attack.
        :return: None
        """
        self.enemy_attack_time = 0.0
        self.enemy_is_attacking = True

    def stop_enemy_attack_clock(self):
        """
        Stops the clock used to track the elapsed time of the enemy attack.
        :return: None
        """
        self.enemy_attack_time = 0.0
        self.enemy_is_attacking = False

    def load_bullet_board(self):
        """ Loads the bullet board with the SOUL at the beginning of the enemy turn. """
        self.bullet_board.load_bullet_board(self)
        self.soul.move_to_bullet_board()

    def unload_bullet_board(self):
        """ Loads the bullet board with the SOUL at the beginning of the enemy turn. """
        self.bullet_board.unload_bullet_board(self)
        self.soul.move_to_player_with_soul()

    def confirm_command(self):
        SelectCommand(self).execute()

    def cancel_command(self):
        CancelCommand(self).execute()

    def right_command(self):
        RightCommand(self).execute()

    def left_command(self):
        LeftCommand(self).execute()

    def up_command(self):
        UpCommand(self).execute()

    def down_command(self):
        DownCommand(self).execute()

    def handle_key(self, key):
        """ Handles user inputs made during the battle. """

        match key:
            case arcade.key.Z:
                self.confirm_command()
            case arcade.key.X:
                self.cancel_command()
            case arcade.key.RIGHT:
                self.right_command()
            case arcade.key.LEFT:
                self.left_command()
            case arcade.key.UP:
                self.up_command()
            case arcade.key.DOWN:
                self.down_command()

    def check_if_battle_is_won(self):
        """
        Checks if the battle is won yet. The win condition is that all the enemies have been defeated, peacefully or not
        :return: A boolean representing if there are any enemies left in battle.
        """
        return len(self.enemies) == 0

    def end_battle(self):
        """
        Ends the battle in the case of a player victory.
        :return: None
        """
        if self.state != BattleState.VICTORY:
            # Set the player state to VICTORY.
            self.state = BattleState.VICTORY

            # Set the animation states of the players to play their victory animations.
            for player in self.players:
                player.set_animation_state("battle_victory")

            # Calculate the amount of TP gained from the fight.
            self.dark_dollars_given_on_defeat = int(self.dark_dollars_given_on_defeat + self.tp_meter.get_tp_in_meter())

            # Check if any enemies were defeated violently. Modify the win message accordingly.
            if self.enemies_defeated_violently == 0:
                second_line_of_win_message = "* Got 0 EXP and " + str(self.dark_dollars_given_on_defeat) + " D$."
            else:
                second_line_of_win_message = "* You became stronger."
                self.power_sound.play(speed=2.0)

            win_message = "* You won!\n" + second_line_of_win_message
            self.battle_textbox.load_dialog(TextBoxDialog(text=win_message))

    def add_tp_to_meter(self, amount: float = 0.0):
        """
        Adds TP to the TP meter. Negative values should also work.
        :param amount: The amount of TP to add to the meter.
        :return: None
        """
        self.tp_meter.update_tp_meter(amount)

    def move_to_next_player_card(self, action: Action):
        """
        Moves to the next player card in the HUD.
        :return:
        """
        self.actions_queue.push(action)

        # Check if the next player character is downed. If so, skip over them.
        next_character_index_change = 1
        not_knocked_out_next_character_found = False

        while (not not_knocked_out_next_character_found) and self.current_player_index + next_character_index_change < self.focus_stack.get_highest_member().get_full_layout_length():
            if self.players[self.current_player_index + next_character_index_change].hp < 0:
                next_character_index_change += 1
            else:
                not_knocked_out_next_character_found = True

        if self.current_player_index + next_character_index_change < self.focus_stack.get_highest_member().get_full_layout_length():
            self.state = BattleState.PLAYER_COMMAND
            self.focus_stack.pop()
            self.battle_player_character_cards.children[self.current_player_index].unfocus()
            self.current_player_index += next_character_index_change
            self.battle_player_character_cards.children[self.current_player_index].focus()
            self.menu_select_sound.play()
            self.focus_stack.push(
                self.battle_player_character_cards,
                self.battle_player_character_cards.children[self.current_player_index].children[0],
                self.state,
                5,
                False
            )
        else:
            self.battle_player_character_cards.children[self.current_player_index].unfocus()
            self.focus_stack.pop()
            self.state = BattleState.EXECUTING_QUEUED_PLAYER_COMMANDS
            self.initialize_sorted_action_queue()
            self.execute_queued_player_action()


    def move_to_previous_player_card(self):
        """
        Move to the previous player card.
        :return: None
        """
        # Check if the next player character is downed. If so, skip over them.
        previous_character_index_change = 1
        not_knocked_out_previous_character_found = False

        while (
                not not_knocked_out_previous_character_found) and self.current_player_index - previous_character_index_change > 0:
            if self.players[self.current_player_index - previous_character_index_change].hp < 0:
                previous_character_index_change += 1
            else:
                not_knocked_out_previous_character_found = True

        if self.current_player_index > 0:
            self.battle_player_character_cards.children[self.current_player_index].unfocus()
            self.current_player_index -= previous_character_index_change
            self.battle_player_character_cards.children[
                self.current_player_index].focus()
            self.focus_stack.push(
                self.battle_player_character_cards,
                self.battle_player_character_cards.children[
                    self.current_player_index].children[0],
                self.state,
                5
            )
            if len(self.actions_queue) > 0:
                self.actions_queue.pop()
            self.menu_move_sound.play()
            self.battle_player_character_cards.children[
                self.current_player_index].change_icon()

    def move_to_first_player_card(self):
        """
        Moves to the first player card in the HUD. Executed after the enemy turn completes.
        :return:
        """
        if len(self.players) > 0:
            self.state = BattleState.PLAYER_COMMAND

            self.current_player_index = 0
            self.battle_player_character_cards.children[self.current_player_index].focus()
            self.focus_stack.push(
                self.battle_player_character_cards,
                self.battle_player_character_cards.children[self.current_player_index].children[0],
                self.state,
                5
            )

    def spawn_fight_bars(self, players_fighting: list[PlayerCharacter], enemy_targets: list[character.Character]):
        """
        Creates a FIGHT graphic for the fighting players.
        :param players_fighting: The player characters attacking.
        :param enemy_targets: The respective targets of the player characters.
        :return: None
        """
        if len(self.fight_box_sprites_array) > 0:
            for sprite in self.fight_box_sprites_array:
                sprite.kill()
        if len(self.fight_crit_box_sprites_array) > 0:
            for sprite in self.fight_crit_box_sprites_array:
                sprite.kill()
        if len(self.icon_and_press_sprites_array) > 0:
            for sprite in self.icon_and_press_sprites_array:
                sprite.kill()
        if len(self.blue_divider_lines_sprites_array) > 0:
            for sprite in self.blue_divider_lines_sprites_array:
                sprite.kill()

        self.start_fight_bar_clock()

        height_of_fight_ui = int(settings.WINDOW_HEIGHT / 4)
        height_of_fight_bar = int(height_of_fight_ui / (len(players_fighting) if len(players_fighting) > 3 else 3))
        width_of_fight_bar = 236
        width_of_fight_crit_bar = 20


        player_index = 0
        icon_center_x = 48
        press_center_x = 128
        fight_box_center_x = settings.WINDOW_WIDTH / 5
        fight_crit_box_center_x = fight_box_center_x - ((width_of_fight_bar / 2) - 16)

        icon_scale = 2.0 if len(players_fighting) < 4 else 2.0 / (len(players_fighting) / 3)

        fight_hit_bar_effects = []

        for player in players_fighting:
            fight_box = Image.new("RGBA", (width_of_fight_bar, height_of_fight_bar), (0, 0, 0, 255))
            fight_crit_box = Image.new("RGBA", (width_of_fight_crit_bar, height_of_fight_bar), (0, 0, 0, 255))
            draw_fight_box = ImageDraw.Draw(fight_box)
            draw_fight_crit_box = ImageDraw.Draw(fight_crit_box)
            fight_box_center_y = height_of_fight_ui - ((height_of_fight_bar / 2) + (height_of_fight_bar * player_index))

            draw_fight_box.rectangle(
                [
                    (0, 0),
                    (width_of_fight_bar - 1, height_of_fight_bar)
                ],
                outline=player.fight_box_color.swizzle("rgba"),
                width=4
            )
            fight_box_sprite = Sprite(Texture(fight_box), center_x=fight_box_center_x, center_y=fight_box_center_y)

            self.fight_box_sprites_array.append(fight_box_sprite)
            self.sprites_and_effects_collection.effects_sprites.append(fight_box_sprite)

            if player_index > 0:
                length_of_divider_bar = int((settings.WINDOW_WIDTH - fight_box_sprite.right) / 5)
                blue_divider_line = Image.new("RGBA", (length_of_divider_bar, 4), (0, 0, 128, 255))
                blue_divider_line_center_x = fight_box_sprite.right + (length_of_divider_bar / 2)
                blue_divider_line_center_y = fight_box_sprite.top - 2
                blue_divider_line_sprite = Sprite(Texture(blue_divider_line),
                                                  center_x=blue_divider_line_center_x,
                                                  center_y=blue_divider_line_center_y)

                self.blue_divider_lines_sprites_array.append(blue_divider_line_sprite)
                self.sprites_and_effects_collection.effects_sprites.append(blue_divider_line_sprite)

            draw_fight_crit_box.rectangle(
                [
                    (0, 0),
                    (width_of_fight_crit_bar, height_of_fight_bar)
                ],
                outline=player.fight_crit_box_color.swizzle("rgba"),
                width=4
            )
            fight_crit_box_sprite = Sprite(Texture(fight_crit_box), center_x=fight_crit_box_center_x, center_y=fight_box_center_y)

            self.fight_crit_box_sprites_array.append(fight_crit_box_sprite)
            self.sprites_and_effects_collection.effects_sprites.append(fight_crit_box_sprite)


            icon_sprite = Sprite(player.normal_icon_texture, scale=icon_scale, center_x=icon_center_x, center_y=fight_box_center_y)
            press_sprite = Sprite(self.press_texture, scale=2.0, center_x=press_center_x, center_y=fight_box_center_y + ((height_of_fight_bar / 2) - 20))
            self.icon_and_press_sprites_array.append(icon_sprite)
            self.icon_and_press_sprites_array.append(press_sprite)
            self.sprites_and_effects_collection.effects_sprites.append(icon_sprite)
            self.sprites_and_effects_collection.effects_sprites.append(press_sprite)

            fight_hit_bar_effect = FightHitBar(
                controller=self,
                actor=players_fighting[player_index],
                target=enemy_targets[player_index],
                bar_height=height_of_fight_bar,
                bar_center_y=int(fight_box_center_y)
            )
            self.fight_hit_markers.append(fight_hit_bar_effect)
            fight_hit_bar_effects.append(fight_hit_bar_effect)
            player_index += 1

        for fight_hit_bar_effect in fight_hit_bar_effects:
            for sprite in fight_hit_bar_effect.get_sprites():
                self.sprites_and_effects_collection.effects_sprites.append(sprite)

        for fight_hit_bar_effect in fight_hit_bar_effects:
            self.sprites_and_effects_collection.effects.append(fight_hit_bar_effect)

        for fight_hit_bar_effect in fight_hit_bar_effects:
            fight_hit_bar_effect.time = 0
            fight_hit_bar_effect.sprite.center_x = fight_hit_bar_effect.initial_center_x

    def despawn_fight_bars(self):
        """ Cleans up the fight bars after they've spawned. """
        for sprite in self.fight_box_sprites_array:
            sprite.kill()
        for sprite in self.fight_crit_box_sprites_array:
            sprite.kill()
        for sprite in self.icon_and_press_sprites_array:
            sprite.kill()
        for sprite in self.blue_divider_lines_sprites_array:
            sprite.kill()

        self.fight_box_sprites_array.clear()
        self.fight_crit_box_sprites_array.clear()
        self.icon_and_press_sprites_array.clear()
        self.blue_divider_lines_sprites_array.clear()

    def attempt_to_hit_enemy(self):
        """
        Goes through the hit markers, finds the positions of the hit markers closest to the left and checks if they
        are within the bounding box of the fight box sprite.
        :return: A ratio representing the attack multiplier for the attack.
        """

        fight_box_max_x = self.fight_box_sprites_array[0].right
        fight_box_min_x = self.fight_box_sprites_array[0].left

        fight_crit_box_max_x = self.fight_crit_box_sprites_array[0].right
        fight_crit_box_min_x = self.fight_crit_box_sprites_array[0].left
        fight_crit_box_center_x = self.fight_crit_box_sprites_array[0].center_x

        min_hit_marker_center_x = settings.WINDOW_WIDTH
        for hit_marker in self.fight_hit_markers:
            if hit_marker.sprite.center_x <= min_hit_marker_center_x:
                min_hit_marker_center_x = hit_marker.sprite.center_x

        enemy_hit = False
        is_crit = False

        for hit_marker in self.fight_hit_markers[:]:
            if min_hit_marker_center_x - 20 < hit_marker.sprite.center_x < min_hit_marker_center_x + 20 and fight_box_min_x < hit_marker.sprite.center_x < fight_box_max_x:
                enemy_hit = True
                if fight_box_min_x <= hit_marker.sprite.center_x <= fight_box_max_x:
                    if fight_crit_box_min_x <= hit_marker.sprite.center_x <= fight_crit_box_max_x:
                        hit_marker.sprite.center_x = fight_crit_box_center_x
                        hit_marker.register_critical_hit()
                        attack_multiplier = 1.25
                        is_crit = True
                    else:
                        hit_marker.register_hit()
                        attack_multiplier = fight_box_min_x / hit_marker.sprite.center_x

                    self.attack_target(hit_marker.actor, hit_marker.target, attack_multiplier, is_crit)

                    if is_crit:
                        critical_hit_sparkle_animation = CriticalHitSparkleAnimation(hit_marker.actor)
                        self.sprites_and_effects_collection.effects.append(critical_hit_sparkle_animation)
                        for sprite in critical_hit_sparkle_animation.get_sprites():
                            self.sprites_and_effects_collection.effects_sprites.append(sprite)

                self.fight_hit_markers.remove(hit_marker)

        if enemy_hit:
            self.player_attack_sound.play()
            if is_crit:
                self.player_critical_hit_sound.play()

    def attack_target(self, actor: player_character.PlayerCharacter, target: character.Character,
                      attack_damage_multiplier: float = 1.0, is_crit: bool = False):
        """ Decreases the targets health by a calculated amount and animates the target taking damage. """
        # TODO: Maybe add percentages to elemental pairs to control how much damage is resisted/amplified?

        if len(self.enemies) > 0:
            if target not in self.enemies:
                target = self.enemies[0]
        else:
            target = None

        actor.attack_enemy(enemy=target, controller=self, attack_damage_multiplier=attack_damage_multiplier)

        # TODO: This currently makes the damage numbers above the enemies disappear.

        """
        if is_crit:
            self.add_tp_to_meter(6.0)
        else:
            self.add_tp_to_meter(attack_damage_multiplier * 4.0)
        """

    def use_consumable_item_on_targets(self, item: ConsumableItem, actor: player_character.PlayerCharacter,
                                       targets: list[character.Character]):
        """
        Uses a consumable item on a list of targets. Probably going to be used by the action queue. Probably.
        :param item: the item being used.
        :param actor: the actor using the item.
        :param targets: the targets that the actor is giving the item to.
        :return: None
        """

        actor.set_animation_state("battle_idle")
        player_healed = False
        player_damaged = False

        for target in targets:
            previous_target_hp = target.hp
            damage_healt = 0
            if item.is_revive_item:
                if target.hp < 0:
                    target.hp = 1
                    damage_healt += target.hp - previous_target_hp
                if item.is_relative_healing_item:
                    amount_healed_by_percent = min(target.hp + (target.max_hp * item.hp_percentage_restored), target.max_hp)
                    target.hp = amount_healed_by_percent
                    damage_healt += amount_healed_by_percent
                else:
                    amount_healed_by_absolute = min(target.hp + item.hp_restored, target.max_hp)
                    target.hp += amount_healed_by_absolute
                    damage_healt += amount_healed_by_absolute
            else:
                if item.is_relative_healing_item:
                    amount_healed_by_percent = min(target.hp + (target.max_hp * item.hp_percentage_restored), target.max_hp)
                    target.hp += amount_healed_by_percent
                    damage_healt += amount_healed_by_percent
                else:
                    target.hp += item.hp_restored
                    damage_healt += item.hp_restored

            if target.hp > target.max_hp:
                target.hp = target.max_hp

            damage_healt_text = str(abs(damage_healt))
            damage_healed_color = arcade.color.WHITE
            if damage_healt > 0:
                player_healed = True
                damage_healed_color = arcade.color.NEON_GREEN # Color(0, 214, 0, 255)
                color_filter_animation = FadeInFadeOutColorAnimation(
                    sprite=target,
                    color=arcade.color.WHITE,
                    total_duration=0.3
                )
                self.sprites_and_effects_collection.effects.append(color_filter_animation)
                self.sprites_and_effects_collection.effects_sprites.append(color_filter_animation.filter_sprite)

                sparkle_animation = HealAnimation(
                    target=target
                )

                self.sprites_and_effects_collection.effects.append(sparkle_animation)
                for sprite in sparkle_animation.get_sprites():
                    self.sprites_and_effects_collection.effects_sprites.append(sprite)

            elif damage_healt < 0:
                if target.hp <= 0 and previous_target_hp > 0:
                    damage_healt_text = "DOWN"
                    damage_healed_color = arcade.color.RED
                    target.set_animation_state("battle_downed")
                    target.hp = -80
                else:
                    player_damaged = True
                    if not target.is_player_defending():
                        target.set_animation_state("battle_hurt")
                        pyglet.clock.schedule_once(lambda dt: target.set_animation_state("battle_idle"), 1.0)
                shake_animation = ShakeAnimation(
                    sprite=target
                )
                self.sprites_and_effects_collection.effects.append(shake_animation)
                arcade.play_sound(self.hurt_sound)

            if target.hp >= target.max_hp:
                damage_healt_text = "MAX"

            if target.hp > 0 and previous_target_hp <= 0:
                damage_healt_text = "UP"
                damage_healed_color = arcade.color.NEON_GREEN
                target.set_animation_state("battle_idle")

            damage_healed_animation = NumberBounceAnimation(
                text=damage_healt_text,
                color=damage_healed_color,
                target=target
            )

            self.sprites_and_effects_collection.effects.append(damage_healed_animation)
            self.sprites_and_effects_collection.effects_sprites.append(damage_healed_animation.sprite)

        if player_healed:
            arcade.play_sound(self.heal_sound)
        if player_damaged:
            arcade.play_sound(self.hurt_sound)

    def open_enemy_select_menu(self):
        """
        Opens the enemy select menu.
        :return: None
        """
        enemy_list_full_layout = EnemySelect(self.enemies)
        enemy_list_interactive_layout = enemy_list_full_layout.children[1]
        self.focus_stack.push(enemy_list_full_layout, enemy_list_interactive_layout,
                                         self.state, 1, True)
        new_focus_animation = self.focus_stack.get_highest_member().get_focused_widget().enemy.focus()
        self.sprites_and_effects_collection.effects.append(new_focus_animation)
        self.sprites_and_effects_collection.effects_sprites.append(new_focus_animation.filter_sprite)

    def move_focus_between_enemies_in_enemy_select(self, previously_focused_widget, currently_focused_widget):
        """
        Used to animate the enemies being targeted in the enemy select screen.
        :param previously_focused_widget: The previously focused enemy's row in the enemy select.
        :param currently_focused_widget: The newly focused enemy's row in the enemy select.
        :return:
        """
        new_focus_animation = currently_focused_widget.enemy.focus()
        self.sprites_and_effects_collection.effects.append(new_focus_animation)
        self.sprites_and_effects_collection.effects_sprites.append(new_focus_animation.filter_sprite)
        previously_focused_widget.enemy.unfocus()

    def open_player_select_menu(self):
        """
        Opens the player select menu.
        :return: None
        """
        player_list_full_layout = battle_widgets.PlayerSelect(self.players)
        player_list_interactive_layout = player_list_full_layout
        self.focus_stack.push(player_list_full_layout, player_list_interactive_layout,
                                         self.state, 1, True)
        new_focus_animation = self.focus_stack.get_highest_member().get_focused_widget().player.focus()
        self.sprites_and_effects_collection.effects.append(new_focus_animation)
        self.sprites_and_effects_collection.effects_sprites.append(new_focus_animation.filter_sprite)

    def move_focus_between_players_in_player_select(self, previously_focused_widget, currently_focused_widget):
        """
        Used to animate the enemies being targeted in the enemy select screen.
        :param previously_focused_widget: The previously focused enemy's row in the enemy select.
        :param currently_focused_widget: The newly focused enemy's row in the enemy select.
        :return:
        """
        new_focus_animation = currently_focused_widget.player.focus()
        self.sprites_and_effects_collection.effects.append(new_focus_animation)
        self.sprites_and_effects_collection.effects_sprites.append(new_focus_animation.filter_sprite)
        previously_focused_widget.player.unfocus()

    def initialize_sorted_action_queue(self):
        """
        Populates self.sorted_actions_queue with a sorted list of the queued player character actions.
        Meant to be executed after the player selects the action of the last party member in the battle.
        Clears the actions queue before the next round.
        :return:
        """
        self.sorted_actions_queue = self.actions_queue.sort_actions_queue()
        self.actions_queue.clear()

    def execute_queued_player_action(self):
        """
        Executes the highest priority player action.
        :return: None
        """
        if self.check_if_battle_is_won():
            self.end_battle()
            return

        if len(self.sorted_actions_queue["complex_act_actions"]) > 0:
            self.sorted_actions_queue["act_actions"].pop().execute()
            return
        elif len(self.sorted_actions_queue["simple_act_actions"]) > 0:
            """
            act_texts = ""
            for action in self.sorted_actions_queue["simple_act_actions"]:
                act_text = self.sorted_actions_queue["simple_act_actions"].pop().execute()
                act_texts += "* " + act_text + "\n"
            self.battle_textbox.load_dialog(TextBoxDialog(act_texts))
            """
            self.sorted_actions_queue["simple_act_actions"].pop().execute()
            return
        elif len(self.sorted_actions_queue["magic_spare_item_actions"]) > 0:
            self.sorted_actions_queue["magic_spare_item_actions"].pop().execute()
            return
        elif len(self.sorted_actions_queue["fight_actions"]) > 0:
            self.state = BattleState.PLAYER_ATTACKING
            self.battle_textbox.load_dialog(TextBoxDialog(text=""))
            fighting_players = []
            enemy_targets = []
            for fight_action in self.sorted_actions_queue["fight_actions"]:
                fighting_players.insert(0, fight_action.actor)
                enemy_targets.insert(0, fight_action.target)
            self.sorted_actions_queue["fight_actions"].clear()
            self.spawn_fight_bars(fighting_players, enemy_targets)
            return
        else:
            # Start the pre enemy attack dialog.
            self.start_pre_enemy_attack_dialog()
            return

    def start_pre_enemy_attack_dialog(self):
        """
        Initializes the pre-enemy attack dialog.
        :return: None
        """
        self.despawn_fight_bars()

        # Check if the battle is over. If so, end the battle.
        if self.check_if_battle_is_won():
            self.end_battle()
            return

        self.state = BattleState.DIALOGUE

        if len(self.scripted_dialogue) == 0:
            self.spawn_enemy_speech_bubbles()
        else:
            dialog_exchange = self.scripted_dialogue.pop(0)
            self.current_dialog_exchange = dialog_exchange
            self.spawn_next_dialog_from_dialog_exchange()

    def spawn_next_dialog_from_dialog_exchange(self):
        """
        Spawns the next dialog from the current dialog exchange.
        :return: None
        """
        self.despawn_speech_bubbles()

        if not self.current_dialog_exchange.execute_next_dialog():
            self.start_enemy_attack()

    def spawn_enemy_speech_bubbles(self):
        """
        Spawns enemy speech bubbles prior to the enemy attack.
        :return: None
        """
        # Clear any text from the battle textbox.
        self.battle_textbox.load_dialog(TextBoxDialog(text=""))

        for enemy in self.enemies:
            speech_bubble = enemy.spawn_speech_bubble_this_turn()
            self.active_speech_bubbles.append(speech_bubble)

    def despawn_speech_bubbles(self):
        """
        Despawns all enemy speech bubbles in lieu of the enemy attack.
        :return: None
        """
        for speech_bubble in self.active_speech_bubbles:
            speech_bubble.despawn_speech_bubble()

        self.active_speech_bubbles.clear()

    def start_enemy_attack(self):
        """
        Starts the enemy attack.
        :return: None
        """

        # Begin the enemy attack
        self.state = BattleState.ENEMY_ATTACK
        self.load_bullet_board()
        self.despawn_fight_bars()

        # Execute the enemy attack depending on all the enemies in the battle and calculate the duration of the attack
        sum_of_attack_durations = 0.0
        if len(self.enemies) > 0:
            for enemy in self.enemies:
                attack_duration = enemy.execute_attack(self.enemies)
                sum_of_attack_durations += attack_duration

        # Set the duration of the attack and start the attack clock.
        if len(self.enemies) > 0:
            self.enemy_attack_duration = sum_of_attack_durations / len(self.enemies)
        else:
            self.enemy_attack_duration = 10.0
        self.start_enemy_attack_clock()

        self.load_bullet_board_called_for_this_turn = True

    def end_enemy_attack(self):
        """
        Ends the enemy attack.
        :return:
        """
        # Terminate all the currently active enemy attacks
        if len(self.enemies) > 0:
            for enemy in self.enemies:
                enemy.terminate_attack()

        # Set all the defending players to not be defending.
        for player in self.players:
            if player.is_defending:
                player.undefend()

        # Return the state of the battle back to the starting state.
        self.unload_bullet_board()
        self.stop_enemy_attack_clock()
        self.load_bullet_board_called_for_this_turn = False

    def change_player_icon(self, icon_path: str = ""):
        """ Changes the icon of the current player to the icon at the given path. """
        self.battle_player_character_cards.children[self.current_player_index].change_icon(icon_path)

    def change_all_player_icons_to_default(self):
        """ Changes the icon of all players to their default icon. """
        for battle_player_character_card in self.battle_player_character_cards.children:
            battle_player_character_card.change_icon()

    def set_animation_state_of_all_players(self, animation_state: str):
        """
        Sets the animation state of all players to the provided animation state. Defaults to battle idle.
        :param animation_state: The animation state to give the players.
        :return: None
        """
        if not animation_state:
            animation_state = "battle_idle"

        for player in self.players:
            player.set_animation_state(animation_state)

    def reset_player_animation_states_before_next_turn(self):
        """
        Resets all non-downed players to have the battle_idle animation state.
        :return: None
        """

        for player in self.players:
            if player.hp > 0:
                player.set_animation_state("battle_idle")

class Command:
    """ The default command object. Represents the Command design pattern. """

    def __init__(self, controller: BattleController):
        self.controller = controller

    def execute(self):
        pass


class SelectCommand(Command):
    """ A command object representing the user selecting (usually pressing Z in the original game.) """

    def execute(self):
        match self.controller.state:
            case BattleState.PLAYER_COMMAND:
                self.controller.menu_select_sound.play()
                match self.controller.focus_stack.get_highest_member().focused_widget_index:
                    case 0:  # user selects ATTACK button
                        self.controller.state = BattleState.PLAYER_ATTACK_SELECT
                        self.controller.open_enemy_select_menu()
                        return
                    case 1:  # user selects ACT/MAGIC button
                        if self.controller.focus_stack.get_highest_member().get_focused_widget().name == "ACT":  # ACT button
                            self.controller.state = BattleState.PLAYER_ACT_ENEMY_SELECT
                            self.controller.open_enemy_select_menu()
                            return
                        else:  # MAGIC button
                            self.controller.state = BattleState.PLAYER_MAGIC_SELECT
                            spell_list_full_layout = SpellSelect(
                                self.controller.focus_stack.get_highest_member().get_interactive_ui_layout().player_character,
                                self.controller
                            )
                            spell_list_interactive_layout = spell_list_full_layout.children[0]
                            self.controller.focus_stack.push(spell_list_full_layout, spell_list_interactive_layout,
                                                             self.controller.state, 2, True)
                            return
                    case 2:  # user selects the ITEM button
                        self.controller.state = BattleState.PLAYER_ITEM_SELECT
                        item_list_full_layout = battle_widgets.ItemSelect(self.controller.items)
                        item_list_interactive_layout = item_list_full_layout.children[0]
                        self.controller.focus_stack.push(item_list_full_layout, item_list_interactive_layout,
                                                         self.controller.state, 2, True)
                        self.controller.focus_stack.get_highest_member().full_ui_layout.update_item_data(
                            self.controller.focus_stack.get_highest_member().get_focused_widget().item
                        )
                        return
                    case 3:  # user selects the SPARE button
                        self.controller.state = BattleState.PLAYER_SPARE_SELECT
                        self.controller.open_enemy_select_menu()
                        return
                    case 4:  # user selects the DEFEND button
                        defending_player_character = self.controller.focus_stack.get_highest_member().get_interactive_ui_layout().player_character
                        defend_action = DefendAction(
                            actor = defending_player_character,
                            targets=[],
                            controller=self.controller
                        )
                        self.controller.move_to_next_player_card(defend_action)
                        return

            case BattleState.PLAYER_ATTACK_SELECT:
                selected_target_enemy = self.controller.focus_stack.get_highest_member().get_focused_widget().enemy
                selected_target_enemy.unfocus()

                self.controller.focus_stack.pop(remove_widget=True)

                current_player_character = self.controller.focus_stack.get_highest_member().get_interactive_ui_layout().player_character

                self.controller.battle_player_character_cards.children[
                    self.controller.current_player_index].change_icon(
                    "assets/textures/gui_graphics/action_icons/fight_icon.png")

                fight_action = FightAction(
                    actor=current_player_character,
                    target=selected_target_enemy,
                    controller=self.controller
                )

                self.controller.move_to_next_player_card(fight_action)
                return

            case BattleState.PLAYER_ACT_ENEMY_SELECT:
                self.controller.state = BattleState.PLAYER_ACT_SELECT
                act_list_full_layout = battle_widgets.ActSelect(
                    self.controller.focus_stack.get_highest_member().get_focused_widget().enemy,
                    self.controller)
                act_list_interactive_layout = act_list_full_layout.children[0]
                self.controller.focus_stack.push(act_list_full_layout, act_list_interactive_layout,
                                                 self.controller.state, 2, True)
                self.controller.menu_select_sound.play()
                self.controller.focus_stack.get_highest_member().full_ui_layout.update_act_data(
                    self.controller.focus_stack.get_highest_member().get_focused_widget().act
                )
                return

            case BattleState.PLAYER_ACT_SELECT:
                selected_act = self.controller.focus_stack.get_highest_member().get_focused_widget().act
                self.controller.focus_stack.pop(remove_widget=True)
                selected_target_enemy = self.controller.focus_stack.get_highest_member().get_focused_widget().enemy
                selected_target_enemy.unfocus()
                self.controller.focus_stack.pop(remove_widget=True)
                current_player_character = self.controller.focus_stack.get_highest_member().get_interactive_ui_layout().player_character

                act_action = ActAction(
                    actor=current_player_character,
                    target=selected_target_enemy,
                    act=selected_act,
                    controller=self.controller
                )

                self.controller.move_to_next_player_card(act_action)

                return

            case BattleState.PLAYER_MAGIC_SELECT:
                if hasattr(self.controller.focus_stack.get_highest_member().get_focused_widget(), "spell"):
                    spell_or_act = self.controller.focus_stack.get_highest_member().get_focused_widget().spell
                else:
                    spell_or_act = self.controller.focus_stack.get_highest_member().get_focused_widget().act
                if spell_or_act.tp_cost <= self.controller.tp_meter.get_tp_in_meter():
                    self.controller.state = BattleState.PLAYER_MAGIC_ENEMY_SELECT
                    self.controller.tp_meter.update_tp_meter(-spell_or_act.tp_cost)
                    self.controller.open_enemy_select_menu()
                    self.controller.menu_select_sound.play()
                return

            case BattleState.PLAYER_MAGIC_ENEMY_SELECT:
                selected_target_enemy = self.controller.focus_stack.get_highest_member().get_focused_widget().enemy
                selected_target_enemy.unfocus()
                self.controller.focus_stack.pop(remove_widget=True)
                is_spell = hasattr(self.controller.focus_stack.get_highest_member().get_focused_widget(), "spell")
                if is_spell:
                    selected_spell_or_act = self.controller.focus_stack.get_highest_member().get_focused_widget().spell
                else:
                    selected_spell_or_act = self.controller.focus_stack.get_highest_member().get_focused_widget().act
                self.controller.focus_stack.pop(remove_widget=True)
                current_player_character = self.controller.focus_stack.get_highest_member().get_interactive_ui_layout().player_character

                if is_spell:
                    spell_or_act_action = SpellAction(
                        actor=current_player_character,
                        targets=[selected_target_enemy],
                        spell=selected_spell_or_act,
                        controller=self.controller
                    )
                else:
                    spell_or_act_action = ActAction(
                        actor=current_player_character,
                        target=selected_target_enemy,
                        act=selected_spell_or_act,
                        controller=self.controller
                    )

                self.controller.move_to_next_player_card(spell_or_act_action)
                return

            case BattleState.PLAYER_ITEM_SELECT:
                item = self.controller.focus_stack.get_highest_member().get_focused_widget().item
                item_index = self.controller.focus_stack.get_highest_member().get_focused_widget_index()
                if item.tp_restored > 0 and item.hp_restored == 0:  # If item is TP item exclusively
                    self.controller.focus_stack.pop(remove_widget=True)
                    current_player_character = self.controller.focus_stack.get_highest_member().get_interactive_ui_layout().player_character
                    item_action = ItemAction(
                        actor=current_player_character,
                        targets=[],
                        controller=self.controller,
                        item=item,
                        item_index=item_index
                    )
                    self.controller.move_to_next_player_card(item_action)
                    return
                if item.heals_all_party_members:  # If item affects all party members
                    # TODO: queue an ItemAction with the item
                    self.controller.focus_stack.pop(remove_widget=True)
                    current_player_character = self.controller.focus_stack.get_highest_member().get_interactive_ui_layout().player_character
                    item_action = ItemAction(
                        actor=current_player_character,
                        targets=self.controller.players,
                        controller=self.controller,
                        item=item,
                        item_index=item_index
                    )
                    self.controller.move_to_next_player_card(item_action)
                    return
                self.controller.state = BattleState.PLAYER_ITEM_PLAYER_SELECT
                self.controller.open_player_select_menu()
                self.controller.menu_select_sound.play()
                return

            case BattleState.PLAYER_ITEM_PLAYER_SELECT:
                targeted_player_character = self.controller.focus_stack.get_highest_member().get_focused_widget().player
                targeted_player_character.unfocus()
                self.controller.focus_stack.pop(remove_widget=True)
                item = self.controller.focus_stack.get_highest_member().get_focused_widget().item
                item_index = self.controller.focus_stack.get_highest_member().get_focused_widget_index()
                self.controller.focus_stack.pop(remove_widget=True)
                player_using_item = self.controller.focus_stack.get_highest_member().get_interactive_ui_layout().player_character
                item_action = ItemAction(
                    actor=player_using_item,
                    targets=[targeted_player_character],
                    controller=self.controller,
                    item=item,
                    item_index=item_index
                )
                self.controller.move_to_next_player_card(item_action)
                self.controller.menu_select_sound.play()


            case BattleState.PLAYER_SPARE_SELECT:
                # animate the player character, queue the act
                selected_target_enemy = self.controller.focus_stack.get_highest_member().get_focused_widget().enemy
                selected_target_enemy.unfocus()

                self.controller.focus_stack.pop(remove_widget=True)

                current_player_character = self.controller.focus_stack.get_highest_member().get_interactive_ui_layout().player_character

                self.controller.battle_player_character_cards.children[
                    self.controller.current_player_index].change_icon(
                    "assets/textures/gui_graphics/action_icons/spare_icon.png")

                spare_action = SpareAction(
                    actor=current_player_character,
                    target=selected_target_enemy,
                    controller=self.controller
                )

                self.controller.move_to_next_player_card(spare_action)
                return

            case BattleState.PLAYER_ATTACKING:
                self.controller.attempt_to_hit_enemy()

            case BattleState.EXECUTING_QUEUED_PLAYER_COMMANDS:
                self.controller.execute_queued_player_action()

            case BattleState.DIALOGUE:
                self.controller.spawn_next_dialog_from_dialog_exchange()


class CancelCommand(Command):
    """ A command object representing the user canceling (usually pressing X in the original game.) """

    def execute(self):
        match self.controller.state:
            case BattleState.PLAYER_COMMAND:
                self.controller.move_to_previous_player_card()
                previous_player = self.controller.focus_stack.get_highest_member().get_interactive_ui_layout().player_character
                previous_player.set_animation_state("battle_idle")
            case BattleState.PLAYER_MAGIC_SELECT:
                self.backup_out_of_focus_stack()
            case BattleState.PLAYER_MAGIC_ENEMY_SELECT:
                focused_enemy = self.controller.focus_stack.get_highest_member().get_focused_widget().enemy
                focused_enemy.unfocus()
                self.backup_out_of_focus_stack()
            case BattleState.PLAYER_ATTACK_SELECT:
                focused_enemy = self.controller.focus_stack.get_highest_member().get_focused_widget().enemy
                focused_enemy.unfocus()
                self.backup_out_of_focus_stack()
            case BattleState.PLAYER_SPARE_SELECT:
                focused_enemy = self.controller.focus_stack.get_highest_member().get_focused_widget().enemy
                focused_enemy.unfocus()
                self.backup_out_of_focus_stack()
            case BattleState.PLAYER_ITEM_SELECT:
                self.backup_out_of_focus_stack()
            case BattleState.PLAYER_ITEM_PLAYER_SELECT:
                focused_player = self.controller.focus_stack.get_highest_member().get_focused_widget().player
                focused_player.unfocus()
                self.backup_out_of_focus_stack()
            case BattleState.PLAYER_ACT_ENEMY_SELECT:
                focused_enemy = self.controller.focus_stack.get_highest_member().get_focused_widget().enemy
                focused_enemy.unfocus()
                self.backup_out_of_focus_stack()
            case BattleState.PLAYER_ACT_SELECT:
                self.backup_out_of_focus_stack()

    def backup_out_of_focus_stack(self):
        """
        Used to back out of loaded battle UI elements while updating self.controller.state and the focus stack.
        Used a lot in CancelCommand.execute().
        :return: None
        """
        focus_stack_member = self.controller.focus_stack.pop(remove_widget=True)
        if focus_stack_member:
            self.controller.state = self.controller.focus_stack.get_highest_member().state
        self.controller.menu_move_sound.play()


class RightCommand(Command):
    """ A command object representing the user pressing right (usually pressing -> in the original game.) """

    def execute(self):
        # States that are in the Battle GUI
        if self.controller.state in [BattleState.PLAYER_COMMAND, BattleState.PLAYER_MAGIC_SELECT,
                                     BattleState.PLAYER_ITEM_SELECT, BattleState.PLAYER_ACT_SELECT]:
            if self.controller.state == BattleState.PLAYER_COMMAND:
                move_succeeded = self.controller.focus_stack.get_highest_member().move_right(wrap=True)
            else:
                move_succeeded = self.controller.focus_stack.get_highest_member().move_right()
            if move_succeeded:
                self.controller.menu_move_sound.play()
                match self.controller.state:
                    case BattleState.PLAYER_MAGIC_SELECT:
                        if hasattr(self.controller.focus_stack.get_highest_member().get_focused_widget(), "spell"):
                            self.controller.focus_stack.get_highest_member().full_ui_layout.update_spell_data(
                                self.controller.focus_stack.get_highest_member().get_focused_widget().spell
                            )
                        else:
                            self.controller.focus_stack.get_highest_member().full_ui_layout.update_act_data(
                                self.controller.focus_stack.get_highest_member().get_focused_widget().act
                            )
                    case BattleState.PLAYER_ITEM_SELECT:
                        self.controller.focus_stack.get_highest_member().full_ui_layout.update_item_data(
                            self.controller.focus_stack.get_highest_member().get_focused_widget().item
                        )
                    case BattleState.PLAYER_ACT_SELECT:
                        self.controller.focus_stack.get_highest_member().full_ui_layout.update_act_data(
                            self.controller.focus_stack.get_highest_member().get_focused_widget().act
                        )


class LeftCommand(Command):
    """ A command object representing the user pressing left (usually pressing <- in the original game.) """

    def execute(self):
        # States that are in the Battle GUI
        if self.controller.state in [BattleState.PLAYER_COMMAND, BattleState.PLAYER_MAGIC_SELECT,
                                     BattleState.PLAYER_ITEM_SELECT, BattleState.PLAYER_ACT_SELECT]:
            if self.controller.state == BattleState.PLAYER_COMMAND:
                move_succeeded = self.controller.focus_stack.get_highest_member().move_left(wrap=True)
            else:
                move_succeeded = self.controller.focus_stack.get_highest_member().move_left()
            if move_succeeded:
                self.controller.menu_move_sound.play()
                match self.controller.state:
                    case BattleState.PLAYER_MAGIC_SELECT:
                        if hasattr(self.controller.focus_stack.get_highest_member().get_focused_widget(), "spell"):
                            self.controller.focus_stack.get_highest_member().full_ui_layout.update_spell_data(
                                self.controller.focus_stack.get_highest_member().get_focused_widget().spell
                            )
                        else:
                            self.controller.focus_stack.get_highest_member().full_ui_layout.update_act_data(
                                self.controller.focus_stack.get_highest_member().get_focused_widget().act
                            )
                    case BattleState.PLAYER_ITEM_SELECT:
                        self.controller.focus_stack.get_highest_member().full_ui_layout.update_item_data(
                            self.controller.focus_stack.get_highest_member().get_focused_widget().item
                        )
                    case BattleState.PLAYER_ACT_SELECT:
                        self.controller.focus_stack.get_highest_member().full_ui_layout.update_act_data(
                            self.controller.focus_stack.get_highest_member().get_focused_widget().act
                        )

class UpCommand(Command):
    """ A command object representing the user pressing up (usually pressing the up arrow key in the original game.) """

    def attempt_to_move_up_in_ui(self):
        """
        Attempt to move focus up in a widget container.
        :return: The newly focused widget above the previously focused widget.
        """
        previously_focused_widget = self.controller.focus_stack.get_highest_member().get_focused_widget()
        if self.controller.focus_stack.get_highest_member().move_up():
            currently_focused_widget = self.controller.focus_stack.get_highest_member().get_focused_widget()
            self.controller.menu_move_sound.play()
            return previously_focused_widget, currently_focused_widget
        return None

    def execute(self):
        match self.controller.state:
            case BattleState.PLAYER_MAGIC_ENEMY_SELECT | BattleState.PLAYER_ATTACK_SELECT | \
                 BattleState.PLAYER_SPARE_SELECT | BattleState.PLAYER_ACT_ENEMY_SELECT:
                previously_focused_widget, currently_focused_widget = self.attempt_to_move_up_in_ui()
                self.controller.move_focus_between_enemies_in_enemy_select(
                    previously_focused_widget,
                    currently_focused_widget
                )
            case BattleState.PLAYER_ITEM_PLAYER_SELECT:
                previously_focused_widget, currently_focused_widget = self.attempt_to_move_up_in_ui()

                self.controller.move_focus_between_players_in_player_select(
                    previously_focused_widget,
                    currently_focused_widget
                )
            case BattleState.PLAYER_MAGIC_SELECT:
                self.attempt_to_move_up_in_ui()
                if hasattr(self.controller.focus_stack.get_highest_member().get_focused_widget(), "spell"):
                    self.controller.focus_stack.get_highest_member().full_ui_layout.update_spell_data(
                        self.controller.focus_stack.get_highest_member().get_focused_widget().spell
                    )
                else:
                    self.controller.focus_stack.get_highest_member().full_ui_layout.update_act_data(
                        self.controller.focus_stack.get_highest_member().get_focused_widget().act
                    )
            case BattleState.PLAYER_ITEM_SELECT:
                self.attempt_to_move_up_in_ui()
                self.controller.focus_stack.get_highest_member().full_ui_layout.update_item_data(
                    self.controller.focus_stack.get_highest_member().get_focused_widget().item
                )

            case BattleState.PLAYER_ACT_SELECT:
                self.attempt_to_move_up_in_ui()
                self.controller.focus_stack.get_highest_member().full_ui_layout.update_act_data(
                    self.controller.focus_stack.get_highest_member().get_focused_widget().act
                )


class DownCommand(Command):
    """
    A command object representing the user pressing down
    (usually pressing the down arrow key in the original game.)
    """

    def attempt_to_move_down_in_ui(self):
        """
        Attempt to move focus down in a widget container.
        """
        previously_focused_widget = self.controller.focus_stack.get_highest_member().get_focused_widget()
        if self.controller.focus_stack.get_highest_member().move_down():
            currently_focused_widget = self.controller.focus_stack.get_highest_member().get_focused_widget()
            self.controller.menu_move_sound.play()
            return previously_focused_widget, currently_focused_widget
        return None

    def execute(self):
        match self.controller.state:
            case BattleState.PLAYER_MAGIC_ENEMY_SELECT | BattleState.PLAYER_ATTACK_SELECT | \
                 BattleState.PLAYER_SPARE_SELECT | BattleState.PLAYER_ACT_ENEMY_SELECT:
                previously_focused_widget, currently_focused_widget = self.attempt_to_move_down_in_ui()
                self.controller.move_focus_between_enemies_in_enemy_select(
                    previously_focused_widget,
                    currently_focused_widget
                )
            case BattleState.PLAYER_ITEM_PLAYER_SELECT:
                previously_focused_widget, currently_focused_widget = self.attempt_to_move_down_in_ui()
                self.controller.move_focus_between_players_in_player_select(
                    previously_focused_widget,
                    currently_focused_widget
                )
            case BattleState.PLAYER_MAGIC_SELECT:
                self.attempt_to_move_down_in_ui()
                if hasattr(self.controller.focus_stack.get_highest_member().get_focused_widget(), "spell"):
                    self.controller.focus_stack.get_highest_member().full_ui_layout.update_spell_data(
                        self.controller.focus_stack.get_highest_member().get_focused_widget().spell
                    )
                else:
                    self.controller.focus_stack.get_highest_member().full_ui_layout.update_act_data(
                        self.controller.focus_stack.get_highest_member().get_focused_widget().act
                    )
            case BattleState.PLAYER_ITEM_SELECT:
                self.attempt_to_move_down_in_ui()
                self.controller.focus_stack.get_highest_member().full_ui_layout.update_item_data(
                    self.controller.focus_stack.get_highest_member().get_focused_widget().item
                )
            case BattleState.PLAYER_ACT_SELECT:
                self.attempt_to_move_down_in_ui()
                self.controller.focus_stack.get_highest_member().full_ui_layout.update_act_data(
                    self.controller.focus_stack.get_highest_member().get_focused_widget().act
                )

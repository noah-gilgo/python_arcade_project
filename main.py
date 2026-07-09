import arcade
import pyglet
from arcade import SpriteList, Window
from arcade.gui import UIManager
from arcade.types import Color

import math_methods
import music_player
import non_player_character
import player_character
import player_characters
import settings
import sound_methods
import graphics_methods
import dialogue_box
import battle_widgets
from animations.background_animations import DepthsBackgroundAnimation
from battle_state_machine import BattleController
import items.armor_items
from bullet_board import BulletBoard
from items import armor_items
from items.armor_items import PrincessRbn, TennaTie, ShadowMantle, Jevilstail, WhiteRibbon, WaferGuard, RoyalPin, \
    MysticBand
from items.weapon_items import JingleBlade, JusticeAxe, ScarfMark, SnowRing
from soul import Soul
from spells import Spell, IceShock
from sprites_and_effects_collection import SpritesAndEffectsCollection


class GameView(arcade.View):
    def __init__(self):
        # Call the parent class initializer
        super().__init__()

        # Captures the game window's width and height when the game is initialized. This is done to dynamically
        # calculate a global "SCALE" variable to set the camera zoom when changing to full screen.
        self._initial_width = self.width
        self._initial_height = self.height

        # Setup camera stuff
        self.camera = arcade.Camera2D()

        # Set up the player info
        self.player_one = None
        self.player_two = None
        self.player_three = None
        self.player_four = None

        self.player_characters = []

        self.enemy_one = None
        self.enemy_two = None
        self.enemy_three = None

        self.enemies = []

        # Set the background color
        self.background_color = arcade.color.BLACK

        self.background_music = None
        self.background_music_player = None

        # Temporary, for testing player animations.
        self._global_timer = 0.0
        self._animation_states = []
        self._animation_state_index = 0

        # Load the fonts used by the game.
        arcade.load_font("assets/fonts/8bitoperator_jve.ttf")
        arcade.load_font("assets/fonts/3x5-font.ttf")
        arcade.load_font("assets/fonts/roarin.ttf")
        arcade.load_font("assets/fonts/greater-determination-dr-damage.ttf")
        arcade.load_font("assets/fonts/dotumche-pixel.ttf")
        arcade.load_font("assets/fonts/undertale-deltarune-extended-fixed.ttf")

        """
        from fontTools.ttLib import TTFont

        font = TTFont("assets/fonts/undertale-deltarune-extended-fixed.ttf")

        for record in font["name"].names:
            if record.nameID == 1:
                print(record.toUnicode())
        """

        # Initialize the UIManager.
        self.manager = UIManager()
        self.manager._pixelated = True
        self.manager.enable()
        self.text_box = None
        self.battle_hud_container = None
        self.battle_player_character_cards = None

        # Holds all main sprite lists used by the system
        self.sprites_and_effects_collection = SpritesAndEffectsCollection(self.camera, self.manager)

        self._dialog = [
            dialogue_box.TextBoxDialog(
                portrait_texture_path="assets/sprites/player_characters/susie/dialog_portraits/susie_happy_blush_grin.png",
                text="* Heck yeah Kris, we're in Fortnite",
                rate_of_text=0.03,
                text_sound_path="assets/audio/dialog/snd_txtsus.wav"
            ),
            dialogue_box.TextBoxDialog(
                portrait_texture_path="assets/sprites/player_characters/ralsei/dialog_portraits/ralsei_hat_shocked.png",
                text="* Wait a minute, how did I get my Chapter 1 clothes?",
                rate_of_text=0.03,
                text_sound_path="assets/audio/dialog/snd_txtral.wav"
            ),
            dialogue_box.TextBoxDialog(
                portrait_texture_path="assets/sprites/player_characters/noelle/dialog_portraits/noelle_pissed.png",
                text="* ...my health meter...",
                rate_of_text=0.06,
                text_sound_path="assets/audio/dialog/snd_txtnoe.wav"
            ),
            dialogue_box.TextBoxDialog(
                portrait_texture_path="assets/sprites/player_characters/noelle/dialog_portraits/noelle_very_pissed.png",
                text="* ...isn't on the screen...",
                rate_of_text=0.06,
                text_sound_path="assets/audio/dialog/snd_txtnoe.wav"
            ),
            dialogue_box.TextBoxDialog(
                portrait_texture_path="assets/sprites/player_characters/ralsei/dialog_portraits/ralsei_normal.png",
                text="* Do you have anything to say about all of this, Kris..?",
                rate_of_text=0.03,
                text_sound_path="assets/audio/dialog/snd_txtral.wav"
            ),
            dialogue_box.TextBoxDialog(
                portrait_texture_path="assets/sprites/player_characters/kris/default/kris-standing.png",
                text="  "
            ),
            dialogue_box.TextBoxDialog(
                portrait_texture_path="assets/sprites/player_characters/susie/dialog_portraits/susie_trying_not_to_laugh.png",
                text="* Alright, fine, keep your secrets.",
                rate_of_text=0.03,
                text_sound_path="assets/audio/dialog/snd_txtsus.wav"
            )
        ]

        self._dialog_box_index = 0

        self.battle_controller = None

        self.bullet_board = None

        self.soul = None

        self.music_player = None

        # Initializes the starting positions of the player characters and enemy characters.
        self._holy_arc = math_methods.initialize_holy_arc(3)
        self._unholy_arc = math_methods.initialize_unholy_arc(3)

        self.background_animation = None

    def setup(self):
        # The bullet board used during the enemy attack.
        self.bullet_board = BulletBoard()

        # Create and append the players to the SpriteList.

        self.player_one = player_characters.Kris()
        self.player_one.set_sprites_and_effects_collection(self.sprites_and_effects_collection)
        self.player_one.center_x = self._holy_arc[0][0]
        self.player_one.center_y = self._holy_arc[0][1]

        self.player_one.equip_weapon(JingleBlade())
        self.player_one.equip_armor_to_slot_1(PrincessRbn())
        self.player_one.equip_armor_to_slot_2(TennaTie())
        self.player_characters.append(self.player_one)

        self._animation_states = self.player_one.get_valid_animation_states()


        self.player_two = player_characters.Susie()
        self.player_two.set_sprites_and_effects_collection(self.sprites_and_effects_collection)
        self.player_two.center_x = self._holy_arc[1][0]
        self.player_two.center_y = self._holy_arc[1][1]
        
        self.player_two.equip_weapon(JusticeAxe())
        self.player_two.equip_armor_to_slot_1(ShadowMantle())
        self.player_two.equip_armor_to_slot_2(MysticBand())
        self.player_characters.append(self.player_two)


        self.player_three = player_characters.Ralsei()
        self.player_three.set_sprites_and_effects_collection(self.sprites_and_effects_collection)
        self.player_three.center_x = self._holy_arc[2][0]
        self.player_three.center_y = self._holy_arc[2][1]

        self.player_three.equip_weapon(ScarfMark())
        self.player_three.equip_armor_to_slot_1(Jevilstail())
        self.player_three.equip_armor_to_slot_2(WaferGuard())
        self.player_characters.append(self.player_three)

        """
        self.player_four = player_characters.Noelle()
        self.player_four.set_sprites_and_effects_collection(self.sprites_and_effects_collection)
        self.player_four.center_x = self._holy_arc[2][0]
        self.player_four.center_y = self._holy_arc[2][1]

        self.player_four.equip_weapon(SnowRing())
        self.player_four.equip_armor_to_slot_1(RoyalPin())
        self.player_four.equip_armor_to_slot_2(WhiteRibbon())
        self.player_characters.append(self.player_four)

        self.player_four.get_valid_animation_states()
        """


        # Create and append the enemies to the SpriteList.
        self.enemy_one = non_player_character.Rudinn(
            sprites_and_effects_collection=self.sprites_and_effects_collection,
            center_x=self._unholy_arc[0][0],
            center_y=self._unholy_arc[0][1],
            enemies_list=self.enemies,
            bullet_board=self.bullet_board
        )
        self.enemies.append(self.enemy_one)

        self.enemy_two = non_player_character.Rudinn(
            sprites_and_effects_collection=self.sprites_and_effects_collection,
            center_x=self._unholy_arc[1][0],
            center_y=self._unholy_arc[1][1],
            enemies_list=self.enemies,
            bullet_board=self.bullet_board
        )
        self.enemies.append(self.enemy_two)

        self.enemy_three = non_player_character.Rudinn(
            sprites_and_effects_collection=self.sprites_and_effects_collection,
            center_x=self._unholy_arc[2][0],
            center_y=self._unholy_arc[2][1],
            enemies_list=self.enemies,
            bullet_board=self.bullet_board
        )
        self.enemies.append(self.enemy_three)

        # for enemy in self.enemies:
        #    enemy.spawn_speech_bubble(enemy.random_speech_bubble_dialogue[0])

        # Start the background music.
        self.music_player = music_player.MusicPlayer()
        self.music_player.play_sound(
            sound_name="another_him",
            pitch=0.0,
            volume=0.3
        )

        sound_methods.gradually_update_pitch(self.music_player.currently_playing_song_player, 1.0, 0.02, 0.05)

        # Animate the background of the GONERMAKER.
        # graphics_methods.animate_depths(self.sprites_and_effects_collection.background_sprites)
        self.background_animation = DepthsBackgroundAnimation(self.sprites_and_effects_collection)
        self.sprites_and_effects_collection.effects.append(self.background_animation)

        # Initialize the GUI.
        self.text_box = dialogue_box.BattleDialogTextBox(self.sprites_and_effects_collection)
        self.battle_player_character_cards = battle_widgets.BattleHUDCharacterClamshellDisplay(self.player_characters, self.sprites_and_effects_collection)
        self.manager.add(self.battle_player_character_cards)
        #self.manager.add(self.tp_meter)
        #self.manager.add(self.text_box)

        self.battle_controller = BattleController(
            ui_manager=self.manager,
            battle_player_character_cards=self.battle_player_character_cards,
            battle_textbox=self.text_box,
            players=self.player_characters,
            enemies=self.enemies,
            sprites_and_effects_collection=self.sprites_and_effects_collection,
            bullet_board=self.bullet_board,
            music_player=self.music_player,
            game_view=self
        )

    def on_draw(self):
        # 3. Clear the screen
        self.clear()

        self.sprites_and_effects_collection.draw()

    def on_resize(self, width, height):
        super().on_resize(width, height)

        settings.WINDOW_WIDTH = width
        settings.WINDOW_HEIGHT = height

        self.camera.match_window()
        self.manager.trigger_render()

    def on_update(self, delta_time):
        """ Movement and game logic """

        self.battle_controller.update_sprites_and_effects(delta_time)

    def on_key_press(self, key, modifiers):
        """Called whenever a key is pressed. """

        if key == arcade.key.F11:
            self.window.set_fullscreen(not self.window.fullscreen)
            settings.WINDOW_SCALE = self.height / self._initial_height
            self.camera.zoom = settings.WINDOW_SCALE
            # self.manager.trigger_render()
            # self.manager.execute_layout()

        self.battle_controller.add_key_pressed(key)
        self.battle_controller.handle_key(key)

    def on_key_release(self, key, modifiers):
        self.battle_controller.remove_key_pressed(key)


def main():
    # Create a window class. This is what actually shows up on screen
    window = arcade.Window(settings.WINDOW_WIDTH, settings.WINDOW_HEIGHT, settings.WINDOW_TITLE)
    window.set_update_rate(settings.FRAMERATE)

    # Create and setup the GameView
    game = GameView()
    game.setup()

    # Show GameView on screen
    window.show_view(game)

    # Start the arcade game loop
    arcade.run()


if __name__ == "__main__":
    main()

import arcade
from arcade.gui import UIManager
from arcade.resources import resolve_resource_path
from arcade.types import Color

import math_methods
import non_player_character
import player_character
import settings
import character
import pyglet
import sound_methods
import graphics_methods
import math
import dialogue_box
import character_options_widget
from battle_state_machine import BattleController
from spell_animations import IceShockAnimation


class GameView(arcade.View):
    def __init__(self):
        # Call the parent class initializer
        super().__init__()

        # Captures the game window's width and height when the game is initialized. This is done to dynamically
        # calculate a global "SCALE" variable to set the camera zoom when changing to full screen.
        self._initial_width = self.width
        self._initial_height = self.height

        # Variables that will hold sprite lists
        self.background_sprites = arcade.SpriteList()
        self.player_sprites = arcade.SpriteList()
        self.foreground_sprites = arcade.SpriteList()
        self.spell_sprites = arcade.SpriteList()

        # Set up the player info
        self.player_one = None
        self.player_two = None
        self.player_three = None
        self.player_four = None

        self.players = []

        self.enemy_one = None

        self.enemies = []

        # Set the background color
        self.background_color = arcade.color.BLACK

        self.background_music = None
        self.background_music_player = None

        # Setup camera stuff
        self.camera = arcade.Camera2D()

        # Initializes the starting positions of the player characters and enemy characters.
        self._holy_arc = math_methods.initialize_holy_arc(3)
        self._unholy_arc = math_methods.initialize_unholy_arc(1)

        # Temporary, for testing player animations.
        self._global_timer = 0.0
        self._animation_states = []
        self._animation_state_index = 0

        # Load the fonts used by the game.
        arcade.load_font("assets/fonts/8bitoperator_jve.ttf")
        arcade.load_font("assets/fonts/3x5-font.ttf")
        arcade.load_font("assets/fonts/roarin.ttf")

        # Initialize the UIManager.
        self.manager = UIManager()
        self.manager._pixelated = True
        self.manager.enable()
        self.text_box = None
        self.battle_hud_container = None

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

        self.iceshock_animation = None

    def setup(self):
        # Create and append the players to the SpriteList.
        self.player_one = player_character.PlayerCharacter(scale=4.0,
                                                           center_x=self._holy_arc[0][0],
                                                           center_y=self._holy_arc[0][1],
                                                           angle=0,
                                                           sprite_folder_name="kris",
                                                           name="Kris",
                                                           max_hp=90,
                                                           attack=10,
                                                           defense=2,
                                                           magic=0,
                                                           battle_ui_color=Color(0, 255, 255, 255),
                                                           knows_magic=False)
        self.player_one.set_animation_state("battle_idle")
        self.player_sprites.append(self.player_one)  # Append the instance to the SpriteList
        self.players.append(self.player_one)

        self._animation_states = self.player_one.get_valid_animation_states()

        self.player_two = player_character.PlayerCharacter(scale=4.0,
                                                           center_x=self._holy_arc[1][0],
                                                           center_y=self._holy_arc[1][1],
                                                           angle=0,
                                                           sprite_folder_name="susie",
                                                           name="Susie",
                                                           max_hp=110,
                                                           attack=14,
                                                           defense=2,
                                                           magic=1,
                                                           battle_ui_color=Color(255, 0, 255, 255))  # Sprite initialization
        self.player_two.set_animation_state("battle_idle")
        self.player_sprites.append(self.player_two)  # Append the instance to the SpriteList
        self.players.append(self.player_two)

        """
        self.player_three = player_character.PlayerCharacter(scale=4.0,
                                                             center_x=self._holy_arc[2][0],
                                                             center_y=self._holy_arc[2][1],
                                                             angle=0,
                                                             sprite_folder_name="ralsei",
                                                             name="ralsei",
                                                             max_hp=70,
                                                             attack=8,
                                                             defense=2,
                                                             magic=7,
                                                             battle_ui_color=Color(0, 255, 0, 255))  # Sprite initialization
        self.player_three.set_animation_state("battle_idle")
        self.player_sprites.append(self.player_three)  # Append the instance to the SpriteList
        self.players.append(self.player_three)
        """

        self.player_four = player_character.PlayerCharacter(scale=4.0,
                                                            center_x=self._holy_arc[2][0],
                                                            center_y=self._holy_arc[2][1],
                                                            angle=0,
                                                            sprite_folder_name="noelle",
                                                            name="Noelle",
                                                            max_hp=90,
                                                            attack=10,
                                                            defense=2,
                                                            magic=0,
                                                            battle_ui_color=Color(255, 255, 0, 255))  # Sprite initialization
        self.player_four.set_animation_state("battle_idle")
        self.player_sprites.append(self.player_four)  # Append the instance to the SpriteList
        self.players.append(self.player_four)


        # Create and append the players to the SpriteList.
        self.enemy_one = non_player_character.NonPlayerCharacter(scale=4.0,
                                                                 center_x=self._unholy_arc[0][0],
                                                                 center_y=self._unholy_arc[0][1],
                                                                 angle=0,
                                                                 sprite_folder_name="rudinn",
                                                                 name="Rudinn",
                                                                 max_hp=90,
                                                                 attack=10,
                                                                 defense=2
                                                                 )
        self.enemy_one.set_animation_state("battle_idle")
        self.player_sprites.append(self.enemy_one)  # Append the instance to the SpriteList
        self.enemies.append(self.enemy_one)

        # self._animation_states = self.enemy_one.get_valid_animation_states()

        # Start the background music.
        self.background_music = arcade.load_sound("assets/audio/songs/ANOTHER_HIM.wav", True)
        self.background_music_player = self.background_music.play()
        self.background_music_player.pitch = 0.0
        self.background_music_player.loop = True

        sound_methods.gradually_update_pitch(self.background_music_player, 1.0, 0.02, 0.05)

        # Animate the background of the GONERMAKER.
        graphics_methods.animate_depths(self.background_sprites)

        # Initialize the GUI.
        self.text_box = dialogue_box.TextBox()
        self.manager.add(self.text_box)

        self.battle_hud_container = character_options_widget.BattleHUDCharacterClamshellDisplay(self.players)
        self.manager.add(self.battle_hud_container)

        self.battle_controller = BattleController(self.text_box, self.battle_hud_container)

        self.iceshock_animation = IceShockAnimation(self.enemy_one.center_x, self.enemy_one.center_y)
        for sprite in self.iceshock_animation.sprites:
            self.spell_sprites.append(sprite.sprite)

    def on_draw(self):
        # 3. Clear the screen
        self.clear()

        # Draw in layer order (background -> player -> foreground)
        with self.camera.activate():
            self.background_sprites.draw(pixelated=True)
            self.player_sprites.draw(pixelated=True)
            self.foreground_sprites.draw(pixelated=True)
            self.spell_sprites.draw(pixelated=True)
            self.manager.draw(pixelated=True)
            self.iceshock_animation.draw()

    def on_resize(self, width, height):
        super().on_resize(width, height)
        self.camera.match_window()

    def on_update(self, delta_time):
        """ Movement and game logic """

        # Update the player's animation.
        for player in self.players:
            player.update_animation(delta_time)

        for enemy in self.enemies:
            enemy.update_animation(delta_time)

        # Used for testing the animation system

        if self._global_timer > 2.0:
            if self._animation_state_index < len(self._animation_states):
                for player in self.players:
                    player.set_animation_state(self._animation_states[self._animation_state_index])
                self._animation_state_index += 1
            self._global_timer = 0.0

        self._global_timer += delta_time

        self.iceshock_animation.update()

    def on_key_press(self, key, modifiers):
        """Called whenever a key is pressed. """

        if key == arcade.key.F11:
            self.window.set_fullscreen(not self.window.fullscreen)
            settings.WINDOW_SCALE = math.sqrt((self.width / self._initial_width) * (self.height / self._initial_height))
            self.camera.zoom = settings.WINDOW_SCALE

        self.battle_controller.handle_key(key)

        """
        if key == arcade.key.UP:
            self.up_pressed = True
            self.update_player_speed()
        elif key == arcade.key.DOWN:
            self.down_pressed = True
            self.update_player_speed()
        elif key == arcade.key.LEFT:
            self.left_pressed = True
            self.update_player_speed()
        elif key == arcade.key.RIGHT:
            self.right_pressed = True
            self.update_player_speed()
        """

        # if key == arcade.key.RIGHT:

        """
        if key == arcade.key.Z:
            self._text_box.load_dialog(self._dialog[self._dialog_box_index])
            if self._dialog_box_index < len(self._dialog) - 1:
                self._dialog_box_index += 1
            else:
                self._dialog_box_index = 0
        """

    """
    def on_key_release(self, key, modifiers):
        # Called when the user releases a key.

        if key == arcade.key.UP:
            self.up_pressed = False
            self.update_player_speed()
        elif key == arcade.key.DOWN:
            self.down_pressed = False
            self.update_player_speed()
        elif key == arcade.key.LEFT:
            self.left_pressed = False
            self.update_player_speed()
        elif key == arcade.key.RIGHT:
            self.right_pressed = False
            self.update_player_speed()
    """


def main():
    # Create a window class. This is what actually shows up on screen
    window = arcade.Window(settings.WINDOW_WIDTH, settings.WINDOW_HEIGHT, settings.WINDOW_TITLE)

    # Create and setup the GameView
    game = GameView()
    game.setup()

    # Show GameView on screen
    window.show_view(game)

    # Start the arcade game loop
    arcade.run()


if __name__ == "__main__":
    main()

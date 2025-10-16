import arcade
import settings
import player
import pyglet
import sound_methods
import graphics_methods
import math


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

        # Set up the player info
        self.player_one = None

        # Track the current state of what key is pressed
        self.left_pressed = False
        self.right_pressed = False
        self.up_pressed = False
        self.down_pressed = False

        # Set the background color
        self.background_color = arcade.color.BLACK

        self.background_music = None
        self.background_music_player = None

        # Setup camera stuff
        self.camera = arcade.Camera2D()

        self._holy_triangle = ((settings.WINDOW_WIDTH/5, settings.WINDOW_HEIGHT-(settings.WINDOW_HEIGHT/4)),
                               (settings.WINDOW_WIDTH/4, settings.WINDOW_HEIGHT/2),
                               (settings.WINDOW_WIDTH/5, settings.WINDOW_HEIGHT/4))

    def setup(self):
        # Create the SpriteList
        self.background_sprites = arcade.SpriteList()
        self.player_sprites = arcade.SpriteList()
        self.foreground_sprites = arcade.SpriteList()

        # Create and append the players to the SpriteList.
        self.player_one = player.PlayerCharacter(default_texture="assets/sprites/player_characters/kris/default.png",
                                                 scale=4.0,
                                                 center_x=self.center_x,
                                                 center_y=self.center_y,
                                                 angle=0,
                                                 sprite_folder_name="kris",
                                                 name="Kris",
                                                 max_hp=90,
                                                 attack=10,
                                                 defense=2,
                                                 magic=0)  # Sprite initialization
        self.player_one.position = self._holy_triangle[0]  # Center sprite on the screen
        self.player_one.set_animation_state("battle_idle")
        self.player_sprites.append(self.player_one)  # Append the instance to the SpriteList

        # Start the background music.
        self.background_music = arcade.load_sound("assets/audio/songs/ANOTHER_HIM.wav", False)
        self.background_music_player = self.background_music.play()
        self.background_music_player.pitch = 0.0
        self.background_music_player.loop = True

        sound_methods.gradually_update_pitch(self.background_music_player, 1.0, 0.02, 0.05)

        # Animate the background of the GONERMAKER.
        graphics_methods.animate_depths(self.background_sprites)

    def on_draw(self):
        # 3. Clear the screen
        self.clear()

        # Draw in layer order (background → player → foreground)
        with self.camera.activate():
            self.background_sprites.draw(pixelated=True)
            self.player_sprites.draw(pixelated=True)
            self.foreground_sprites.draw(pixelated=True)

    def on_resize(self, width, height):
        super().on_resize(width, height)
        self.camera.match_window()

    def update_player_speed(self):
        # Calculate speed based on the keys pressed
        self.player_one.change_x = 0
        self.player_one.change_y = 0

        if self.up_pressed and not self.down_pressed:
            self.player_one.change_y = player.MOVEMENT_SPEED
        elif self.down_pressed and not self.up_pressed:
            self.player_one.change_y = -player.MOVEMENT_SPEED
        if self.left_pressed and not self.right_pressed:
            self.player_one.change_x = -player.MOVEMENT_SPEED
        elif self.right_pressed and not self.left_pressed:
            self.player_one.change_x = player.MOVEMENT_SPEED

    def on_update(self, delta_time):
        """ Movement and game logic """

        # Contains the default positions for all three players
        self._holy_triangle = ((settings.WINDOW_WIDTH / 5, settings.WINDOW_HEIGHT - (settings.WINDOW_HEIGHT / 4)),
                               (),
                               (settings.WINDOW_WIDTH / 5, settings.WINDOW_HEIGHT / 4))

        # Update the player's animation.
        self.player_one.update_animation(delta_time)

    def on_key_press(self, key, modifiers):
        """Called whenever a key is pressed. """

        if key == arcade.key.F11:
            self.window.set_fullscreen(not self.window.fullscreen)
            settings.WINDOW_SCALE = math.sqrt((self.width / self._initial_width) * (self.height / self._initial_height))
            self.camera.zoom = settings.WINDOW_SCALE

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

    def on_key_release(self, key, modifiers):
        """Called when the user releases a key. """

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

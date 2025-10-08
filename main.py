import arcade
import settings
import player
import pyglet
import sound_methods
import graphics_methods


class GameView(arcade.View):
    def __init__(self):
        # Call the parent class initializer
        super().__init__()

        # Variables that will hold sprite lists
        self.player_list = None

        # Set up the player info
        self.player_sprite = None

        # Track the current state of what key is pressed
        self.left_pressed = False
        self.right_pressed = False
        self.up_pressed = False
        self.down_pressed = False

        # 1. Create the SpriteList
        self.sprites = arcade.SpriteList()

        # Set the background color
        self.background_color = arcade.color.BLACK

        self.background_music = None
        self.background_music_player = None

    def setup(self):
        # 1. Create the SpriteList
        self.sprites = arcade.SpriteList()

        # 2. Create and append your sprite instance to the SpriteList
        self.player_sprite = arcade.Sprite(path_or_texture="assets/sprites/soul/soul.png",
                                           scale=2.0)  # Sprite initialization
        self.player_sprite.position = self.center  # Center sprite on the screen
        self.sprites.append(self.player_sprite)  # Append the instance to the SpriteList

        # 3. Start the background music.
        self.background_music = arcade.load_sound("assets/audio/songs/ANOTHER_HIM.wav", False)
        self.background_music_player = self.background_music.play()
        self.background_music_player.pitch = 0.0
        self.background_music_player.loop = True

        sound_methods.gradually_update_pitch(self.background_music_player, 1.0, 0.02, 0.05)

        # 4. Animate the background of the GONERMAKER.
        graphics_methods.initialize_depths_array(1.0, self.center, self.sprites)

        graphics_methods.animate_depths(0.05)

    def on_draw(self):
        # 3. Clear the screen
        self.clear()

        # 4. Call draw() on the SpriteList inside an on_draw() method
        self.sprites.draw(pixelated=True)

    def update_player_speed(self):

        # Calculate speed based on the keys pressed
        self.player_sprite.change_x = 0
        self.player_sprite.change_y = 0

        if self.up_pressed and not self.down_pressed:
            self.player_sprite.change_y = player.MOVEMENT_SPEED
        elif self.down_pressed and not self.up_pressed:
            self.player_sprite.change_y = -player.MOVEMENT_SPEED
        if self.left_pressed and not self.right_pressed:
            self.player_sprite.change_x = -player.MOVEMENT_SPEED
        elif self.right_pressed and not self.left_pressed:
            self.player_sprite.change_x = player.MOVEMENT_SPEED

    def on_update(self, delta_time):
        """ Movement and game logic """

        # Move the player
        self.sprites.update(delta_time)

    def on_key_press(self, key, modifiers):
        """Called whenever a key is pressed. """

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

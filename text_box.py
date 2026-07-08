import math

import arcade
from arcade import Sound, Sprite, Texture

from sprites_and_effects_collection import SpritesAndEffectsCollection


class SpriteTextBoxDialog:
    """
    Contains the data needed to display a dialog in the SpriteTextBox.
    """
    def __init__(
            self,
            text: str = "",
            font_size: float = 48.0,
            character_width: int = 16,
            character_height: int = 32,
            text_spacing: int = 1,
            line_spacing: int = 8,
            rate_of_text: float = 0.05,
            text_sound_path: str = "assets/audio/dialog/snd_text.wav",
            font_name: str = "8bitoperator JVE",
            font_texture_dict: dict = None
    ):
        """
        Initializes the basic dialog data
        :param text: the text to display in the dialog.
        # TODO: allow this string to be modified to have the textbox provide effects to the text.
        :param character_width: the width of the characters in the dialog
        :param character_height: the height of the characters in the dialog
        :param text_spacing: The space (in pixels) between characters.
        :param rate_of_text: The amount of time (in seconds) between each character being displayed.
        :param text_sound_path: The sound to be played every time that a letter of dialog is loaded.
        :param font_name: the font name of the text, if it is font-based.
        :param font_texture_dict: the texture dict, if the font is spritesheet-based.
        """
        self.text = text
        self.font_size = font_size
        self.text_spacing = text_spacing
        self.line_spacing = line_spacing
        self.rate_of_text = rate_of_text
        self.text_sound_path = text_sound_path
        self.font_name = font_name
        self.font_texture_dict = font_texture_dict
        self.character_width = character_width
        self.character_height = character_height

class SpriteTextBox(Sprite):
    """
    My attempt at creating a non-widget means of displaying text. This will be more in line with the way text is
    rendered in Deltarune, rendering each character as an individual sprite to support text effects and non-font
    typefaces.
    """
    def __init__(self,
                 center_x: int = 0,
                 center_y: int = 0,
                 width: int = 200,
                 height: int = 100,
                 sprites_and_effects_collection: SpritesAndEffectsCollection = None):
        """
        Load the text box.
        :param center_x: the x coordinate of the center of the box.
        :param center_y: the y coordinate of the center of the box.
        :param width: the width of the box.
        :param height: the height of the box.
        """
        super().__init__(
            path_or_texture=arcade.Texture.create_empty(
                name="text_box",
                size=(width, height),
                color=(0, 0, 0, 255)
            ),
            center_x=center_x,
            center_y=center_y
        )

        self.text = ""
        self.text_length = len(self.text)
        self.current_character_index = 0
        self.row_count = 1
        self.column_count = 1
        self.character_row_index = 0
        self.character_column_index = 0

        # Default internal variables to be used in lieu of a text box dialog being loaded.
        self.rate_of_text = 0.05
        self.time_elapsed_since_last_character = 0.0
        self.text_spacing = 1
        self.line_spacing = 8
        self.text_font_name = "8bitoperator JVE"
        self.text_font_size = 36
        self.text_font_sprite_sheet_path = ""
        self.text_sound = Sound("assets/audio/dialog/snd_text.wav")
        self.character_width = 0
        self.character_height = 0
        self.font_texture_dict = None

        self.sprites_and_effects_collection = sprites_and_effects_collection
        self.sprites_associated_with_text_box = []
        self.sprites_associated_with_text_box.append(self)
        self.letter_sprites = []

        self.sprite_sheet = None

        # Controls whether the text box is loading dialog.
        self.is_loading_dialog = False

        # Variables used to dynamically calculate row/column counts
        self.letter_width = 16
        self.letter_height = 32
        self.current_word_index = 0
        self.current_character_index_in_current_word = 0
        self.words = []
        self.max_number_of_characters_in_a_row = 0

        # Space texture
        self.space_texture = None

        # Used for debugging
        self.last_character_loaded = False

    def get_character_sprite(self, character: str) -> Sprite:
        """
        Gets the sprite for the character to be loaded.
        :return: None
        """
        if self.font_texture_dict is not None:
            character_sprite=Sprite(
                path_or_texture=self.font_texture_dict[character],
                scale=2.0
            )
        else:
            character_sprite = arcade.create_text_sprite(
                text=character,
                color=(255, 255, 255),
                font_name=self.text_font_name,
                font_size=self.text_font_size
            )

        return character_sprite

    def add_character_to_text_box(self):
        """ Adds an individual letter from the supplied text to the speech bubble. """
        character = self.text[self.current_character_index]
        character_sprite = self.get_character_sprite(character)

        character_x_coordinate = self.left + 24 + int(self.character_column_index * (self.letter_width + self.text_spacing))
        character_y_coordinate = self.top - 24 - int(self.character_row_index * (self.letter_height + self.line_spacing))

        character_sprite.center_x = character_x_coordinate
        character_sprite.center_y = character_y_coordinate

        self.sprites_and_effects_collection.soul_sprites.append(character_sprite)
        self.sprites_associated_with_text_box.append(character_sprite)
        self.letter_sprites.append(character_sprite)

        # Iterate the indexes.
        self.current_character_index += 1
        if self.current_character_index_in_current_word == len(self.words[self.current_word_index]):
            self.current_word_index += 1
            self.current_character_index_in_current_word = 0
        else:
            self.current_character_index_in_current_word += 1

        # If the current character is the first letter of a new word, check to see if the word fits in the current line
        if (self.current_character_index_in_current_word == 0 and self.character_column_index + len(
                self.words[self.current_word_index]) >= self.max_number_of_characters_in_a_row) or self.words[self.current_word_index] == "\n":
            self.character_row_index += 1
            self.character_column_index = 0
        else:
            self.character_column_index += 1

        return character_sprite

    def load_dialog(self, text_box_dialog: SpriteTextBoxDialog):
        """
        Initiates the process that loads the provided text_box_dialog into the text box.
        :param text_box_dialog: The TextBoxDialog object representing the text to be loaded.
        :return:
        """
        # Used for debugging
        self.last_character_loaded = False

        # Kill the sprites from the previous dialog loading instance, if there was one.
        for sprite in self.letter_sprites:
            sprite.kill()

        self.letter_sprites.clear()
        self.sprites_associated_with_text_box = [self.sprites_associated_with_text_box[0]]

        # Reset the indexes
        self.character_row_index = 0
        self.character_column_index = 0
        self.current_character_index = 0
        self.current_word_index = 0
        self.current_character_index_in_current_word = 0

        self.text = text_box_dialog.text
        self.text_font_size = text_box_dialog.font_size
        self.text_spacing = text_box_dialog.text_spacing
        self.line_spacing = text_box_dialog.line_spacing
        self.rate_of_text = text_box_dialog.rate_of_text
        if text_box_dialog.text_sound_path:
            self.text_sound = arcade.load_sound(text_box_dialog.text_sound_path)
        else:
            self.text_sound = None
        self.text_font_name = text_box_dialog.font_name
        self.font_texture_dict = text_box_dialog.font_texture_dict
        self.character_width = text_box_dialog.character_width
        self.character_height = text_box_dialog.character_height

        self.text_length = len(self.text)
        self.current_character_index = 0

        # The letter 'W' is used as a crude gauge of the average required space for each character.
        gauge_letter_sprite = self.get_character_sprite("W")
        self.letter_width = int(gauge_letter_sprite.width)
        self.letter_height = int(gauge_letter_sprite.height)

        # Calculate the length of each row and the number of rows.
        self.max_number_of_characters_in_a_row = self.width // (self.letter_width + self.text_spacing)

        self.words = self.text.split()

    def clear_dialog(self):
        """
        Clears the text box from the text box.
        :return: None
        """
        self.load_dialog(SpriteTextBoxDialog(text=""))

    def update_animation(self, delta_time):
        if self.current_character_index < self.text_length:
            self.time_elapsed_since_last_character += delta_time
            if self.time_elapsed_since_last_character > self.rate_of_text:
                self.time_elapsed_since_last_character -= self.rate_of_text
                # Attempt to add a character to the text box.
                self.add_character_to_text_box()
                if self.text_sound:
                    self.text_sound.play()
        else:
            if not self.last_character_loaded:
                self.last_character_loaded = True

    def despawn_text_box(self):
        """
        Despawns the text box.
        :return: None
        """
        if self in self.sprites_and_effects_collection.effects:
            self.sprites_and_effects_collection.effects.remove(self)
        for sprite in self.sprites_associated_with_text_box:
            sprite.kill()


class HimTextBox(SpriteTextBox):
    """
    A textbox representing the "voice" that plays in the GONERMAKER section of the game.
    """
    def __init__(
        self,
        center_x: int = 0,
        center_y: int = 0,
        width: int = 200,
        height: int = 100,
        sprites_and_effects_collection: SpritesAndEffectsCollection = None
    ):
        super().__init__(
            center_x,
            center_y,
            width,
            height,
            sprites_and_effects_collection
        )

        self.text_effect_sprites = []

        self.min_alpha = 24
        self.max_alpha = 56
        self.delta_alpha = self.max_alpha - self.min_alpha
        self.animation_duration = 3

    def add_character_to_text_box(self):
        character_sprite = super().add_character_to_text_box()
        offset_in_pixels = int(self.text_font_size / 12)
        for i in range(-1, 2):
            for j in range(-1, 2):
                if i != 0 or j != 0:
                    x_offset = offset_in_pixels * i
                    y_offset = offset_in_pixels * j
                    adjacent_character_sprite = Sprite(
                        path_or_texture=character_sprite.texture,
                        center_x=character_sprite.center_x + x_offset,
                        center_y=character_sprite.center_y + y_offset
                    )

                    adjacent_character_sprite.alpha = 16

                    self.text_effect_sprites.append(adjacent_character_sprite)
                    self.sprites_and_effects_collection.soul_sprites.append(adjacent_character_sprite)

        return character_sprite

    def animate_letter_sprites(self, time: float):
        """
        period_adjusted_time = time % self.animation_duration
        if period_adjusted_time < self.animation_duration * .25:
            alpha = self.min_alpha + (self.delta_alpha * (period_adjusted_time * (self.animation_duration / 2)))
        elif self.animation_duration * .25 <= period_adjusted_time < self.animation_duration * .5:
            alpha = self.max_alpha
        elif self.animation_duration * .5 <= period_adjusted_time < self.animation_duration * .75:
            alpha = self.max_alpha - (self.delta_alpha * ((period_adjusted_time - (self.animation_duration / 2)) * (self.animation_duration / 2)))
        else:
            alpha = self.min_alpha
        """
        theta = (time / self.animation_duration) * (2 * math.pi)

        alpha = self.min_alpha + (self.delta_alpha * (math.sin(theta) + 1) / 2)

        for sprite in self.text_effect_sprites:
            sprite.alpha = alpha

    def despawn_text_box(self):
        super().despawn_text_box()
        for sprite in self.text_effect_sprites:
            sprite.kill()

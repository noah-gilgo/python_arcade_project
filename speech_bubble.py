import arcade
from arcade import Sprite, Texture, SpriteSheet, LBWH, Sound

from sprites_and_effects_collection import SpritesAndEffectsCollection


class SpeechBubbleTextContainer(Sprite):
    """
    The part of speech bubbles that contain text. This version only supports Latin characters. I was originally going to
    implement the speech bubbles (and all other dialogue in the game) with multi-language support, but as it turns out
    many of the fonts used in Deltarune only have the very limited basic Latin character set available. Only one font
    in Deltarune (Greater Determination Dr Damage) has a variant with broader language support, so a true broad-tongue
    Deltarune would require either non-Deltarune fonts or a lot of commissioned font work.

    This version of the speech bubble is meant to most closely mimic the speech bubbles in Deltarune. (Dotum Che font,
    animatable characters, even spacing between the characters, etc.)
    """

    # TODO: make a speech bubble that supports multiple languages.

    def __init__(self, text: str = "test text", center_x: float = 0, center_y: float = 0, row_count: int = 1,
                 column_count: int = 1, text_spacing: int = 1, rate_of_text: float = 0.05, text_sound: Sound = None,
                 sprites_and_effects_collection: SpritesAndEffectsCollection = None):

        self.text = text
        self.text_length = len(self.text)
        self.current_character_index = 0
        self.row_count = row_count
        self.column_count = column_count
        self.character_row_index = 0
        self.character_column_index = 0

        self.rate_of_text = rate_of_text
        self.time_elapsed_since_last_character = 0.0

        if text_sound is None:
            self.text_sound = Sound("assets/audio/dialog/snd_text.wav")
        else:
            self.text_sound = text_sound

        self.sprites_and_effects_collection = sprites_and_effects_collection

        self.text_spacing = text_spacing  # The amount of pixels between each character

        width = (self.column_count * 11) + (self.column_count - self.text_spacing)
        height = (self.row_count * 17) + (self.row_count - self.text_spacing)

        super().__init__(
            path_or_texture=Texture.create_empty(
                name="speech_bubble_text_container",
                size=(width, height),
                color=(255, 255, 255, 255)
            ),
            center_x=center_x,
            center_y=center_y
        )

        self.sprites_and_effects_collection.speech_bubble_sprites.append(self)
        self.sprites_and_effects_collection.effects.append(self)

        self.text_character_sprite_sheet = SpriteSheet("assets/sprites/speech_bubbles/speech_bubble_text_sprite_sheet.png")

    def get_character_sprite(self, character_unicode_code: int) -> Sprite:
        """ Returns a character sprite from the sprite sheet depending on the supplied character. """

        offset_code = character_unicode_code - 32

        char_column = offset_code % 13
        char_row = offset_code // 13

        #offset_from_start_in_pixels = 9 * (character_unicode_code - 32)

        character_x_coordinate = char_column * 9
        character_y_coordinate = char_row * 17

        character_rect = LBWH(left=character_x_coordinate, bottom=character_y_coordinate, width=8, height=16)

        """
        character_sprite = arcade.create_text_sprite(
            text=character,
            color=(0, 0, 0),
            font_size=12.0,
            #width=10,
            font_name="DotumChe Pixel"
        )
        """

        return Sprite(self.text_character_sprite_sheet.get_texture(character_rect))

    def add_character_to_speech_bubble(self):
        """ Adds an individual letter from the supplied text to the speech bubble. """
        character = self.text[self.current_character_index]
        character_unicode_code = ord(character)

        if 127 > character_unicode_code > 31: # Letters, numbers, symbols
            character_sprite = self.get_character_sprite(character_unicode_code)

            character_x_coordinate = self.left + 7 + (self.character_column_index * (8 + self.text_spacing))
            character_y_coordinate = self.top - 9 - (self.character_row_index * 17)

            character_sprite.center_x = character_x_coordinate
            character_sprite.center_y = character_y_coordinate

            self.sprites_and_effects_collection.speech_bubble_sprites.append(character_sprite)

            if self.character_column_index < self.column_count:
                self.character_column_index += 1
            else:
                self.character_column_index = 0
                self.character_row_index += 1

        else: # Basic characters such as newline, tab, etc, as well as characters beyond basic latin characters
            # Treat them all like they're the enter key.
            self.character_column_index = 0
            self.character_row_index += 1

        self.current_character_index += 1

    def update_animation(self, delta_time):
        if self.current_character_index < self.text_length:
            self.time_elapsed_since_last_character += delta_time
            if self.time_elapsed_since_last_character > self.rate_of_text:
                self.time_elapsed_since_last_character -= self.rate_of_text
                self.add_character_to_speech_bubble()
                self.text_sound.play()


class SpeechBubbleDialog:
    def __init__(self, text: str = "", row_count: int = 10, column_count: int = 10, text_spacing: int = 1,
                 text_sound: Sound = None, rate_of_text: float = 0.05):
        """
        Stores basic data needed by the speech bubble to render a specific dialogue.
        :param text: The text of the dialogue.
        :param row_count: The rows of dialogue accommodated by the speech bubble.
        :param column_count: The columns of dialogue accommodated by the speech bubble.
        :param text_spacing: The space between letters in the rendered dialogue.
        """

        self.text = text
        self.row_count = row_count
        self.column_count = column_count
        self.text_spacing = text_spacing
        self.text_sound = text_sound
        self.rate_of_text = rate_of_text

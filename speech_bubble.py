import arcade
from arcade import Sprite, Texture, SpriteSheet, LBWH, Sound

from sprites_and_effects_collection import SpritesAndEffectsCollection


class SpeechBubbleDialog:
    def __init__(self, text: str = "", row_count: int = 10, column_count: int = 10, text_spacing: int = 1,
                 text_sound: Sound = None, rate_of_text: float = 0.05, is_left_of_character: bool = True,
                 actor = None):
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
        self.is_left_of_character = is_left_of_character
        self.actor = actor


class SpeechBubble(Sprite):
    """
    The part of speech bubbles that contain text. This version only supports Latin characters. I was originally going to
    implement the speech bubbles (and all other dialogue in the game) with multi-language support, but as it turns out
    many of the fonts used in Deltarune only have the very limited basic Latin character set available. Only one font
    in Deltarune (Greater Determination Dr Damage) has a variant with broader language support, so a true broad-tongue
    Deltarune simulator would require either non-Deltarune fonts or a lot of commissioned font work.

    This version of the speech bubble is meant to most closely mimic the speech bubbles in Deltarune. (Dotum Che font,
    animatable characters, even spacing between the characters, etc.)
    """

    # TODO: make a speech bubble that supports multiple languages.

    def __init__(self, speech_bubble_dialog: SpeechBubbleDialog,
                 sprites_and_effects_collection: SpritesAndEffectsCollection = None,
                 center_x: float = 0, center_y: float = 0):
        """
        Initializes the speech bubble. Adds it to the screen and starts animating the text.
        :param speech_bubble_dialog: The SpeechBubbleDialog object containing the dialog data for the speech bubble.
        :param sprites_and_effects_collection: The collection of sprite lists the speech bubble sprites will be added to
        :param center_x: The center_x of the main text component of the speech bubble, if the uses wishes to specify one
        :param center_y: The center_y of the main text component of the speech bubble, if the uses wishes to specify one
        :param actor: Optional actor parameter. If specified, the coordinates of the speech bubble will be set near it.
        :param is_left_of_character: If specified with actor, controls which side of the actor the bubble will spawn on
        """

        self.text = speech_bubble_dialog.text
        self.text_length = len(self.text)
        self.current_character_index = 0
        self.row_count = speech_bubble_dialog.row_count
        self.column_count = speech_bubble_dialog.column_count
        self.character_row_index = 0
        self.character_column_index = 0

        self.rate_of_text = speech_bubble_dialog.rate_of_text
        self.time_elapsed_since_last_character = 0.0
        self.speech_bubble_is_left_of_character = speech_bubble_dialog.is_left_of_character

        self.speech_bubble_scale = 5/3  # The amount that the speech bubble is scaled up from its default size.

        if speech_bubble_dialog.text_sound is None:
            self.text_sound = Sound("assets/audio/dialog/snd_text.wav")
        else:
            self.text_sound = speech_bubble_dialog.text_sound

        self.sprites_and_effects_collection = sprites_and_effects_collection

        self.text_spacing = speech_bubble_dialog.text_spacing  # The amount of pixels between each character

        width = int(((self.column_count * 8) + (self.column_count - self.text_spacing)) * self.speech_bubble_scale)
        height = int(((self.row_count * 17) + (self.row_count - self.text_spacing)) * self.speech_bubble_scale)

        speech_bubble_center_x = center_x
        speech_bubble_center_y = center_y

        if speech_bubble_dialog.actor:
            speech_bubble_center_y = speech_bubble_dialog.actor.center_y + (speech_bubble_dialog.actor.height / 10)
            if speech_bubble_dialog.is_left_of_character:
                speech_bubble_center_x = speech_bubble_dialog.actor.center_x - (speech_bubble_dialog.actor.width / 2) - (width / 2) - 60
            else:
                speech_bubble_center_x = speech_bubble_dialog.actor.center_x + (speech_bubble_dialog.actor.width / 2) + (width / 2) + 60


        super().__init__(
            path_or_texture=Texture.create_empty(
                name="speech_bubble_text_container",
                size=(width, height),
                color=(255, 255, 255, 255)
            ),
            center_x=speech_bubble_center_x,
            center_y=speech_bubble_center_y
        )

        # Append the sprites that decorate the basic text box.
        self.sprites_associated_with_text_box = []

        self.sprites_associated_with_text_box.append(self)

        # Side sprites (top, bottom, left, right borders of the dialogue box)
        left_right_border_sprite_width = int(10*self.speech_bubble_scale)
        top_bottom_border_sprite_height = left_right_border_sprite_width

        # Left/right border texture
        left_right_border_texture = Texture.create_empty(
            name="left_right_border_texture",
            size=(left_right_border_sprite_width, int(self.height)),
            color=(255, 255, 255, 255)
        )

        # Left border sprite
        self.sprites_associated_with_text_box.append(
            Sprite(
                path_or_texture=left_right_border_texture,
                center_x=self.center_x - (self.width / 2) - (left_right_border_sprite_width / 2),
                center_y=self.center_y,
            )
        )

        # Right border sprite
        self.sprites_associated_with_text_box.append(
            Sprite(
                path_or_texture=left_right_border_texture,
                center_x=self.center_x + (self.width / 2) + (left_right_border_sprite_width / 2),
                center_y=self.center_y
            )
        )

        # Top/bottom border texture
        top_bottom_border_texture = Texture.create_empty(
            name="top_bottom_border_texture",
            size=(int(self.width), top_bottom_border_sprite_height),
            color=(255, 255, 255, 255)
        )

        # Bottom border sprite
        self.sprites_associated_with_text_box.append(
            Sprite(
                path_or_texture=top_bottom_border_texture,
                center_x=self.center_x,
                center_y=self.center_y - (self.height / 2) - (top_bottom_border_sprite_height / 2)
            )
        )

        # Top border sprite
        self.sprites_associated_with_text_box.append(
            Sprite(
                path_or_texture=top_bottom_border_texture,
                center_x=self.center_x,
                center_y=self.center_y + (self.height / 2) + (top_bottom_border_sprite_height / 2)
            )
        )

        # Corner texture
        corner_texture = arcade.load_texture("assets/sprites/speech_bubbles/speech_bubble_corner_texture.png")
        corner_texture.width = left_right_border_sprite_width
        corner_texture.height = top_bottom_border_sprite_height

        # Corner sprites

        # Top right corner
        self.sprites_associated_with_text_box.append(
            Sprite(
                path_or_texture=corner_texture,
                center_x=self.center_x + (self.width / 2) + (left_right_border_sprite_width / 2),
                center_y=self.center_y + (self.height / 2) + (top_bottom_border_sprite_height / 2)
            )
        )

        # Bottom right corner
        self.sprites_associated_with_text_box.append(
            Sprite(
                path_or_texture=corner_texture.flip_vertically(),
                center_x=self.center_x + (self.width / 2) + (left_right_border_sprite_width / 2),
                center_y=self.center_y - (self.height / 2) - (top_bottom_border_sprite_height / 2)
            )
        )

        # Bottom left corner
        self.sprites_associated_with_text_box.append(
            Sprite(
                path_or_texture=corner_texture.flip_diagonally(),
                center_x=self.center_x - (self.width / 2) - (left_right_border_sprite_width / 2),
                center_y=self.center_y - (self.height / 2) - (top_bottom_border_sprite_height / 2)
            )
        )

        # Top left corner
        self.sprites_associated_with_text_box.append(
            Sprite(
                path_or_texture=corner_texture.flip_horizontally(),
                center_x=self.center_x - (self.width / 2) - (left_right_border_sprite_width / 2),
                center_y=self.center_y + (self.height / 2) + (top_bottom_border_sprite_height / 2)
            )
        )

        # The pointy bit that points at the character talking.
        if self.speech_bubble_is_left_of_character:
            if speech_bubble_dialog.row_count < 3:
                speech_bubble_arrow_texture_path = "assets/sprites/speech_bubbles/small_right_facing_speech_bubble_arrow.png"
            else:
                speech_bubble_arrow_texture_path = "assets/sprites/speech_bubbles/big_right_facing_speech_bubble_arrow.png"
        else:
            if speech_bubble_dialog.row_count < 3:
                speech_bubble_arrow_texture_path = "assets/sprites/speech_bubbles/small_left_facing_speech_bubble_arrow.png"
            else:
                speech_bubble_arrow_texture_path = "assets/sprites/speech_bubbles/big_left_facing_speech_bubble_arrow.png"

        speech_bubble_arrow_texture = arcade.load_texture(
            file_path=speech_bubble_arrow_texture_path,
        )

        speech_bubble_arrow_sprite_width = int(speech_bubble_arrow_texture.width * self.speech_bubble_scale)

        if self.speech_bubble_is_left_of_character:
            speech_bubble_arrow_sprite_center_x = self.center_x + (self.width / 2) + left_right_border_sprite_width + (
                    speech_bubble_arrow_sprite_width / 2)
        else:
            speech_bubble_arrow_sprite_center_x = self.center_x - (self.width / 2) + left_right_border_sprite_width - (
                    speech_bubble_arrow_sprite_width / 2)

        self.sprites_associated_with_text_box.append(
            Sprite(
                path_or_texture=speech_bubble_arrow_texture_path,
                center_x=speech_bubble_arrow_sprite_center_x,
                center_y=self.center_y,
                scale=self.speech_bubble_scale,
            )
        )

        for sprite in self.sprites_associated_with_text_box:
            self.sprites_and_effects_collection.speech_bubble_sprites.append(sprite)

        self.sprites_and_effects_collection.effects.append(self)

        self.text_character_sprite_sheet = SpriteSheet("assets/sprites/speech_bubbles/speech_bubble_text_sprite_sheet.png")

    def get_character_sprite(self, character_unicode_code: int) -> Sprite:
        """ Returns a (letter) character sprite from the sprite sheet depending on the supplied character. """

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

        letter_sprite = Sprite(
            path_or_texture=self.text_character_sprite_sheet.get_texture(character_rect),
            scale=self.speech_bubble_scale
        )

        self.sprites_associated_with_text_box.append(letter_sprite)

        return letter_sprite

    def add_character_to_speech_bubble(self):
        """ Adds an individual letter from the supplied text to the speech bubble. """
        character = self.text[self.current_character_index]
        character_unicode_code = ord(character)

        if 127 > character_unicode_code > 31: # Letters, numbers, symbols
            character_sprite = self.get_character_sprite(character_unicode_code)

            character_x_coordinate = self.left + 6 + int((self.character_column_index * (8 + self.text_spacing)) * self.speech_bubble_scale)
            character_y_coordinate = self.top - 16 - int(self.character_row_index * 17 * self.speech_bubble_scale)

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

    def despawn_speech_bubble(self):
        """
        Despawns the speech bubble.
        :return: None
        """
        if self in self.sprites_and_effects_collection.effects:
            self.sprites_and_effects_collection.effects.remove(self)
        for sprite in self.sprites_associated_with_text_box:
            sprite.kill()

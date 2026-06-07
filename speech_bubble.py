from arcade import Sprite, Texture, SpriteSheet, LBWH

from sprites_and_effects_collection import SpritesAndEffectsCollection


class ClassicSpeechBubbleTextContainer:
    """
    The part of speech bubbles that contain text. This version only supports English.
    """
    def __init__(self, text: str = "test text", center_x: int = 0, center_y: int = 0, row_count: int = 1, column_count: int = 1,
                 text_spacing: int = 1, sprites_and_effects_collection: SpritesAndEffectsCollection = None):

        self.text = text
        self.text_length = len(self.text)
        self.current_character_index = 0

        self.sprites_and_effects_collection = sprites_and_effects_collection

        self.text_spacing = text_spacing  # The amount of pixels between each character

        width = (column_count * 8) + (column_count - self.text_spacing)
        height = (row_count * 16) + (row_count - self.text_spacing)

        self.speech_bubble_background_sprite = Sprite(
            path_or_texture=Texture.create_empty(
                name="speech_bubble_text_container",
                size=(width, height),
                color=(255, 255, 255, 255)
            ),
            center_x=center_x,
            center_y=center_y
        )

        self.sprites_and_effects_collection.speech_bubble_sprites.append(self.speech_bubble_background_sprite)

        self.text_character_sprite_sheet = SpriteSheet("assets/sprites/speech_bubbles/speech_bubble_text_sprite_sheet.png")

    def get_character_from_sprite_sheet(self, character: str):
        """ Returns a character sprite from the sprite sheet depending on the supplied character. """
        character_unicode_code = ord(character)

        offset_from_start_in_pixels = 9 * (character_unicode_code - 32)

        character_y_coordinate = offset_from_start_in_pixels // 117
        character_x_coordinate = offset_from_start_in_pixels % 117

        character_rect = LBWH(left=character_x_coordinate, bottom=character_y_coordinate, width=8, height=16)

        return self.text_character_sprite_sheet.get_texture(character_rect)

    def add_character_to_speech_bubble(self):
        """ Adds an individual letter from the supplied text to the speech bubble. """
        pass


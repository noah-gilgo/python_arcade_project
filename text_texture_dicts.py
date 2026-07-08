from pyglet.image.atlas import TextureAtlas

from texture_methods import load_textures_at_filepath_into_texture_array, load_images_at_filepath_into_image_array


class BattleMessageTextureDict(dict):
    def __init__(self):
        super().__init__()
        keys = [
            "MISS",
            "DOWN",
            "MAX",
            "UP",
            "100%",
            "RECRUIT",
            "LOST",
            "FROZEN",
            "SWOON",
            "TIRED",
            "AWAKE",
            "PURIFIED",
            "BURNED",
            "CHARRED"
        ]

        textures = load_textures_at_filepath_into_texture_array("assets/sprites/glyph_sprites/battle_message_sprites/words")

        texture_index = 0
        for key in keys:
            self[key] = textures[texture_index]
            texture_index += 1

class BattleMessageImageDict(dict):
    def __init__(self):
        super().__init__()

        keys = [
            "0",
            "1",
            "2",
            "3",
            "4",
            "5",
            "6",
            "7",
            "8",
            "9",
            "+",
            "-",
            "%",
            "0_golden",
            "1_golden",
            "2_golden",
            "3_golden",
            "4_golden",
            "5_golden",
            "6_golden",
            "7_golden",
            "8_golden",
            "9_golden",
            "+_golden",
            "-_golden",
            "%_golden",
            "/_golden"
        ]

        images = load_images_at_filepath_into_image_array("assets/sprites/glyph_sprites/battle_message_sprites/numbers")

        image_index = 0
        for key in keys:
            self[key] = images[image_index]
            image_index += 1

class DWDefaultTextureDict(dict):
    def __init__(self):
        super().__init__()
        keys = [
            "A",
            "B",
            "C",
            "D",
            "E",
            "F",
            "G",
            "H",
            "I",
            "J",
            "K",
            "L",
            "M",
            "N",
            "O",
            "P",
            "Q",
            "R",
            "S",
            "T",
            "U",
            "V",
            "W",
            "X",
            "Y",
            "Z",
            "a",
            "b",
            "c",
            "d",
            "e",
            "f",
            "g",
            "h",
            "i",
            "j",
            "k",
            "l",
            "m",
            "n",
            "o",
            "p",
            "q",
            "r",
            "s",
            "t",
            "u",
            "v",
            "w",
            "x",
            "y",
            "z",
            "0",
            "1",
            "2",
            "3",
            "4",
            "5",
            "6",
            "7",
            "8",
            "9",
            ".",
            ",",
            "?",
            "!",
            "@",
            "_",
            "*",
            "#",
            "$",
            "%",
            "&",
            "(",
            ")",
            "+",
            "-",
            "\\",
            ":",
            ";",
            "<",
            "=",
            ">",
            "[",
            "/",
            "]",
            "^",
            "`",
            "{",
            "|",
            "}",
            "~",
            "'",
            '"',
            " "
        ]

        textures = load_textures_at_filepath_into_texture_array(
            "assets/sprites/glyph_sprites/fonts/dw_default")

        texture_index = 0
        for key in keys:
            self[key] = textures[texture_index]
            texture_index += 1

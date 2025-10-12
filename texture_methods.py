import os
import arcade


def load_textures_at_filepath_into_texture_array(folder_path: str):
    textures = []

    for filename in sorted(os.listdir(folder_path)):
        if filename.lower().endswith(".png"):
            texture_path = os.path.join(folder_path, filename)
            texture = arcade.load_texture(texture_path)
            textures.append(texture)

    return textures

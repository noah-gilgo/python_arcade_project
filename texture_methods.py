import os
import arcade
from PIL.Image import Image
from arcade import Texture


def load_textures_at_filepath_into_texture_array(folder_path: str) -> list[Texture]:
    textures = []

    for filename in sorted(os.listdir(folder_path)):
        if filename.lower().endswith(".png"):
            texture_path = os.path.join(folder_path, filename)
            texture = arcade.load_texture(texture_path)
            textures.append(texture)

    return textures

def load_images_at_filepath_into_image_array(folder_path: str) -> list[Image]:
    images = []

    for filename in sorted(os.listdir(folder_path)):
        if filename.lower().endswith(".png"):
            image_path = os.path.join(folder_path, filename)
            image = arcade.load_image(image_path)
            images.append(image)
            print(filename)

    return images

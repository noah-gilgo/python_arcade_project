from PIL import Image, ImageDraw
from arcade import Texture, Sprite
from arcade.hitbox import HitBox

import settings


class BulletBoard:
    def __init__(self):
        self.bullet_board_image = Image.new("RGBA", (150, 150))
        self.draw = ImageDraw.Draw(self.bullet_board_image)
        self.draw.rectangle((0, 0, 149, 149), outline=(0, 192, 0, 255), fill=(0, 0, 0, 255), width=4)
        self.bullet_board_texture = Texture(self.bullet_board_image)
        self.bullet_board_sprite = Sprite(
            path_or_texture=self.bullet_board_texture,
            center_x=settings.WINDOW_CENTER_X,
            center_y=settings.WINDOW_HEIGHT * (2 / 3),
            scale=2.0
        )

        self.bullet_board_sprite.alpha = 128

        self.bullet_board_sprite.visible = False

        self.bullet_board_loading_animation_sprites = []
        scale = 0.1
        for i in range(1, 18):
            bullet_board_sprite = Sprite(
                path_or_texture=self.bullet_board_texture,
                center_x=settings.WINDOW_CENTER_X,
                center_y=settings.WINDOW_HEIGHT * (2 / 3)
            )
            bullet_board_sprite.alpha = 255
            bullet_board_sprite.visible = False
            bullet_board_sprite.turn_left(15 * i)
            bullet_board_sprite.scale = scale
            scale += 0.1

            self.bullet_board_loading_animation_sprites.insert(0, bullet_board_sprite)

        self.bullet_board_loading_animation_sprites.insert(0, self.bullet_board_sprite)

        self.time = 0
        self.load_bullet_board_animation_total_duration = 0.6

        self.number_of_sprites_in_loading_animation = len(self.bullet_board_loading_animation_sprites)
        self.loading_animation_framerate = self.number_of_sprites_in_loading_animation / self.load_bullet_board_animation_total_duration

        self.load_bullet_board_animation_playing = False
        self.unload_bullet_board_animation_playing = False
        self.bullet_board_sprites_not_loaded = True  # TODO: remove sprites from list after battle is done

        self.is_terminated = False

        # Load the hitbox
        self.bullet_board_sprite.hit_box = HitBox(
            points=[
                (self.bullet_board_sprite.left, self.bullet_board_sprite.top),
                (self.bullet_board_sprite.right, self.bullet_board_sprite.top),
                (self.bullet_board_sprite.right, self.bullet_board_sprite.bottom),
                (self.bullet_board_sprite.left, self.bullet_board_sprite.bottom)
            ]
        )

    def get_center_coordinates(self):
        """ Get the center coordinates of the bullet board. """
        return (self.bullet_board_sprite.center_x, self.bullet_board_sprite.center_y)

    def update_animation(self, delta_time: float):
        """ Updates the load bullet board animation. """
        if self.load_bullet_board_animation_playing:
            self.time += delta_time
            # print(self.time)
            sprite_index = self.number_of_sprites_in_loading_animation
            for sprite in self.bullet_board_loading_animation_sprites:
                if sprite_index < (self.time * self.loading_animation_framerate):
                    sprite.visible = True
                    if sprite_index < self.number_of_sprites_in_loading_animation:
                        sprite.alpha -= (720
                                         * delta_time) # 255 - (1.5 * (255 * (self.time / self.load_bullet_board_animation_total_duration)))
                    else:
                        sprite.alpha = min(sprite.alpha + (180 * delta_time), 255)

                sprite_index -= 1

            if self.time >= self.load_bullet_board_animation_total_duration * 1.6:
                # for sprite in self.bullet_board_loading_animation_sprites[1:]:
                #     sprite.visible = False
                # self.bullet_board_sprite.alpha = 255
                self.load_bullet_board_animation_playing = False
                self.time = 0.0

        if self.unload_bullet_board_animation_playing:
            self.time += delta_time
            sprite_index = 0
            for sprite in self.bullet_board_loading_animation_sprites:
                if sprite_index < (self.time * self.loading_animation_framerate):
                    sprite.visible = False
                else:
                    sprite.alpha = max(sprite.alpha - (180 * delta_time), 0)

                sprite_index += 1

            if self.time >= self.load_bullet_board_animation_total_duration * 1.6:
                # for sprite in self.bullet_board_loading_animation_sprites[1:]:
                #     sprite.visible = False
                # self.bullet_board_sprite.alpha = 255
                self.unload_bullet_board_animation_playing = False
                self.time = 0.0

    def load_bullet_board(self, controller):
        """ Loads the bullet board sprite. """
        self.load_bullet_board_animation_playing = True

        if self not in controller.sprites_and_effects_collection.effects:
            controller.sprites_and_effects_collection.effects.append(self)
        if self.bullet_board_sprites_not_loaded:
            for sprite in self.bullet_board_loading_animation_sprites:
                if sprite not in controller.sprites_and_effects_collection.effects_sprites:
                    controller.sprites_and_effects_collection.effects_sprites.append(sprite)

            self.bullet_board_sprites_not_loaded = False

    def unload_bullet_board(self, controller):
        """ Unloads the bullet board sprite. """
        self.unload_bullet_board_animation_playing = True

        for sprite in self.bullet_board_loading_animation_sprites:
            sprite.alpha = 128

        if self.bullet_board_sprites_not_loaded:
            for sprite in self.bullet_board_loading_animation_sprites:
                controller.sprites_and_effects_collection.effects_sprites.append(sprite)

            self.bullet_board_sprites_not_loaded = False

    def get_sprites(self):
        return self.bullet_board_loading_animation_sprites + [self.bullet_board_sprite]

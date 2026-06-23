import arcade
from arcade import Camera2D, SpriteList
from arcade.gui import UIManager


class SpritesAndEffectsCollection:
    """
    Contains a lot of the generic sprite lists/effects used by the games rendering.

    This will be passed into any objects that require rendering stuff on the screen
    """

    def __init__(self, camera: Camera2D, manager: UIManager):
        self.camera = camera

        self.effects = []
        self.manager = manager

        self.background_sprites = SpriteList()  # Background sprites, like the animated background in battle.
        self.character_sprites = SpriteList()  # Character sprites, like for player characters/non player characters
        self.effects_sprites = SpriteList()  # Effects sprites, like the animations for attacking/spells
        self.bullet_sprites = SpriteList()  # Bullet sprites, like the ones spawned by enemies in their attacks
        self.speech_bubble_sprites = SpriteList()  # Speech bubbles, such as the ones characters talk with in battle
        self.soul_sprites = SpriteList()  # The SOUL sprite and related sprites, like the yellow soul bullets

        self.is_drawing = True  # Controls whether the sprites are being drawn to the screen.
        self.is_drawing_background_sprites = True
        self.is_drawing_character_sprites = True
        self.is_drawing_gui_sprites = True
        self.is_drawing_effects_sprites = True
        self.is_drawing_speech_bubble_sprites = True
        self.is_drawing_bullet_sprites = True
        self.is_drawing_soul_sprites = True

    def draw(self):
        """ Calls the draw function on all the sprite lists contained in this object. """
        if self.is_drawing:
            with self.camera.activate():
                if self.is_drawing_background_sprites:
                    self.background_sprites.draw(pixelated=True)
                if self.is_drawing_character_sprites:
                    self.character_sprites.draw(pixelated=True)
                if self.is_drawing_gui_sprites:
                    self.manager.draw()
                if self.is_drawing_effects_sprites:
                    self.effects_sprites.draw(pixelated=True)
                if self.is_drawing_speech_bubble_sprites:
                    self.speech_bubble_sprites.draw(pixelated=True)
                if self.is_drawing_bullet_sprites:
                    self.bullet_sprites.draw(pixelated=True)
                for effect in self.effects:
                    if hasattr(effect, "draw") and callable(effect.draw):
                        effect.draw()
                if self.is_drawing_soul_sprites:
                    self.soul_sprites.draw(pixelated=True)


            """
            for sprite in self.effects_sprites:
                sprite.draw_hit_box(color=arcade.color.GREEN)
            for sprite in self.bullet_sprites:
                sprite.draw_hit_box(color=arcade.color.GREEN)
            for sprite in self.soul_sprites:
                sprite.draw_hit_box(color=arcade.color.GREEN)
            """

    def enable_drawing(self):
        """
        Activates the draw loop.
        :return: None
        """
        self.is_drawing = True

    def disable_drawing(self):
        """
        Disables the draw loop.
        :return: None
        """
        self.is_drawing = False

    def game_over(self):
        """
        Disables the draw loop for all sprites except soul-related sprites.
        :return: None
        """
        self.is_drawing_background_sprites = False
        self.is_drawing_character_sprites = False
        self.is_drawing_gui_sprites = False
        self.is_drawing_effects_sprites = False
        self.is_drawing_speech_bubble_sprites = False
        self.is_drawing_bullet_sprites = False
        self.is_drawing_soul_sprites = True

    def resume_game(self):
        """
        Re-enables the draw loop for all sprites.
        :return: None
        """
        self.is_drawing_background_sprites = True
        self.is_drawing_character_sprites = True
        self.is_drawing_gui_sprites = True
        self.is_drawing_effects_sprites = True
        self.is_drawing_speech_bubble_sprites = True
        self.is_drawing_bullet_sprites = True
        self.is_drawing_soul_sprites = True


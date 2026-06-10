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

    def draw(self):
        """ Calls the draw function on all the sprite lists contained in this object. """
        with self.camera.activate():
            self.background_sprites.draw(pixelated=True)
            self.character_sprites.draw(pixelated=True)
            self.manager.draw()
            self.effects_sprites.draw(pixelated=True)
            self.speech_bubble_sprites.draw(pixelated=True)
            self.bullet_sprites.draw(pixelated=True)
            for effect in self.effects:
                if hasattr(effect, "draw") and callable(effect.draw):
                    effect.draw()
            self.soul_sprites.draw(pixelated=True)


            """
            for sprite in self.effects_sprites:
                sprite.draw_hit_box(color=arcade.color.GREEN)
            for sprite in self.soul_sprites:
                sprite.draw_hit_box(color=arcade.color.GREEN)
            for sprite in self.bullet_sprites:
                sprite.draw_hit_box(color=arcade.color.GREEN)
            """


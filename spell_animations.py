from arcade import Sprite

from graphics_objects import MultiSpriteAnimation, AnimatedSprite


class IceShockAnimation(MultiSpriteAnimation):
    def __init__(self, center_x: int, center_y: int):
        sprites = [
            AnimatedSprite(Sprite(path_or_texture="assets/sprites/effects/snowflake.png", scale=1.0), 1),
            AnimatedSprite(Sprite(path_or_texture="assets/sprites/effects/snowflake.png", scale=1.0), 2),
            AnimatedSprite(Sprite(path_or_texture="assets/sprites/effects/snowflake.png", scale=1.0), 3),
            AnimatedSprite(Sprite(path_or_texture="assets/sprites/effects/snowflake.png", scale=0.5), 4),
            AnimatedSprite(Sprite(path_or_texture="assets/sprites/effects/snowflake.png", scale=0.5), 5),
            AnimatedSprite(Sprite(path_or_texture="assets/sprites/effects/snowflake.png", scale=0.5), 6),
            AnimatedSprite(Sprite(path_or_texture="assets/sprites/effects/snowflake.png", scale=0.5), 7),
            AnimatedSprite(Sprite(path_or_texture="assets/sprites/effects/snowflake.png", scale=0.5), 8),
            AnimatedSprite(Sprite(path_or_texture="assets/sprites/effects/snowflake.png", scale=0.5), 9),
            AnimatedSprite(Sprite(path_or_texture="assets/sprites/effects/snowflake.png", scale=0.5), 10),
            AnimatedSprite(Sprite(path_or_texture="assets/sprites/effects/snowflake.png", scale=0.5), 11),
            AnimatedSprite(Sprite(path_or_texture="assets/sprites/effects/snowflake.png", scale=0.5), 12),
            AnimatedSprite(Sprite(path_or_texture="assets/sprites/effects/snowflake.png", scale=0.5), 13),
            AnimatedSprite(Sprite(path_or_texture="assets/sprites/effects/snowflake.png", scale=0.5), 14),
            AnimatedSprite(Sprite(path_or_texture="assets/sprites/effects/snowflake.png", scale=0.5), 15),
            AnimatedSprite(Sprite(path_or_texture="assets/sprites/effects/snowflake.png", scale=0.5), 16),
            AnimatedSprite(Sprite(path_or_texture="assets/sprites/effects/snowflake.png", scale=0.5), 17),
            AnimatedSprite(Sprite(path_or_texture="assets/sprites/effects/snowflake.png", scale=0.5), 18),
            AnimatedSprite(Sprite(path_or_texture="assets/sprites/effects/snowflake.png", scale=0.5), 19),
            AnimatedSprite(Sprite(path_or_texture="assets/sprites/effects/snowflake.png", scale=0.5), 20),
            AnimatedSprite(Sprite(path_or_texture="assets/sprites/effects/snowflake.png", scale=0.5), 21)
        ]

        super().__init__(sprites, 1.0)

    def update(self):


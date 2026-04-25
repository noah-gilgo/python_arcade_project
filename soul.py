import random

import arcade
from arcade.hitbox import HitBox

import player_character
from bullet_board import BulletBoard


class Soul(arcade.Sprite):
    """ SOUL Class """
    def __init__(self, player_with_soul: player_character.PlayerCharacter, battle_controller):
        super().__init__(
            center_x=player_with_soul.center_x,
            center_y=player_with_soul.center_y,
            scale=2.0
        )
        self.textures = [
            arcade.load_texture("assets/sprites/soul/battle_soul.png"),
            arcade.load_texture("assets/sprites/soul/battle_soul_damaged.png")
        ]

        self.set_texture(0)

        self.hit_box = HitBox(
            points=[
                (-4.14, -10.0),
                ( 4.14, -10.0),
                (10.0, -4.14),
                (10.0,  4.14),
                ( 4.14, 10.0),
                (-4.14, 10.0),
                (-10.0,  4.14),
                (-10.0, -4.14),
            ],
            position=(
                self.center_x,
                self.center_y
            )
        )


        self.controller = battle_controller

        self.movement_speed = 4.0

        self.visible = False

        # Variables used by the animation that moves the soul to the center of the bullet board.
        self.player_with_soul_coordinates = (self.center_x, self.center_y)
        self.bullet_board_center_coordinates = (0.0, 0.0)
        self.moving_soul_to_bullet_board = False
        self.moving_soul_to_bullet_board_animation_duration = 0.6
        self.total_distance_to_move_soul_x = 1
        self.total_distance_to_move_soul_y = 1
        self.moving_soul_to_bullet_board_animation_time = 0.0

        # Controls whether or not the player can move the soul by pressing the directional buttons.
        self.soul_movement_enabled = False

        # The default invincibility duration after the soul gets hit.
        self.invincibility_after_taking_damage_duration = 1.2

        # A timer tracking how much longer the soul should remain invincible after taking damage.
        self.invincibility_after_taking_damage_time = 0.0

        # The player hurt sound.
        self.player_hurt_sound = arcade.load_sound("assets/audio/battle/player_character/common/snd_hurt1.wav", False)

    def enable_soul_movement(self):
        self.soul_movement_enabled = True

    def disable_soul_movement(self):
        self.soul_movement_enabled = False

    def move_to_bullet_board(self, bullet_board: BulletBoard):
        self.moving_soul_to_bullet_board = True
        self.moving_soul_to_bullet_board_animation_time = 0.0
        self.bullet_board_center_coordinates = bullet_board.get_center_coordinates()
        self.visible = True
        self.total_distance_to_move_soul_x = self.bullet_board_center_coordinates[0] - \
                                             self.player_with_soul_coordinates[0]
        self.total_distance_to_move_soul_y = self.bullet_board_center_coordinates[1] - \
                                             self.player_with_soul_coordinates[1]

    def update_soul_speed(self):
        # Calculate speed based on the keys pressed
        self.change_x = 0
        self.change_y = 0
        movement_speed = self.movement_speed

        # If the player is holding down C, make them move slower.
        if self.controller.x_pressed:
            movement_speed /= 2

        if self.controller.up_pressed and not self.controller.down_pressed:
            self.change_y = movement_speed
        elif self.controller.down_pressed and not self.controller.up_pressed:
            self.change_y = -movement_speed
        if self.controller.left_pressed and not self.controller.right_pressed:
            self.change_x = -movement_speed
        elif self.controller.right_pressed and not self.controller.left_pressed:
            self.change_x = movement_speed

        self.center_x += self.change_x
        self.center_y += self.change_y

    def update(self, delta_time):
        if self.moving_soul_to_bullet_board: # If the soul is being moved to/from the bullet board
            self.moving_soul_to_bullet_board_animation_time += delta_time
            distance_ratio = delta_time / self.moving_soul_to_bullet_board_animation_duration
            distance_to_move_soul_x = self.total_distance_to_move_soul_x * distance_ratio
            distance_to_move_soul_y = self.total_distance_to_move_soul_y * distance_ratio
            self.center_x += distance_to_move_soul_x
            self.center_y += distance_to_move_soul_y
            if self.moving_soul_to_bullet_board_animation_time >= self.moving_soul_to_bullet_board_animation_duration:
                # Terminate the soul movement animation
                self.center_x = self.bullet_board_center_coordinates[0]
                self.center_y = self.bullet_board_center_coordinates[1]
                self.moving_soul_to_bullet_board = False
                self.enable_soul_movement()
            return
        else: # The default movement for the soul.
            if self.soul_movement_enabled:
                self.update_soul_speed()

        # Checks if the soul is colliding with any bullets.
        # If the soul is invincible, don't bother checking the collision.
        if self.invincibility_after_taking_damage_time <= 0.0:
            bullets_colliding = self.collides_with_list(self.controller.sprites_and_effects_collection.bullet_sprites)
            if len(bullets_colliding) > 0:
                self.invincibility_after_taking_damage_time = self.invincibility_after_taking_damage_duration
                # The first bullet in the list of bullets overlapping the soul will be considered the first to hit it
                colliding_bullet = bullets_colliding[0]
                players_not_knocked = []
                for player in self.controller.players:
                    if player.hp > 0:
                        players_not_knocked.append(player)
                if len(players_not_knocked) > 0:
                    if colliding_bullet.targets_multiple_players:
                        base_damage_to_each_player = colliding_bullet.base_damage / 3
                        for player in players_not_knocked:
                            player.damage(
                                damage_dealt=base_damage_to_each_player,
                                element_id=colliding_bullet.element_id,
                                play_hurt_sound=False
                            )
                        self.player_hurt_sound.play()
                    else:
                        player = players_not_knocked[random.randint(0, len(players_not_knocked) - 1)]
                        player.damage(colliding_bullet.base_damage, colliding_bullet.element_id)
                else:
                    self.player_hurt_sound.play()

        else:
            # Decrement the invincibility timer if it is above zero.
            self.invincibility_after_taking_damage_time -= delta_time
            if self.invincibility_after_taking_damage_time <= 0.0:
                self.invincibility_after_taking_damage_time = 0.0
            else:
                # Animate the soul in its invincibility frame state.
                soul_sprite_is_translucent = int(self.invincibility_after_taking_damage_time / 0.1) % 2
                self.set_texture(soul_sprite_is_translucent)

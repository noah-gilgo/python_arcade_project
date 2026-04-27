import random

import arcade
from arcade import Sprite
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

        self.controller = battle_controller

        self.textures = [
            arcade.load_texture("assets/sprites/soul/battle_soul.png"),
            arcade.load_texture("assets/sprites/soul/battle_soul_damaged.png")
        ]

        self.set_texture(0)

        # Load the graze sprite and all of its child textures
        self.graze_sprite = Sprite(
            scale=2.0,
            center_x=self.center_x,
            center_y=self.center_y,
        )

        self.graze_sprite.textures = [
            arcade.load_texture("assets/sprites/soul/graze/soul_graze_1.png"),
            arcade.load_texture("assets/sprites/soul/graze/soul_graze_2.png"),
            arcade.load_texture("assets/sprites/soul/graze/soul_graze_3.png"),
            arcade.load_texture("assets/sprites/soul/graze/soul_graze_4.png")
        ]

        self.graze_sprite.set_texture(0)

        self.graze_sprite.visible = False

        self.controller.sprites_and_effects_collection.soul_sprites.append(self.graze_sprite)

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

        # A timer tracking the amount of time that has passed since the last successful graze.
        self.time_since_last_graze = 1.0

        # A variable tracking if the graze area is still in range of previously grazed bullets.
        # If so, the graze sprite should remain visible.
        self.graze_hitbox_still_touching_grazed_bullets = False

        # A variable tracking if the graze area left the area of grazed bullets and is only touching previously grazed bullets.
        self.graze_hitbox_touching_grazed_bullets_after_leaving_them = False

        # Load sounds used by soul events.
        self.player_hurt_sound = arcade.load_sound("assets/audio/battle/player_character/common/snd_hurt1.wav", False)
        self.graze_sound = arcade.load_sound("assets/audio/battle/player_character/common/snd_graze.wav", False)

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

    def move_soul_with_player_controls(self):
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

    def check_if_soul_is_colliding_with_bullets(self, delta_time):
        """
        Checks if soul is colliding with bullets.
        If it is, damage a random player depending on the programming of the bullet and make the soul temporarily
        invincible, if the soul isn't temporarily invincible already.
        :param delta_time: the amount of time elapsed since the last frame
        :return: None
        """

        # Only check if bullets are colliding with the soul if the soul is not invincible.
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
                        player_to_be_damaged = players_not_knocked[random.randint(0, len(players_not_knocked) - 1)]
                        player_to_be_damaged.damage(colliding_bullet.base_damage, colliding_bullet.element_id)
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

    def set_texture_for_graze_sprite(self):
        """
        Sets the texture for the graze sprite depending on the time since the last successful graze.
        :return: None
        """
        if self.graze_hitbox_touching_grazed_bullets_after_leaving_them:
            self.graze_sprite.visible = True
            self.graze_sprite.set_texture(3)
            return

        if self.time_since_last_graze < 0.1:
            self.graze_sprite.visible = True
            self.graze_sprite.set_texture(0)
        elif 0.1 < self.time_since_last_graze < 0.14:
            self.graze_sprite.visible = True
            self.graze_sprite.set_texture(1)
        elif 0.14 < self.time_since_last_graze < 0.16:
            self.graze_sprite.visible = True
            self.graze_sprite.set_texture(2)
        elif 0.16 < self.time_since_last_graze < 0.18:
            self.graze_sprite.visible = True
            self.graze_sprite.set_texture(3)
        else:
            self.graze_sprite.visible = False

    def check_if_graze_area_is_colliding_with_bullets(self, delta_time):
        """
        Check if the graze area is colliding with bullets.
        If it is, add the sum of the TP from the bullets to the TP meter, set them all to have been grazed and play
        the graze sound effect.
        :param delta_time: the amount of time elapsed since the last frame
        :return: None
        """
        tp_gained = 0
        touching_bullets = False

        # Only check if bullets are colliding with the graze area if the soul is not invincible.
        if self.invincibility_after_taking_damage_time <= 0.0:
            bullets_colliding = self.graze_sprite.collides_with_list(self.controller.sprites_and_effects_collection.bullet_sprites)
            if len(bullets_colliding) > 0:
                touching_bullets = True
                # Add up the total TP from the non-grazed bullets.
                for bullet in bullets_colliding:
                    if not bullet.has_been_grazed:
                        tp_gained += bullet.tp_gain_when_grazed
                        bullet.has_been_grazed = True
                # If the total TP from the grazing exceeds 0, add it to the meter and play the graze sound.
                if tp_gained > 0:
                    self.controller.add_tp_to_meter(tp_gained)
                    self.graze_sound.play()
                    self.time_since_last_graze = 0.0
                    self.graze_hitbox_still_touching_grazed_bullets = True
                    self.graze_hitbox_touching_grazed_bullets_after_leaving_them = False
                    self.set_texture_for_graze_sprite()
                if not self.graze_hitbox_still_touching_grazed_bullets:
                    self.graze_hitbox_touching_grazed_bullets_after_leaving_them = True
            else:
                self.graze_hitbox_still_touching_grazed_bullets = False
                self.graze_hitbox_touching_grazed_bullets_after_leaving_them = False
            self.set_texture_for_graze_sprite()

        if not touching_bullets:
            self.graze_hitbox_still_touching_grazed_bullets = False
            self.graze_hitbox_touching_grazed_bullets_after_leaving_them = False
            self.set_texture_for_graze_sprite()

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
        else: # The default movement for the soul.
            if self.soul_movement_enabled:
                self.move_soul_with_player_controls()

            # Perform collision checking
            self.check_if_soul_is_colliding_with_bullets(delta_time)
            self.check_if_graze_area_is_colliding_with_bullets(delta_time)

        # Set the center of the graze sprite to the center of the soul sprite
        self.graze_sprite.center_x = self.center_x
        self.graze_sprite.center_y = self.center_y

        # Increment the time since last graze timer if it is less than 1 second.
        if self.time_since_last_graze < 1.0 and not self.graze_hitbox_still_touching_grazed_bullets:
            self.time_since_last_graze += delta_time

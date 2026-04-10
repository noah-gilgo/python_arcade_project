import arcade

import player_character
from bullet_board import BulletBoard


class Soul(arcade.Sprite):
    """ SOUL Class """
    def __init__(self, player_with_soul: player_character.PlayerCharacter, battle_controller):
        super().__init__(
            path_or_texture="assets/sprites/soul/soul.png",
            center_x=player_with_soul.center_x,
            center_y=player_with_soul.center_y,
            scale=2.0
        )

        self.controller = battle_controller

        self.movement_speed = 5.0

        self.visible = False

        # Variables used by the animation that moves the soul to the center of the bullet board.
        self.player_with_soul_coordinates = (self.center_x, self.center_y)
        self.bullet_board_center_coordinates = (0.0, 0.0)
        self.moving_soul_to_bullet_board = False
        self.moving_soul_to_bullet_board_animation_duration = 1.0
        self.total_distance_to_move_soul_x = 1
        self.total_distance_to_move_soul_y = 1
        self.moving_soul_to_bullet_board_animation_time = 0.0

        self.soul_movement_enabled = False

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

        if self.controller.up_pressed and not self.controller.down_pressed:
            self.change_y = self.movement_speed
        elif self.controller.down_pressed and not self.controller.up_pressed:
            self.change_y = -self.movement_speed
        if self.controller.left_pressed and not self.controller.right_pressed:
            self.change_x = -self.movement_speed
        elif self.controller.right_pressed and not self.controller.left_pressed:
            self.change_x = self.movement_speed

        self.center_x += self.change_x
        self.center_y += self.change_y

    def update(self, delta_time):
        if self.moving_soul_to_bullet_board:
            self.moving_soul_to_bullet_board_animation_time += delta_time
            print(self.moving_soul_to_bullet_board_animation_time)
            distance_ratio = delta_time / self.moving_soul_to_bullet_board_animation_duration
            distance_to_move_soul_x = self.total_distance_to_move_soul_x * distance_ratio
            distance_to_move_soul_y = self.total_distance_to_move_soul_y * distance_ratio
            self.center_x += distance_to_move_soul_x
            self.center_y += distance_to_move_soul_y
            if self.moving_soul_to_bullet_board_animation_time >= self.moving_soul_to_bullet_board_animation_duration:
                self.center_x = self.bullet_board_center_coordinates[0]
                self.center_y = self.bullet_board_center_coordinates[1]
                self.moving_soul_to_bullet_board = False
                self.enable_soul_movement()
            return
        else:
            if self.soul_movement_enabled:
                self.update_soul_speed()

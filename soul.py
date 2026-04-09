import arcade

import player_character
from bullet_board import BulletBoard


class Soul(arcade.Sprite):
    """ SOUL Class """
    def __init__(self, player_with_soul: player_character.PlayerCharacter):
        super().__init__(
            path_or_texture="assets/sprites/soul/soul.png",
            center_x=player_with_soul.center_x,
            center_y=player_with_soul.center_y,
            scale=2.0
        )

        self.movement_speed = 3.0

        self.visible = False

        # Track the current state of what key is pressed
        self.left_pressed = False
        self.right_pressed = False
        self.up_pressed = False
        self.down_pressed = False

        # Variables used by the animation that moves the soul to the center of the bullet board.
        self.player_with_soul_coordinates = (self.center_x, self.center_y)
        self.bullet_board_center_coordinates = (0.0, 0.0)
        self.moving_soul_to_bullet_board = False
        self.moving_soul_to_bullet_board_animation_duration = 0.5
        self.total_distance_to_move_soul_x = 1
        self.total_distance_to_move_soul_y = 1
        self.moving_soul_to_bullet_board_animation_time = 0.0

    def move_to_bullet_board(self, bullet_board: BulletBoard):
        self.bullet_board_center_coordinates = bullet_board.get_center_coordinates()
        self.visible = True
        self.total_distance_to_move_soul_x = self.bullet_board_center_coordinates[0] - \
                                             self.player_with_soul_coordinates[0]
        self.total_distance_to_move_soul_y = self.bullet_board_center_coordinates[1] - \
                                             self.player_with_soul_coordinates[1]
        self.moving_soul_to_bullet_board = True

    def update_soul_speed(self):
        # Calculate speed based on the keys pressed
        self.change_x = 0
        self.change_y = 0

        if self.up_pressed and not self.down_pressed:
            self.change_y = self.movement_speed
        elif self.down_pressed and not self.up_pressed:
            self.change_y = -self.movement_speed
        if self.left_pressed and not self.right_pressed:
            self.change_x = -self.movement_speed
        elif self.right_pressed and not self.left_pressed:
            self.change_x = self.movement_speed

        self.velocity = (self.change_x, self.change_y)

    def update(self, delta_time: float = 1/60):
        if self.moving_soul_to_bullet_board:
            self.moving_soul_to_bullet_board_animation_time += delta_time
            distance_ratio = delta_time / self.moving_soul_to_bullet_board_animation_duration
            distance_to_move_soul_x = self.total_distance_to_move_soul_x * distance_ratio
            distance_to_move_soul_y = self.total_distance_to_move_soul_y * distance_ratio
            self.center_x += distance_to_move_soul_x
            self.center_y += distance_to_move_soul_y
            if self.moving_soul_to_bullet_board_animation_time >= self.moving_soul_to_bullet_board_animation_duration:
                self.center_x = self.bullet_board_center_coordinates[0]
                self.center_y = self.bullet_board_center_coordinates[1]
                self.moving_soul_to_bullet_board_animation_time = 0.0
                self.moving_soul_to_bullet_board = False
            return

        """
        if key == arcade.key.UP:
            self.up_pressed = True
            self.update_soul_speed()
        elif key == arcade.key.DOWN:
            self.down_pressed = True
            self.update_soul_speed()
        elif key == arcade.key.LEFT:
            self.left_pressed = True
            self.update_soul_speed()
        elif key == arcade.key.RIGHT:
            self.right_pressed = True
            self.update_soul_speed()
        """
import arcade


class Soul(arcade.Sprite):
    """ SOUL Class """
    def __init__(self, center_x: float, center_y: float, angle: float = 0.0):
        super().__init__(
            path_or_texture="assets/sprites/soul/soul.png",
            center_x=center_x,
            center_y=center_y,
            angle=angle,
            scale=2.0
        )

        self.movement_speed = 3.0

        # Track the current state of what key is pressed
        self.left_pressed = False
        self.right_pressed = False
        self.up_pressed = False
        self.down_pressed = False

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



    def on_update(self, key, delta_time: float = 1/60):
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
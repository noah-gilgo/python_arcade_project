import arcade


class LinesBehindCharacterClamshellButtonsAnimation:
    def __init__(self, layout):
        self.layout = layout
        self.layout_width = self.layout.width
        self.layout_height = self.layout.height
        self.layout_start_x = self.layout.left
        self.layout_end_x = self.layout.right
        self.layout_start_y = self.layout.bottom
        self.layout_end_y = self.layout.top

        self.lines_coming_from_left = []
        self.lines_coming_from_right = []
        self.character_color_r = layout.player_character.battle_ui_color.r
        self.character_color_g = layout.player_character.battle_ui_color.g
        self.character_color_b = layout.player_character.battle_ui_color.b
        self.line_lifetime = 2
        self.velocity_magnifier = 0.1
        self.alpha_loss_magnifier = 4

        self.is_terminated = True

        for i in range(6):
            time = (self.line_lifetime * (i / 6))
            distance = ((time ** 2) * (self.layout_width * self.velocity_magnifier)) + self.layout_start_x
            start_x = distance
            end_x = distance
            alpha = min(255, int(max(255 - (distance * self.alpha_loss_magnifier), 0)))
            self.lines_coming_from_left.append(
                [start_x, self.layout_start_y, end_x, self.layout_end_y,
                 [self.character_color_r, self.character_color_g, self.character_color_b, alpha], 5, time]
            )

        for i in range(6):
            time = (self.line_lifetime * (i / 6))
            distance = (self.layout_width - ((time ** 2) * (self.layout_width * self.velocity_magnifier))) + self.layout_start_x
            start_x = distance
            end_x = distance
            alpha = min(255, int(max(255 - ((self.layout_width - distance) * self.alpha_loss_magnifier), 0)))
            self.lines_coming_from_right.append(
                [start_x, self.layout_start_y, end_x, self.layout_end_y,
                 [self.character_color_r, self.character_color_g, self.character_color_b, alpha], 5, time]
            )

    def update_animation(self, delta_time: float):
        """ Updates the animated lines data behind the battle HUD action buttons. """
        if self.layout.is_focused:
            for line in self.lines_coming_from_left:
                # Check if the line is older than the max line lifetime
                if line[6] >= self.line_lifetime:
                    # Set line back to initial conditions
                    line[0] = 0
                    line[2] = 0
                    line[4][3] = 255
                    line[6] -= self.line_lifetime
                else:
                    # Progress the line animation
                    line[6] += delta_time
                    distance = (line[6] ** 2) * (self.layout_width * self.velocity_magnifier)
                    line[0] = distance
                    line[2] = distance
                    line[4][3] = min(255, int(max(255 - (distance * self.alpha_loss_magnifier), 0)))

            for line in self.lines_coming_from_right:
                # Check if the line is older than the max line lifetime
                if line[6] >= self.line_lifetime:
                    # Set line back to initial conditions
                    line[0] = self.layout_width
                    line[2] = self.layout_width
                    line[4][3] = 255
                    line[6] -= self.line_lifetime
                else:
                    # Progress the line animation
                    line[6] += delta_time
                    distance = self.layout_width - ((line[6] ** 2) * (self.layout_width * self.velocity_magnifier))
                    line[0] = distance
                    line[2] = distance
                    line[4][3] = min(255, int(max(255 - ((self.layout_width - distance) * self.alpha_loss_magnifier), 0)))

    def draw(self):
        if self.layout.is_focused:
            for line in self.lines_coming_from_left:
                arcade.draw_line(line[0], line[1], line[2], line[3], line[4], line[5])
            for line in self.lines_coming_from_right:
                arcade.draw_line(line[0], line[1], line[2], line[3], line[4], line[5])

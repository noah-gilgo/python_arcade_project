import settings


def initialize_holy_arc(number_of_players: int = 3):
    """
    Generates a list of tuples representing the starting positions of each of the player characters in battle.
    Mathematical function for the arc is x = (y^2)/768, starting_y <= y <= ending_y.
    :param number_of_players: Number of player characters present in battle.
    :return: A list of tuples representing the positions of the characters in battle.
    """

    holy_arc = []

    starting_y = int(settings.WINDOW_CENTER_Y + (settings.WINDOW_HEIGHT * .3))
    ending_y = int(settings.WINDOW_CENTER_Y - (settings.WINDOW_HEIGHT * .3))

    delta_y = starting_y - ending_y

    y = starting_y

    # This corner case avoids a divide by 0 error when calculating the increment variable.
    if number_of_players == 1:
        y = settings.WINDOW_CENTER_Y
        return [(
            int((((y - settings.WINDOW_CENTER_Y) ** 2) / 768) + (settings.WINDOW_WIDTH / 8)),
            y
        )]

    increment = int(delta_y / (number_of_players - 1))

    for i in range(number_of_players):
        position = (
            int((((y - settings.WINDOW_CENTER_Y) ** 2) / 768) + (settings.WINDOW_WIDTH / 8)),
            y
        )
        y -= increment
        holy_arc.append(position)

    return holy_arc

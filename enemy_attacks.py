
class EnemyIndividualAttack:
    """
    The attack an individual enemy contributes to an enemy turn.
    Receives (optionally) the number of active opponents as a parameter to modify the attack based on concurrent
    attacks. Often contains a multitude of bullet patterns, but it doesn't really have to. It's just a possible
    contribution that an enemy can make to a combo attack.
    """

    def __init__(self, unique_enemies: int = 1):
        """
        Initializes the initial conditions for the attack.
        :param unique_enemies: an optional parameter indicating how many unique enemies are attacking. Can be used to
        modify the behavior of the attack depending on the unique number of enemies.
        """
        self.unique_enemies = unique_enemies
        self.time = 0.0

    def update_animation(self):
        """
        Updates a multitude of bullet patterns. Behavior can be coded to vary based on the number of unique enemies.
        :return: None
        """
        pass


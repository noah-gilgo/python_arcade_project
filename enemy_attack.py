import non_player_character
from sprites_and_effects_collection import SpritesAndEffectsCollection


class EnemyAttack:
    """
    The attack that the enemy/combination of enemies do together to create the barrage of bullets the player has to
    avoid during the enemy turn.

    Think of EnemyIndividualAttacks as the individual contribution that each enemy makes to the actual attack they all
    do together. If a Rudinn and a Hathy attack together, the Hathy conjures a circle of hearts while the Rudinn rains
    diamonds on the bullet board. Each of them contribute an EnemyIndividualAttack which is controlled by the parameters
    of the EnemyAttack.
    """

    def __init__(self, enemies: list[non_player_character.NonPlayerCharacter],
                 sprites_and_effects_collection: SpritesAndEffectsCollection):
        """
        Initializes the initial conditions for the attack.
        :param enemies: The enemies present in battle.
        """
        self.enemies = enemies
        self.time = 0.0

        # for enemy in self.enemies:


    def update_animation(self, delta_time: float):
        """
        Updates a multitude of bullet patterns. Behavior can be coded to vary based on the number of unique enemies.
        :return: None
        """
        pass

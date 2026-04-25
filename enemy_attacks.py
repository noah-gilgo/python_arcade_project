from bullet_patterns import RainingDiamondBulletPattern
from sprites_and_effects_collection import SpritesAndEffectsCollection


class EnemyIndividualAttack:
    """
    The attack an individual enemy contributes to an enemy turn.
    Receives (optionally) the number of active opponents as a parameter to modify the attack based on concurrent
    attacks. Often contains a multitude of bullet patterns, but it doesn't really have to. It's just a possible
    contribution that an enemy can make to a combo attack.
    """

    def __init__(self, attacker, attackers: list, sprites_and_effects_collection: SpritesAndEffectsCollection):
        """
        Initializes the initial conditions for the attack.
        :param attacker: the enemy doing the attack.
        :param attackers: the enemies attacking. Can be used to modify the behavior of the attack depending on the
        unique number/types of enemies.
        """
        self.sprites_and_effects_collection = sprites_and_effects_collection
        self.attacker = attacker
        self.attackers = attackers
        self.time = 0.0
        self.bullet_patterns = []

    def update_animation(self, delta_time: float):
        """
        Updates a multitude of bullet patterns. Behavior can be coded to vary based on the number of unique enemies.
        :return: None
        """
        if len(self.bullet_patterns) > 0:
            for bullet_pattern in self.bullet_patterns:
                bullet_pattern.update_animation(delta_time)


class DefaultAttack(EnemyIndividualAttack):
    """
    Default enemy attack.
    """
    def __init__(self, attacker, attackers: list, sprites_and_effects_collection):
        super().__init__(attacker, attackers, sprites_and_effects_collection)
        self.bullet_patterns = [RainingDiamondBulletPattern()]

    def update_animation(self, delta_time: float):
        super().update_animation(delta_time)


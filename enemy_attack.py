from sprites_and_effects_collection import SpritesAndEffectsCollection


class EnemyAttack:
    """
    An individual enemy attack. Ideally just spawns a bunch of bullet patterns.

    NOTE: When spawning bullets/bullet patterns, *add them to self.bullets and self.bullet_patterns, respectively.*
    If you do this, self.terminate_attack will clean up all the bullets for you once the enemy turn ends.
    """

    def __init__(self, sprites_and_effects_collection: SpritesAndEffectsCollection, duration: float = 10.0):
        """
        Initializes the initial conditions for the attack.
        :param enemies: The enemies present in battle.
        """
        self.sprites_and_effects_collection = sprites_and_effects_collection

        self.duration = duration
        self.time = 0.0

        # All the active bullets/bullet patterns spawned by the attack
        self.bullets = []
        self.bullet_patterns = []

    def execute_attack(self):
        """
        Starts the attack. This usually sets the initial conditions for the attack.
        :return: None
        """
        pass

    def update_attack(self, delta_time: float):
        """
        Updates the attack. This is the meat and potatoes of most complex attacks that don't involve just spawning one
        or more bullet patterns at the very beginning of the attack.
        :return: None
        """
        self.time += delta_time

    def terminate_attack(self):
        """
        Ends the attack.
        :return: None
        """
        for bullet in self.bullets:
            bullet.kill()

        for bullet_pattern in self.bullet_patterns:
            bullet_pattern.terminate_animation()


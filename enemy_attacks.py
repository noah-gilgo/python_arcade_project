from bullet_board import BulletBoard
from bullet_patterns import RainingDiamondBulletPattern
from enemy_attack import EnemyAttack
from sprites_and_effects_collection import SpritesAndEffectsCollection


class RainingDiamondAttack(EnemyAttack):
    def __init__(self, sprites_and_effects_collection: SpritesAndEffectsCollection, bullet_board: BulletBoard,
                 attacker, enemies_list: list, frequency: float = 1.0):
        super().__init__(
            sprites_and_effects_collection=sprites_and_effects_collection,
            duration=10.0
        )

        self.frequency = frequency
        self.bullet_board = bullet_board
        self.attacker = attacker
        self.enemies_list = enemies_list

    def execute_attack(self):
        """
        Starts the attack.
        :return: the duration of the attack
        """
        # Find the number of unique enemy types in battle.
        number_of_unique_enemies_in_battle = get_number_of_unique_enemies_from_enemies_list(self.enemies_list)

        for enemy in self.enemies_list:
            if type(enemy) is type(self.attacker):
                if enemy is self.attacker:
                    raining_diamond_bullet_pattern = RainingDiamondBulletPattern(
                        sprites_and_effects_collection=self.sprites_and_effects_collection,
                        bullet_board=self.bullet_board,
                        frequency=1 / number_of_unique_enemies_in_battle
                    )
                    self.sprites_and_effects_collection.effects.append(raining_diamond_bullet_pattern)
                    self.bullet_patterns.append(raining_diamond_bullet_pattern)
                else:
                    break

        return 10.0


def get_number_of_unique_enemies_from_enemies_list(enemies_list: list):
    """
    Get the number of unique enemies in the enemies list.
    :param enemies_list: the enemies list to be checked
    :return: the number of unique enemies in the enemies list
    """
    enemy_types_in_battle = []
    for enemy in enemies_list:
        if type(enemy) not in enemy_types_in_battle:
            enemy_types_in_battle.append(type(enemy))

    return len(enemy_types_in_battle)



from non_player_character import NonPlayerCharacter

class EnemyAttackGenerator:
    def __init__(self, enemies: list[NonPlayerCharacter]):
        self.enemies = enemies

    def execute_enemy_attack(self):
        """
        Executes the enemy attacks.
        :return: None
        """
        for enemy in self.enemies:
            pass
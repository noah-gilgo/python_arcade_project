from act import SimpleAct


class CheckAct(SimpleAct):
    """
    The act associated with the "Check" option in the ACT menu. Displays data about the selected opponent.
    """

    def __init__(self, target, description: str = "Useless analysis"):
        super().__init__(
            name="Check",
            description=description,
            perform_act_text=target.battle_description
        )


class RudinnConvince(SimpleAct):
    def __init__(self):
        super().__init__(
            name="Convince",
            perform_act_text="* You told Rudinn to quit fighting.\n* It was utterly swayed.",
            description="Politely persuade enemy",
            mercy_percentage=100
        )


class RudinnLecture(SimpleAct):
    def __init__(self, enemies_list: list):
        super().__init__(
            name="Lecture",
            perform_act_text="* You lectured the enemies on the importance of kindness.\n* The enemies became TIRED...",
            description="Passionately lecture opponents"
        )

        self.enemies_list = enemies_list

    def perform_act(self, actor, target, dialogue_box):
        super().perform_act(actor, target, dialogue_box)
        for enemy in self.enemies_list:
            enemy.receive_tired(100.0)
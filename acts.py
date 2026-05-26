from act import SimpleAct


class RudinnConvince(SimpleAct):
    def __init__(self):
        super().__init__(
            name="Convince",
            description="You told Rudinn to quit fighting.\n* It was utterly swayed.",
            mercy_percentage=100
        )


class RudinnLecture(SimpleAct):
    def __init__(self, enemies_list: list):
        super().__init__(
            name="Lecture",
            description="* You lectured the enemies on the importance of kindness.\n* It was utterly swayed."
        )

        self.enemies_list = enemies_list

    def perform_act(self, actor, target, dialogue_box):
        super().perform_act(actor, target, dialogue_box)
        for enemy in self.enemies_list:
            enemy.receive_tired(100.0)
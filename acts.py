from act import SimpleAct, MagicUserAct
from speech_bubble import SpeechBubbleDialog


# SimpleActs

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

    def perform_act(self, actor, target, dialogue_box):
        super().perform_act(actor, target, dialogue_box)
        target.assign_speech_bubble_dialog_this_turn(
            SpeechBubbleDialog(
                text="Yeah that\nmakes sense.",
                row_count=2,
                column_count=12,
                actor=target
            )
        )


class RudinnLecture(SimpleAct):
    def __init__(self, enemies_list: list):
        super().__init__(
            name="Lecture",
            perform_act_text="You lectured the enemies on the importance of kindness.\nThe enemies became TIRED...",
            description="Passionately lecture opponents"
        )

        self.enemies_list = enemies_list

    def perform_act(self, actor, target, dialogue_box):
        super().perform_act(actor, target, dialogue_box)
        for enemy in self.enemies_list:
            enemy.receive_tired(100.0)
            enemy.assign_speech_bubble_dialog_this_turn(
                SpeechBubbleDialog(
                    text="(Yawn)...\nWhat? OK..",
                    row_count=2,
                    column_count=10,
                    actor=enemy
                )
            )


# Magic user acts

class NoelleRudinnAction1(MagicUserAct):
    def __init__(self, player):
        from non_player_character import Rudinn  # TODO: fix this

        super().__init__(
            player=player,
            enemy_type=Rudinn,
            description="Traumatize playing card\nSPARE 50%",
            perform_act_text="Noelle cuts Rudinn card paper snowflakes!\nThey are mortified but impressed!",
            mercy_percentage=50
        )

    def perform_act(self, actor, target, dialogue_box):
        super().perform_act(actor, target, dialogue_box)
        target.assign_speech_bubble_dialog_this_turn(
            SpeechBubbleDialog(
                text="That's what the\nKnight did to my\ncousin Phil",
                row_count=3,
                column_count=16,
                actor=target
            )
        )

class RalseiRudinnAction1(MagicUserAct):
    def __init__(self, player):
        from non_player_character import Rudinn

        super().__init__(
            player=player,
            enemy_type=Rudinn,
            description="Offer relief from duty\nSPARE 50%",
            perform_act_text="Ralsei promises that his castle town has suites suited for all suits.",
            mercy_percentage=50
        )

    def perform_act(self, actor, target, dialogue_box):
        super().perform_act(actor, target, dialogue_box)
        target.assign_speech_bubble_dialog_this_turn(
            SpeechBubbleDialog(
                text="My last house\nwasn't a full\none, but...",
                row_count=3,
                column_count=13,
                actor=target
            )
        )

class SusieRudinnAction1(MagicUserAct):
    def __init__(self, player):
        from non_player_character import Rudinn

        super().__init__(
            player=player,
            enemy_type=Rudinn,
            description="Wisecrack,\nSPARE 50%",
            perform_act_text="Susie tries to make a joke about UNO and Xboxes.",
            mercy_percentage=30
        )

    def perform_act(self, actor, target, dialogue_box):
        super().perform_act(actor, target, dialogue_box)
        target.assign_speech_bubble_dialog_this_turn(
            SpeechBubbleDialog(
                text="Oh yeah, never\nheard that one\nbefore...",
                row_count=3,
                column_count=14,
                actor=target
            )
        )

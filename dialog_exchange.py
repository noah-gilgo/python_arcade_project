from dialogue_box import BattleTextBoxDialog
from speech_bubble import SpeechBubbleDialog, SpeechBubble


class DialogExchange:
    """
    Stores instances of SpeechBubbleDialog/TextBoxDialog objects to be called this turn during the dialog segment before
    the enemy attacks.
    """
    def __init__(self, dialog_instances: list[SpeechBubbleDialog | BattleTextBoxDialog | None],
                 battle_textbox,
                 sprites_and_effects_collection):
        self.dialog_instances = dialog_instances
        self.battle_textbox = battle_textbox
        self.sprites_and_effects_collection = sprites_and_effects_collection

        self.currently_active_speech_bubbles = []

    def execute_next_dialog(self):
        """
        Executes the next dialog in the dialog segment. If none are left, return False.
        :return: False if there are no remaining dialogs, otherwise True
        """
        self.battle_textbox.clear_dialog()

        if len(self.currently_active_speech_bubbles) > 0:
            for speech_bubble in self.currently_active_speech_bubbles:
                speech_bubble.despawn_speech_bubble()

        if len(self.dialog_instances) == 0:
            return False
        else:
            dialog_instance = self.dialog_instances.pop(0)

            if isinstance(dialog_instance, SpeechBubbleDialog):
                speech_bubble = SpeechBubble(dialog_instance, self.sprites_and_effects_collection)
                self.currently_active_speech_bubbles.append(speech_bubble)
                return speech_bubble
            elif isinstance(dialog_instance, BattleTextBoxDialog):
                self.battle_textbox.load_dialog(dialog_instance)
                return True
            else:
                return True

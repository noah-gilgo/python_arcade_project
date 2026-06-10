from dialogue_box import TextBoxDialog
from speech_bubble import SpeechBubbleDialog, SpeechBubble
from sprites_and_effects_collection import SpritesAndEffectsCollection


class DialogExchange:
    """
    Stores instances of SpeechBubbleDialog/TextBoxDialog objects to be called this turn during the dialog segment before
    the enemy attacks.
    """
    def __init__(self, dialog_instances: list[SpeechBubbleDialog | TextBoxDialog | None],
                 battle_textbox,
                 sprites_and_effects_collection):
        self.dialog_instances = dialog_instances
        self.battle_textbox = battle_textbox
        self.sprites_and_effects_collection = sprites_and_effects_collection

    def execute_next_dialog(self):
        """
        Executes the next dialog in the dialog segment. If none are left, return None.
        :return: None if there are no remaining dialogs, otherwise the dialog instance or True
        """
        if len(self.dialog_instances) == 0:
            return None
        else:
            dialog_instance = self.dialog_instances.pop(0)

            if isinstance(dialog_instance, SpeechBubbleDialog):
                return SpeechBubble(dialog_instance, self.sprites_and_effects_collection)
            elif isinstance(dialog_instance, TextBoxDialog):
                self.battle_textbox.load_dialog(dialog_instance)
                return True

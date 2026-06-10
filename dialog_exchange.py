from speech_bubble import SpeechBubbleDialog


class DialogExchange:
    """ Stores instances of  """
    def __init__(self, dialog_instances: list):
        self.dialog_instances = dialog_instances

    def execute_next_dialog(self):
        if len(self.dialog_instances) == 0:
            return None
        else:
            dialog_instance = self.dialog_instances.pop(0)

            if isinstance(dialog_instance, SpeechBubbleDialog):
                return SpeechBubbleDialog()
            else:
                pass

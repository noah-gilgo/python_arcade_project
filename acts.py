from dialogue_box import TextBoxDialog


class SimpleAct:
    """
    A simple act. Many acts in Deltarune battles follow a format where text is displayed related to the act and
    the enemy is granted a certain percentage of mercy/tired. This object encapsulates this simple kind of act, which
    does not require any additional animations, player interactions or cause any changes to the enemy behavior.
    """
    def __init__(self):
        self.name = "Placeholder Act Name"  # The name of the act in the ACT menu.
        self.description_text = "You just performed an act!"  # Dialog box text when the act is performed
        self.mercy_percentage = 0.1  # Mercy granted to the enemy the act is performed on
        self.tired_percentage = 0.1  # Tired granted to the enemy the act is performed on
        self.actor_animation_state = ""  # The animation the actor is briefly given when they perform the act.

    def perform_act(self, actor, target, dialogue_box):
        """
        Executes the act.
        :return: None
        """

        if self.actor_animation_state:
            actor.set_animation_state(self.actor_animation_state)

        dialogue_box.load_dialog(TextBoxDialog(text=self.description_text))



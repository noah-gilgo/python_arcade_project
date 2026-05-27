from dialogue_box import TextBoxDialog


class Act:
    """
    An abstract Act method. The parent class that all types of acts should inherit from.
    """
    def __init__(self, name: str = "Placeholder Act Name", description: str = "Performs an act", tp_cost: float = 0.0):
        self.name = name  # The name of the act in the ACT menu.
        self.description = description  # The description of the act displayed in the ACT menu when hovered over.
        self.tp_cost = tp_cost  # It's rare, but some acts have a TP cost.


class SimpleAct(Act):
    """
    A simple act. Many acts in Deltarune battles follow a format where text is displayed related to the act and
    the enemy is granted a certain percentage of mercy/tired. This object encapsulates this simple kind of act, which
    does not require any additional animations, player interactions or cause any changes to the enemy behavior.
    """
    def __init__(
            self,
            name: str = "Placeholder Act Name",
            description: str = "Performs an act",
            tp_cost: float = 0.0,
            perform_act_text: str = "You just performed an act!",
            mercy_percentage: float = 0.0,
            tired_percentage: float = 0.0,
            actor_animation_state: str = ""
    ):
        super().__init__(name, description, tp_cost)
        self.perform_act_text = perform_act_text  # Dialog box text when the act is performed
        self.mercy_percentage = mercy_percentage  # Mercy granted to the enemy the act is performed on (between 0 and 100)
        self.tired_percentage = tired_percentage  # Tired granted to the enemy the act is performed on (between 0 and 100)
        self.actor_animation_state = actor_animation_state  # The animation the actor is briefly given when they perform the act.

    def perform_act(self, actor, target, dialogue_box):
        """
        Executes the act.
        :return: None
        """

        # TODO: add logic to decrease TP from meter if the act requires TP

        # If there is a valid actor animation state associated with the act, set it.
        # Otherwise, just use the battle_act animation (if the actor has it.)
        if self.actor_animation_state and self.actor_animation_state in actor.animations_by_state:
            actor.set_animation_state(self.actor_animation_state)
        else:
            if "battle_act" in actor.animations_by_state:
                actor.set_animation_state("battle_act")

        # Load the act dialogue into the dialogue box, if there is any.
        if self.perform_act_text:
            dialogue_box.load_dialog(TextBoxDialog(text="* " + self.perform_act_text))

        # If the mercy/tired percentages are greater than zero, have the target receive them.
        if self.mercy_percentage > 0.0:
            target.receive_mercy(self.mercy_percentage)

        if self.tired_percentage > 0.0:
            target.receive_tired(self.mercy_percentage)

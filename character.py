import arcade
from arcade.types import Color

import graphics_objects
import settings
import texture_methods
from animations.common_animations import FadeInFadeOutColorAnimation
from speech_bubble import SpeechBubbleDialog, SpeechBubble
from sprites_and_effects_collection import SpritesAndEffectsCollection

SPRITE_SCALING = 1.0
MOVEMENT_SPEED = 5
WINDOW_WIDTH = settings.WINDOW_WIDTH
WINDOW_HEIGHT = settings.WINDOW_HEIGHT


class Character(arcade.Sprite):
    def __init__(self, sprites_and_effects_collection: SpritesAndEffectsCollection,
                 scale: float, center_x: float, center_y: float, angle: float,
                 sprite_folder_name: str, name: str, max_hp: int, attack: int, defense: int,
                 element_id: int = 0, talk_sound_path: str = "assets/audio/dialog/snd_text.wav"):
        super().__init__(scale=scale, center_x=center_x, center_y=center_y, angle=angle)
        self.sprites_and_effects_collection = sprites_and_effects_collection
        self.sprite_folder_name = sprite_folder_name
        self.name = name
        self.max_hp = max_hp
        self.hp = max_hp
        self.attack = attack
        self.defense = defense
        self.element_id = element_id

        if self.sprites_and_effects_collection:
            self.sprites_and_effects_collection.character_sprites.append(self)

        self.current_animation_state = "default"

        # This dictionary maps state names to texture arrays that represent the animations of said state.
        self.animations_by_state = {
            "default": graphics_objects.SimpleLoopAnimation(
                sprite_pack_path="assets/sprites/soul",
                frame_duration=0.15,
                loop_animation=True
            )
        }

        self.state = "default"  # This is the default texture state upon game creation, as of right now.
        self.current_animation = self.animations_by_state["default"]
        self.current_animation_timer = 0.0
        self.current_texture_index = 0

        self.is_focused = False
        self.focus_animation = None

        # This variable controls how high new NumberBounceAnimations spawned around this character should be.
        self.number_bounce_index = 0

        self.non_idle_timer = 0.0

        self.hurt_sound = arcade.load_sound("assets/audio/battle/player_character/common/snd_hurt1.wav", False)
        self.talk_sound = arcade.load_sound(talk_sound_path, False)

    def set_sprites_and_effects_collection(self, sprites_and_effects_collection: SpritesAndEffectsCollection):
        """
        Sets the sprite collection and effects collection to the character.
        Only works if the sprites and effects collection hasn't already been set.
        :param sprites_and_effects_collection: the sprites and effects collection.
        :return: None
        """
        if not self.sprites_and_effects_collection:
            self.sprites_and_effects_collection = sprites_and_effects_collection
            self.sprites_and_effects_collection.character_sprites.append(self)

    def calculate_received_damage(self, base_damage: float, element_id: int = 0):
        """
        Takes the base damage of the attacker's attack and modifies it based on the characteristics of the receiver
        (ex. defense, element_id, etc.)
        Since player characters/non player characters are a bit different on the back end, this is just a stub.
        :param base_damage: The base damage of the attacker's attack. This function modifies this value
        :param element_id: The element ID of the attack.
        :return:
        """
        pass

    def set_animation_to_not_idle(self, duration: float = 1.0, animation_state: str = "battle_idle"):
        """
        Starts a timer that eventually sets the character back to a battle_idle animation state.
        Used in situations where the character receives a temporary animation state.
        :param duration: The amount of time the character is meant to not be idle.
        :param animation_state: The animation state that the character is meant to be temporarily set to.
        :return: None
        """
        self.non_idle_timer = duration
        self.set_animation_state(animation_state, is_temporary=True)

    def update(self, delta_time: float = 1 / 60, **kwargs):
        """ Helps the player do things.
        :param delta_time: the amount of time in seconds that the player updates
        :param **kwargs:
        """
        if self.non_idle_timer > 0.0:
            self.non_idle_timer -= delta_time
            if self.non_idle_timer <= 0.0:
                self.set_animation_state("battle_idle")

    def update_animation(self, delta_time=1/60, **kwargs):
        """ Cycles through textures based on the player state.
        :param delta_time: interval of time between each update cycle
        """

        # Gets the current animation textures.
        # current_animation = self._animations_by_state.get(self._state)
        if not self.current_animation or len(self.current_animation) <= 1:
            return

        # Update frame timer. If self._current_animation._loop_animation == False, don't loop the animation.
        self.current_animation_timer += delta_time
        if self.current_animation_timer > self.current_animation.get_frame_duration():
            self.current_animation_timer = 0
            if self.current_animation.get_loop_animation() or self.current_texture_index < len(self.current_animation) - 1:
                self.current_texture_index = (self.current_texture_index + 1) % len(self.current_animation)
                self.texture = self.current_animation[self.current_texture_index]

    def set_animation_state(self, state: str = "default", is_temporary: bool = False):
        """
        Sets the animation state of the PlayerCharacter instance. Throws an error if no such state exists in
        self._animations_by_state.
        :param state: The name of the state, in the form of a string.
        :param is_temporary: Internal variable used to determine whether the animation change was temporary.
        :return: None
        """
        if state in self.animations_by_state:
            self.state = state
            self.current_animation = self.animations_by_state.get(state)
            self.current_animation_timer = 0.0
            self.current_texture_index = 0
            self.texture = self.current_animation[0]
            if not is_temporary:
                self.non_idle_timer = 0.0
        else:
            raise ValueError("set_animation_state was given a state that is not present in self._animations_by_state:" + str(state))

    def set_position(self, center_x: int = settings.WINDOW_WIDTH/2, center_y: int = settings.WINDOW_HEIGHT/2):
        """
        Sets the position of the player character.
        :param center_x: The x coordinate of the center of the player character.
        :param center_y: The y coordinate of the center of the player character.
        :return: None
        """
        self.center_x = center_x
        self.center_y = center_y

    def get_valid_animation_states(self):
        """
        Gets a list of all of the valid animation state strings.
        :return: A list of all of the valid animation state strings.
        """
        keys_list = []
        for key in self.animations_by_state.keys():
            keys_list.append(key)
        return keys_list

    def focus(self):
        """
        Creates an instance of a repeating FadeInFadeOutColorAnimation. Returns it so it can be added to the
        animation queue in main.
        """
        if not self.is_focused:
            self.focus_animation = FadeInFadeOutColorAnimation(
                sprite=self,
                color=arcade.color.WHITE,
                total_duration=1,
                is_continuous=True,
                min_alpha=32,
            )
            self.is_focused = True
            return self.focus_animation
        return None

    def unfocus(self):
        """
        Destroys instance of FadeInFadeOutColorAnimation associated with the focused enemy.
        """
        if self.focus_animation:
            self.focus_animation.is_terminated = True
            self.focus_animation.filter_sprite.kill()
            self.is_focused = False

    def spawn_speech_bubble(self, speech_bubble_dialogue: SpeechBubbleDialog) -> SpeechBubble:
        """
        Spawns a speech bubble within the proximity of the NPC.
        :param speech_bubble_dialogue: A SpeechBubbleDialogue instance containing the text/dimensional data of the dialogue.
        :param is_left_of_character: Whether the speech bubble is to the right of the character.
        :return: None
        """

        speech_bubble = SpeechBubble(
            speech_bubble_dialog=speech_bubble_dialogue,
            sprites_and_effects_collection=self.sprites_and_effects_collection
        )

        return speech_bubble

    def set_scale(self, scale: float):
        """
        Set the scale of the player character sprite.
        :param scale: The new scale of the player character sprite.
        :return: None
        """
        self.scale = scale

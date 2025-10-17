import arcade

import graphics_objects
import settings
import texture_methods


SPRITE_SCALING = 1.0
MOVEMENT_SPEED = 5
WINDOW_WIDTH = settings.WINDOW_WIDTH
WINDOW_HEIGHT = settings.WINDOW_HEIGHT

PLAYER_SPRITES_FOLDER_PATH = "assets/sprites/player_characters/"


class Player(arcade.Sprite):
    """ Player Class """

    def update(self, delta_time: float = 1/60):
        """ Move the player """
        # Move player.
        # Remove these lines if physics engine is moving player.
        self.center_x += self.change_x
        self.center_y += self.change_y

        # Check for out-of-bounds
        if self.left < 0:
            self.left = 0
        elif self.right > WINDOW_WIDTH - 1:
            self.right = WINDOW_WIDTH - 1

        if self.bottom < 0:
            self.bottom = 0
        elif self.top > WINDOW_HEIGHT - 1:
            self.top = WINDOW_HEIGHT - 1


class PlayerCharacter(arcade.Sprite):
    def __init__(self, scale: float, center_x: float, center_y: float, angle: float,
                 sprite_folder_name: str, name: str, max_hp: int, attack: int, defense: int, magic: int):
        super().__init__(scale=scale)
        self.center_x = center_x
        self.center_y = center_y
        self.angle = angle
        self.sprite_pack_path = PLAYER_SPRITES_FOLDER_PATH + sprite_folder_name
        self.name = name
        self.max_hp = max_hp
        self.hp = max_hp
        self.attack = attack
        self.defense = defense
        self.magic = magic

        self._current_animation_state = "default"

        # This dictionary maps state names to texture arrays that represent the animations of said state.
        self._animations_by_state = {
            "default": graphics_objects.SimpleLoopAnimation(
                sprite_pack_path=self.sprite_pack_path + "/battle_idle",
                frame_duration=0.15,
                loop_animation=True
            ),

            "battle_act": graphics_objects.SimpleLoopAnimation(
                sprite_pack_path=self.sprite_pack_path + "/battle_act",
                frame_duration=0.10,
                loop_animation=False
            ),

            "battle_attack": graphics_objects.SimpleLoopAnimation(
                sprite_pack_path=self.sprite_pack_path + "/battle_attack",
                frame_duration=0.10,
                loop_animation=False
            ),

            "battle_attack_ready": graphics_objects.SimpleLoopAnimation(
                sprite_pack_path=self.sprite_pack_path + "/battle_attack_ready",
                frame_duration=0.15,
                loop_animation=True
            ),

            "battle_defend": graphics_objects.SimpleLoopAnimation(
                sprite_pack_path=self.sprite_pack_path + "/battle_defend",
                frame_duration=0.10,
                loop_animation=False
            ),

            "battle_downed": graphics_objects.SimpleLoopAnimation(
                sprite_pack_path=self.sprite_pack_path + "/battle_downed",
                frame_duration=0.15,
                loop_animation=False
            ),

            "battle_hurt": graphics_objects.SimpleLoopAnimation(
                sprite_pack_path=self.sprite_pack_path + "/battle_hurt",
                frame_duration=0.6,
                loop_animation=False
            ),

            "battle_idle": graphics_objects.SimpleLoopAnimation(
                sprite_pack_path=self.sprite_pack_path + "/battle_idle",
                frame_duration=0.15,
                loop_animation=True
            ),

            "battle_intro": graphics_objects.SimpleLoopAnimation(
                sprite_pack_path=self.sprite_pack_path + "/battle_intro",
                frame_duration=0.10,
                loop_animation=False
            ),

            "battle_item": graphics_objects.SimpleLoopAnimation(
                sprite_pack_path=self.sprite_pack_path + "/battle_item",
                frame_duration=0.10,
                loop_animation=False
            ),

            "battle_item_ready": graphics_objects.SimpleLoopAnimation(
                sprite_pack_path=self.sprite_pack_path + "/battle_item_ready",
                frame_duration=0.4,
                loop_animation=True
            ),

            "battle_spare": graphics_objects.SimpleLoopAnimation(
                sprite_pack_path=self.sprite_pack_path + "/battle_spare",
                frame_duration=0.10,
                loop_animation=False
            ),

            "battle_victory": graphics_objects.SimpleLoopAnimation(
                sprite_pack_path=self.sprite_pack_path + "/battle_victory",
                frame_duration=0.10,
                loop_animation=False
            ),
        }

        self._state = "default"  # This is the default texture state upon game creation, as of right now.
        self._current_animation = self._animations_by_state["battle_idle"]
        self._current_animation_timer = 0.0
        self._current_texture_index = 0

        # This is temporary.
        if len(self._animations_by_state["battle_idle"]) > 0:
            self.texture = self._animations_by_state["battle_idle"][0]
        else:
            raise FileNotFoundError(f"No .png files found in folder: {self.sprite_pack_path + '/battle_idle'}")

    def update(self, delta_time: float = 1 / 60, **kwargs):
        """ Helps the player do things.
        :param delta_time: the amount of time in seconds that the player updates
        :param **kwargs:
        """

        pass

    def update_animation(self, delta_time=1/60, **kwargs):
        """ Cycles through textures based on the player state.
        :param delta_time: interval of time between each update cycle
        """

        # Gets the current animation textures.
        # current_animation = self._animations_by_state.get(self._state)
        if not self._current_animation or len(self._current_animation) <= 1:
            return

        # Update frame timer. If self._current_animation._loop_animation == False, don't loop the animation.
        self._current_animation_timer += delta_time
        if self._current_animation_timer > self._current_animation.get_frame_duration():
            self._current_animation_timer = 0
            if self._current_animation.get_loop_animation() or self._current_texture_index < len(self._current_animation) - 1:
                self._current_texture_index = (self._current_texture_index + 1) % len(self._current_animation)
                self.texture = self._current_animation[self._current_texture_index]

    def set_animation_state(self, state: str = "default"):
        """
        Sets the animation state of the PlayerCharacter instance. Throws an error if no such state exists in
        self._animations_by_state.
        :param state: The name of the state, in the form of a string.
        :return: None
        """
        if state in self._animations_by_state:
            self._state = state
            self._current_animation = self._animations_by_state.get(state)
            self._current_animation_timer = 0.0
            self._current_texture_index = 0
            self.texture = self._current_animation[0]

        else:
            raise ValueError("set_animation_state was given a state that is not present in self._animations_by_state.")

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
        for key in self._animations_by_state.keys():
            keys_list.append(key)
        print(str(keys_list))
        return keys_list

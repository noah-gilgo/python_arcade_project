import math
from enum import Enum, auto

from arcade.gui import UILayout, UIManager


class Direction(Enum):
    RIGHT = auto()
    LEFT = auto()
    UP = auto()
    DOWN = auto()


class FocusStackMember:
    def __init__(self, ui_layout: UILayout = None, row_count: int = 1):
        self.ui_layout = ui_layout
        self.widgets = self.ui_layout.children
        self.focused_widget = self.widgets[0]
        self.focused_widget_index = 0
        self.row_count = row_count
        self.row_length = math.ceil(len(self.widgets) / self.row_count)

    def move(self, direction: Direction):
        self.focused_widget.focused = False
        match direction:
            case Direction.RIGHT:
                self.focused_widget_index = (self.focused_widget_index + 1) % len(self.widgets)
            case Direction.LEFT:
                self.focused_widget_index = (self.focused_widget_index - 1) % len(self.widgets)
            case Direction.UP:
                self.focused_widget_index = (self.focused_widget_index + self.row_length) % len(self.widgets)
            case Direction.DOWN:
                self.focused_widget_index = (self.focused_widget_index + self.row_length) % len(self.widgets)
        self.focused_widget = self.widgets[self.focused_widget_index]
        self.focused_widget.focused = True

    # Focus the next widget in the layout.
    def move_right(self):
        self.move(Direction.RIGHT)

    def move_left(self):
        self.move(Direction.LEFT)

    def move_up(self):
        self.move(Direction.UP)

    def move_down(self):
        self.move(Direction.DOWN)


class FocusStack:
    def __init__(self, ui_manager: UIManager):
        self.ui_manager = ui_manager
        self.focus_stack = []

    # Returns the highest member in the focus stack. This would presumably be the member that the user wants to
    # interact with when shifting focus between widgets.
    def get_highest_member(self):
        return self.focus_stack[-1]

    # Adds a member to the top of the focus stack. Adds the ui_layout in said member to the ui
    def push(self, ui_layout: UILayout, row_count: int = 1):
        self.focus_stack.append(FocusStackMember(ui_layout, row_count))
        self.ui_manager.add(self.focus_stack[-1].ui_layout)

    # Removes the higest member from the focus stack.
    def pop(self):
        self.ui_manager.remove(self.focus_stack[-1].ui_layout)
        self.focus_stack.pop(-1)

import math
from enum import Enum, auto

from arcade.gui import UILayout, UIManager


class Direction(Enum):
    RIGHT = auto()
    LEFT = auto()
    UP = auto()
    DOWN = auto()


class FocusStackMember:
    def __init__(self, ui_layout: UILayout, state, row_count: int = 1):
        self.ui_layout = ui_layout
        self.widgets = self.ui_layout.children
        self.focused_widget = self.widgets[0]
        self.focused_widget.focused = True
        self.focused_widget_index = 0
        self.row_count = row_count
        self.row_length = math.ceil(len(self.widgets) / self.row_count)

        self.state = state

    def move(self, direction: Direction):
        old_focused_widget = self.focused_widget
        match direction:
            case Direction.RIGHT:
                new_index = self.focused_widget_index + 1
                if 0 <= new_index < len(self.widgets):
                    self.focused_widget_index = new_index % len(self.widgets)
                else:
                    return False
            case Direction.LEFT:
                new_index = self.focused_widget_index - 1
                if 0 <= new_index < len(self.widgets):
                    self.focused_widget_index = new_index % len(self.widgets)
                else:
                    return False
            case Direction.UP:
                if self.row_count > 1:
                    new_index = self.focused_widget_index - self.row_length
                    if new_index >= 0:
                        self.focused_widget_index = new_index
                    else:
                        return False
            case Direction.DOWN:
                if self.row_count > 1:
                    new_index = self.focused_widget_index + self.row_length
                    if new_index < len(self.widgets):
                        self.focused_widget_index = new_index
                    else:
                        return False
        old_focused_widget.focused = False
        self.focused_widget = self.widgets[self.focused_widget_index]
        self.focused_widget.focused = True
        return True

    # Focus the next widget in the layout.
    def move_right(self):
        return self.move(Direction.RIGHT)

    def move_left(self):
        return self.move(Direction.LEFT)

    def move_up(self):
        return self.move(Direction.UP)

    def move_down(self):
        return self.move(Direction.DOWN)


class FocusStack:
    def __init__(self, ui_manager: UIManager):
        self.ui_manager = ui_manager
        self.focus_stack = []

    # Returns the highest member in the focus stack. This would presumably be the member that the user wants to
    # interact with when shifting focus between widgets.
    def get_highest_member(self):
        return self.focus_stack[-1]

    # Adds a member to the top of the focus stack. Adds the ui_layout in said member to the ui
    def push(self, ui_layout: UILayout, state, row_count: int = 1):
        self.focus_stack.append(FocusStackMember(ui_layout, state, row_count))
        self.ui_manager.add(self.focus_stack[-1].ui_layout)

    # Removes the higest member from the focus stack.
    def pop(self):
        if len(self.focus_stack) > 1:
            self.ui_manager.remove(self.focus_stack[-1].ui_layout)
            return self.focus_stack.pop(-1)
        return None

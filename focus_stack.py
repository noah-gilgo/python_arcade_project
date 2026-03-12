import math
from enum import Enum, auto

from arcade.gui import UILayout, UIManager


class Direction(Enum):
    RIGHT = auto()
    LEFT = auto()
    UP = auto()
    DOWN = auto()


class FocusStackMember:
    def __init__(self, full_ui_layout: UILayout, interactive_ui_layout, state, column_count: int):
        self.interactive_ui_layout = interactive_ui_layout
        self.full_ui_layout = full_ui_layout
        self.widgets = self.interactive_ui_layout.children
        self.focused_widget = self.widgets[0]
        self.focused_widget.focused = True
        self.focused_widget_index = 0
        self.column_count = column_count if column_count else len(self.widgets)
        self.row_count = 1 if not column_count else math.ceil(len(self.widgets) / self.column_count)

        self.state = state

    def get_focused_widget(self):
        return self.focused_widget

    def get_focused_widget_index(self):
        return self.focused_widget_index

    def get_interactive_ui_layout(self):
        return self.interactive_ui_layout

    def get_full_ui_layout(self):
        return self.full_ui_layout

    def get_interactive_layout_length(self):
        return len(self.interactive_ui_layout.children)

    def get_full_layout_length(self):
        return len(self.full_ui_layout.children)

    def move(self, direction: Direction):
        old_focused_widget = self.focused_widget
        match direction:
            case Direction.RIGHT:
                new_index = self.focused_widget_index + 1
                if 0 <= new_index < len(self.widgets) and new_index % self.column_count != 0:
                    self.focused_widget_index = new_index % len(self.widgets)
                else:
                    return False
            case Direction.LEFT:
                new_index = self.focused_widget_index - 1
                if 0 <= new_index < len(self.widgets) and self.focused_widget_index % self.column_count != 0:
                    self.focused_widget_index = new_index % len(self.widgets)
                else:
                    return False
            case Direction.UP:
                if self.row_count > 1:
                    new_index = self.focused_widget_index - self.column_count
                    if new_index >= 0:
                        self.focused_widget_index = new_index
                    else:
                        return False
            case Direction.DOWN:
                if self.row_count > 1:
                    new_index = self.focused_widget_index + self.column_count
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
    def get_highest_member(self) -> FocusStackMember:
        return self.focus_stack[-1]

    # Adds a member to the top of the focus stack. Adds the ui_layout in said member to the ui
    def push(self, full_ui_layout: UILayout, interactive_ui_layout, state, column_count: int = 0):
        self.focus_stack.append(FocusStackMember(full_ui_layout, interactive_ui_layout, state, column_count))
        self.ui_manager.add(full_ui_layout)
        self.ui_manager.trigger_render()

    # Removes the higest member from the focus stack.
    def pop(self):
        if len(self.focus_stack) > 1:
            self.ui_manager.remove(self.get_highest_member().get_full_ui_layout())
            return self.focus_stack.pop(-1)
        return None

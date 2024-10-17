# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause


class TreeItem:
    """A tree item class for rendering tree view."""

    def __init__(self, data: list, parent: 'TreeItem' = None):
        self.item_data = data
        self.parent_item = parent
        self.child_items = []

    def child(self, number: int): # -> 'TreeItem':
        """Returns the child item at position number."""
        if number < 0 or number >= len(self.child_items):
            return None
        return self.child_items[number]

    def last_child(self):
        """Returns the last child item."""
        return self.child_items[-1] if self.child_items else None

    def child_count(self) -> int:
        """Returns the number of child items."""
        return len(self.child_items)

    def child_number(self) -> int:
        """Returns the number of child items."""
        if self.parent_item:
            return self.parent_item.child_items.index(self)
        return 0

    def column_count(self) -> int:
        """Returns the number of columns in the item."""
        return len(self.item_data)

    def data(self, column: int):
        """Returns the data for the given column in the item."""
        if column < 0 or column >= len(self.item_data):
            return None
        return self.item_data[column]

    def insert_children(self, position: int, count: int, columns: int) -> bool:
        """Inserts children into the item."""
        if position < 0 or position > len(self.child_items):
            return False

        for _ in range(count):
            data = [None] * columns
            item = TreeItem(data.copy(), self)
            self.child_items.insert(position, item)

        return True

    def insert_columns(self, position: int, columns: int) -> bool:
        """Inserts columns into the item."""
        if position < 0 or position > len(self.item_data):
            return False

        for _ in range(columns):
            self.item_data.insert(position, None)

        for child in self.child_items:
            child.insert_columns(position, columns)

        return True

    def parent(self):
        """Returns the parent item."""
        return self.parent_item

    def remove_children(self, position: int, count: int) -> bool:
        """Removes children from the item."""
        if position < 0 or position + count > len(self.child_items):
            return False

        for _ in range(count):
            self.child_items.pop(position)

        return True

    def remove_columns(self, position: int, columns: int) -> bool:
        """Removes columns from the item."""
        if position < 0 or position + columns > len(self.item_data):
            return False

        for _ in range(columns):
            self.item_data.pop(position)

        for child in self.child_items:
            child.remove_columns(position, columns)

        return True

    def set_data(self, column: int, value):
        """Sets the data for the given column in the item."""
        if column < 0 or column >= len(self.item_data):
            return False

        self.item_data[column] = value
        return True

    def __repr__(self) -> str:
        result = f"<treeitem.TreeItem at 0x{id(self):x}"
        for d in self.item_data:
            result += f' "{d}"' if d else " <None>"
        result += f", {len(self.child_items)} children>"
        return result

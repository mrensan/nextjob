# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause

from PySide6.QtCore import QModelIndex, Qt, QAbstractItemModel

from gui.treeitem import TreeItem


class BaseTreeModel(QAbstractItemModel):
    """The model for the tree view."""

    def __init__(self, headers: list, parent=None):
        super().__init__(parent)

        self.root_data = headers
        self.root_item = TreeItem(self.root_data.copy())

    # pylint: disable=invalid-name, unused-argument
    def columnCount(self, parent: QModelIndex = None) -> int:
        """Returns the number of columns in the model."""
        return self.root_item.column_count()

    def data(self, index: QModelIndex, role: int = None):
        """Returns the data for the given index and role."""
        if not index.isValid():
            return None

        if role not in (Qt.ItemDataRole.DisplayRole, Qt.ItemDataRole.EditRole):
            return None

        item: TreeItem = self.get_item(index)

        return item.data(index.column())

    def flags(self, index: QModelIndex) -> Qt.ItemFlag:
        """Returns the flags for the given index."""
        if not index.isValid():
            return Qt.ItemFlag.NoItemFlags

        return Qt.ItemFlag.ItemIsEditable | QAbstractItemModel.flags(self, index)

    def get_item(self, index: QModelIndex = QModelIndex()) -> TreeItem:
        """Returns the item for the given index."""
        if index.isValid():
            item: TreeItem = index.internalPointer()
            if item:
                return item

        return self.root_item

    def headerData(self, section: int, orientation: Qt.Orientation,
                   role: int = Qt.ItemDataRole.DisplayRole):
        """Returns the header data for the given section and orientation."""
        if orientation == Qt.Orientation.Horizontal and role == Qt.ItemDataRole.DisplayRole:
            return self.root_item.data(section)

        return None

    def index(self, row: int, column: int, parent: QModelIndex = QModelIndex()) -> QModelIndex:
        """Returns the index for the given row, column, and parent index."""
        if parent.isValid() and parent.column() != 0:
            return QModelIndex()

        parent_item: TreeItem = self.get_item(parent)
        if not parent_item:
            return QModelIndex()

        child_item: TreeItem = parent_item.child(row)
        if child_item:
            return self.createIndex(row, column, child_item)
        return QModelIndex()

    def insertColumns(self, position: int, columns: int,
                      parent: QModelIndex = QModelIndex()) -> bool:
        """Inserts columns into the model."""
        self.beginInsertColumns(parent, position, position + columns - 1)
        success: bool = self.root_item.insert_columns(position, columns)
        self.endInsertColumns()

        return success

    def insertRows(self, position: int, rows: int,
                   parent: QModelIndex = QModelIndex()) -> bool:
        """Inserts rows into the model."""
        parent_item: TreeItem = self.get_item(parent)
        if not parent_item:
            return False

        self.beginInsertRows(parent, position, position + rows - 1)
        column_count = self.root_item.column_count()
        success: bool = parent_item.insert_children(position, rows, column_count)
        self.endInsertRows()

        return success

    def parent(self, index: QModelIndex = QModelIndex()) -> QModelIndex:
        """Returns the parent index for the given index."""
        if not index.isValid():
            return QModelIndex()

        child_item: TreeItem = self.get_item(index)
        if child_item:
            parent_item = child_item.parent()
        else:
            parent_item = None

        if parent_item == self.root_item or not parent_item:
            return QModelIndex()

        return self.createIndex(parent_item.child_number(), 0, parent_item)

    def removeColumns(self, position: int, columns: int,
                      parent: QModelIndex = QModelIndex()) -> bool:
        """Removes columns from the model."""
        self.beginRemoveColumns(parent, position, position + columns - 1)
        success: bool = self.root_item.remove_columns(position, columns)
        self.endRemoveColumns()

        if self.root_item.column_count() == 0:
            self.removeRows(0, self.rowCount())

        return success

    def removeRows(self, position: int, rows: int,
                   parent: QModelIndex = QModelIndex()) -> bool:
        """Removes rows from the model."""
        parent_item: TreeItem = self.get_item(parent)
        if not parent_item:
            return False

        self.beginRemoveRows(parent, position, position + rows - 1)
        success: bool = parent_item.remove_children(position, rows)
        self.endRemoveRows()

        return success

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        """Returns the number of rows in the model for the given parent index."""
        if parent.isValid() and parent.column() > 0:
            return 0

        parent_item: TreeItem = self.get_item(parent)
        if not parent_item:
            return 0
        return parent_item.child_count()

    def setData(self, index, value, role=...):
        """Sets the data for the given index."""
        if role != Qt.ItemDataRole.EditRole:
            return False

        item: TreeItem = self.get_item(index)
        result: bool = item.set_data(index.column(), value)

        if result:
            self.dataChanged.emit(
                index,
                index,
                [Qt.ItemDataRole.DisplayRole, Qt.ItemDataRole.EditRole]
            )

        return result

    def setHeaderData(self, section: int, orientation: Qt.Orientation, value,
                      role: int = None) -> bool:
        """Sets the header data for the given section and orientation."""
        if role != Qt.ItemDataRole.EditRole or orientation != Qt.Orientation.Horizontal:
            return False

        result: bool = self.root_item.set_data(section, value)

        if result:
            self.headerDataChanged.emit(orientation, section, section)

        return result

    def _repr_recursion(self, item: TreeItem, indent: int = 0) -> str:
        result = " " * indent + repr(item) + "\n"
        for child in item.child_items:
            result += self._repr_recursion(child, indent + 2)
        return result

    def __repr__(self) -> str:
        return self._repr_recursion(self.root_item)

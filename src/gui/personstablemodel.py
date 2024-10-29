from typing import List, Tuple

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QTableView, QWidget

from backend.models import Person
from gui.basetreemodel import BaseTreeModel
from gui.guiutils import config_view_as_line_selectable
from gui.treeitem import TreeItem

VISIBLE_COLUMNS_COUNT = 5


class PersonsTableModel(BaseTreeModel):
    """Table model for a list of persons."""

    def __init__(self, headers: list, data: List[Person], parent=None):
        super().__init__(headers, parent=parent)
        self.setup_model_data(data, self.root_item)

    def setup_model_data(self, persons: List[Person], parent: TreeItem):
        """Setups the model data."""
        for person in persons:
            self._insert_person(person, parent)

    @staticmethod
    def _insert_person(person: Person, parent: TreeItem):
        parent.insert_children(parent.child_count(), 1, VISIBLE_COLUMNS_COUNT + 1)
        child = parent.last_child()
        child.set_data(0, person.title.value)
        child.set_data(1, person.name)
        child.set_data(2, person.role)
        child.set_data(3, person.email)
        child.set_data(4, person.description)
        child.set_data(5, person.uuid)


def create_person_table_view(persons: List[Person], parent: QWidget, width: int = 800) -> Tuple[
    QTableView, BaseTreeModel]:
    """Creates a table view for a list of persons."""
    persons_table = QTableView()
    config_view_as_line_selectable(persons_table)
    return persons_table, set_person_table_model(persons, persons_table, parent, width)


def set_person_table_model(persons: List[Person], persons_table: QTableView, parent: QWidget,
                           width: int = 800) -> BaseTreeModel:
    """Sets the table model for a list of persons."""
    headers = ["Title", "Name", "Role", "Email", "Description"]
    interviewers_model = PersonsTableModel(headers, persons, parent)
    persons_table.setModel(interviewers_model)
    persons_table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
    persons_table.setColumnWidth(0, int(width * .5 / 10))
    persons_table.setColumnWidth(1, int(width * 1.75 / 10))
    persons_table.setColumnWidth(2, int(width * 2 / 10))
    persons_table.setColumnWidth(3, int(width * 2.2 / 10))
    persons_table.setColumnWidth(4, int(width * 2.8 / 10))

    return interviewers_model

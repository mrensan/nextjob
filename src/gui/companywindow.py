from typing import List

from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QTableView

from backend.data_service import DataService
from backend.models import Company, Role
from gui.basetreemodel import BaseTreeModel
from gui.guiutils import get_line_layout, create_save_cancel_layout, config_view_as_line_selectable
from gui.personstablemodel import create_person_table_view
from gui.treeitem import TreeItem

MAIN_WINDOW_WIDTH = 800

VISIBLE_COLUMNS_COUNT = 5


class CompanyWindow(QDialog):
    """Company edit window."""

    # pylint: disable=too-few-public-methods
    def __init__(self, company: Company):
        super().__init__()
        self.setWindowTitle("Company Details")
        self.resize(MAIN_WINDOW_WIDTH, 600)

        self.company = company

        vertical = QVBoxLayout()

        name_label = QLabel("Name:")
        self.name_value = QLineEdit(str(self.company.name))
        vertical.addLayout(get_line_layout(name_label, self.name_value, 1, 3, 6))

        website_label = QLabel("Website:")
        self.website_value = QLineEdit(self.company.website)
        vertical.addLayout(get_line_layout(website_label, self.website_value, 1, 3, 6))

        recruiters_label = QLabel("Recruiters:")
        vertical.addWidget(recruiters_label)

        self.recruiters_table, self.recruiters_model = create_person_table_view(
            company.recruiters, self)
        vertical.addWidget(self.recruiters_table)

        roles_label = QLabel("Roles:")
        vertical.addWidget(roles_label)

        self.roles_table = QTableView()
        config_view_as_line_selectable(self.roles_table)
        headers = ["Title", "Applied Date", "Employment Type", "Work Location", "Description"]
        self.interviewers_model = RolesTableModel(headers, company.roles, self)
        self.roles_table.setModel(self.interviewers_model)
        self.roles_table.setColumnWidth(0, int(MAIN_WINDOW_WIDTH * 2.3 / 10))
        self.roles_table.setColumnWidth(1, int(MAIN_WINDOW_WIDTH * 1.2 / 10))
        self.roles_table.setColumnWidth(2, int(MAIN_WINDOW_WIDTH * 1.4 / 10))
        self.roles_table.setColumnWidth(3, int(MAIN_WINDOW_WIDTH * 1.4 / 10))
        self.roles_table.setColumnWidth(4, int(MAIN_WINDOW_WIDTH * 3.1 / 10))
        vertical.addWidget(self.roles_table)

        vertical.addLayout(create_save_cancel_layout(self._cancel, self._save))

        self.setLayout(vertical)

    def _cancel(self):
        self.reject()

    def _save(self):
        data_service = DataService()
        self.company.name = self.name_value.text()
        self.company.website = self.website_value.text()

        data_service.update_company(self.company)
        self.accept()


class RolesTableModel(BaseTreeModel):
    """Table model for roles."""
    # pylint: disable=too-few-public-methods

    def __init__(self, headers: list, data: List[Role], parent=None):
        super().__init__(headers, parent=parent)
        self.setup_model_data(data, self.root_item)

    def setup_model_data(self, roles: List[Role], parent: TreeItem):
        """Setups the model data."""
        for role in roles:
            self._insert_role(role, parent)

    @staticmethod
    def _insert_role(role: Role, parent: TreeItem):
        parent.insert_children(parent.child_count(), 1, VISIBLE_COLUMNS_COUNT + 1)
        child = parent.last_child()
        child.set_data(0, role.title)
        child.set_data(1, f"{role.applied_date}")
        child.set_data(2, role.employment_type.value)
        child.set_data(3, role.work_location.value)
        child.set_data(4, role.description)
        child.set_data(5, role.uuid)

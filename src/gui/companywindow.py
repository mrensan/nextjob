from typing import List

from PySide6.QtCore import QModelIndex
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QTableView, QMenu

from backend.data_service import DataService
from backend.htmlextractor import get_html_text
from backend.models import Company, Role
from gui.basetreemodel import BaseTreeModel
from gui.guiutils import get_line_layout, create_save_cancel_layout, config_view_as_line_selectable, get_attr, \
    verify_delete_row, EDIT_ICON, DELETE_ICON, ADD_ICON
from gui.personstablemodel import create_person_table_view, set_person_table_model
from gui.personwindow import PersonWindow
from gui.treeitem import TreeItem

MAIN_WINDOW_WIDTH = 900

VISIBLE_COLUMNS_COUNT = 5


class CompanyWindow(QDialog):
    """Company edit window."""

    def __init__(self, company: Company = None):
        super().__init__()
        self.setWindowTitle("Company Details")
        self.resize(MAIN_WINDOW_WIDTH, 600)

        self.data_service = DataService()
        self.company = company

        vertical = QVBoxLayout()

        name_label = QLabel("Name:")
        self.name_value = QLineEdit(get_attr(self.company, "name"))
        vertical.addLayout(get_line_layout(name_label, self.name_value, 1, 4, 5))

        website_label = QLabel("Website:")
        self.website_value = QLineEdit(get_attr(self.company, "website"))
        vertical.addLayout(get_line_layout(website_label, self.website_value, 1, 4, 5))

        recruiters_label = QLabel("Recruiters:")
        vertical.addWidget(recruiters_label)

        self.recruiters_table, self.recruiters_model = create_person_table_view(
            get_attr(company, "recruiters", []), self)
        self.recruiters_table.customContextMenuRequested.connect(self._open_context_menu)
        vertical.addWidget(self.recruiters_table)

        roles_label = QLabel("Roles:")
        vertical.addWidget(roles_label)

        self.roles_table = QTableView()
        config_view_as_line_selectable(self.roles_table)
        headers = ["Title", "Applied Date", "Employment Type", "Work Location", "Description"]
        self.interviewers_model = RolesTableModel(headers, get_attr(self.company, "roles", []), self)
        self.roles_table.setModel(self.interviewers_model)
        self.roles_table.setColumnWidth(0, int(MAIN_WINDOW_WIDTH * 2.3 / 10))
        self.roles_table.setColumnWidth(1, int(MAIN_WINDOW_WIDTH * 1.2 / 10))
        self.roles_table.setColumnWidth(2, int(MAIN_WINDOW_WIDTH * 1.4 / 10))
        self.roles_table.setColumnWidth(3, int(MAIN_WINDOW_WIDTH * 1.4 / 10))
        self.roles_table.setColumnWidth(4, int(MAIN_WINDOW_WIDTH * 3.1 / 10))
        vertical.addWidget(self.roles_table)

        vertical.addLayout(create_save_cancel_layout(self._cancel, self._save))

        self.setLayout(vertical)

    def _open_context_menu(self, point):
        index = self.recruiters_table.indexAt(point)
        context_menu = QMenu()
        if index.isValid():
            context_menu.addAction(QIcon(EDIT_ICON), "Edit Recruiter", lambda: self._open_recruiter_window(index))
            context_menu.addAction(QIcon(DELETE_ICON), "Delete Recruiter",
                                   lambda: self._delete_recruiter_row(index))
        else:
            context_menu.addAction(QIcon(ADD_ICON), "Add Recruiter", lambda: self._open_recruiter_window(index))

        context_menu.exec(self.recruiters_table.viewport().mapToGlobal(point))

    def _open_recruiter_window(self, index: QModelIndex):
        item_data = self.recruiters_model.get_item(index).item_data
        recruiter_window = PersonWindow(item_data, self.company)
        if recruiter_window.exec():
            self._set_recruiter_table_model()

    def _delete_recruiter_row(self, index: QModelIndex):
        item_data = self.recruiters_model.get_item(index).item_data
        if verify_delete_row(f"Are you sure you want to delete recruiter: {item_data[0]} {item_data[1]}?", self):
            self.data_service.delete_recruiter(item_data[5], self.company.uuid)
            self._set_recruiter_table_model()

    def _set_recruiter_table_model(self):
        self.company = self.data_service.get_company_by_uuid(self.company.uuid)
        set_person_table_model(self.company.recruiters, self.recruiters_table, self)

    def _cancel(self):
        self.reject()

    def _save(self):
        is_new_company = False
        if not self.company:
            self.company = Company(name=self.name_value.text())
            is_new_company = True
        else:
            self.company.name = self.name_value.text()
        self.company.website = self.website_value.text()

        if is_new_company:
            self.data_service.insert_company(self.company)
        else:
            self.data_service.update_company(self.company)
        self.accept()


class RolesTableModel(BaseTreeModel):
    """Table model for roles."""

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
        child.set_data(4, get_html_text(role.description))
        child.set_data(5, role.uuid)

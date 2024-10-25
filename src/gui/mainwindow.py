from enum import Enum
from typing import List

from PySide6.QtCore import QModelIndex, Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QMainWindow, QTreeView, QAbstractItemView, QDialog, QMenu

from backend.data_service import DataService
from backend.models import Company, Role, Interview
from gui.basetreemodel import BaseTreeModel
from gui.companywindow import CompanyWindow
from gui.interviewwindow import InterviewWindow
from gui.rolewindow import RoleWindow
from gui.treeitem import TreeItem

MAIN_WINDOW_HEIGHT = 800

MAIN_WINDOW_WIDTH = 1200

VISIBLE_COLUMNS_COUNT = 3

ADD_ICON = ":/qt-project.org/styles/commonstyle/images/newdirectory-32.png"
EDIT_ICON = ":/qt-project.org/styles/commonstyle/images/desktop-32.png"
DELETE_ICON = ":/qt-project.org/styles/commonstyle/images/critical-32.png"


class RowType(Enum):
    """Enum to represent type of row."""
    COMPANY = 'COMPANY'
    ROLE = 'ROLE'
    INTERVIEW = 'INTERVIEW'


class MainWindow(QMainWindow):
    """Main window of GUI"""

    def __init__(self, app):
        super().__init__()
        self.app = app
        self.setWindowTitle("Next Job")
        self.resize(MAIN_WINDOW_WIDTH, MAIN_WINDOW_HEIGHT)

        self.view = QTreeView()
        self.view.setAlternatingRowColors(True)
        self.view.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.view.setHorizontalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)
        self.view.setAllColumnsShowFocus(True)
        self.view.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.view.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.view.doubleClicked.connect(self._on_row_double_clicked)
        self.view.customContextMenuRequested.connect(self._open_context_menu)
        self.setCentralWidget(self.view)

        self.headers = ["Title", "Details", "Recruiter(s)/Interviewer(s)"]
        self.data_service = DataService()
        self._set_tree_view_model()

    def _open_context_menu(self, point):
        index = self.view.indexAt(point)
        context_menu = QMenu()
        if index.isValid():
            item = self.tree_model.get_item(index)
            row_type = item.item_data[4]
            match row_type:
                case RowType.COMPANY:
                    context_menu.addAction(QIcon(EDIT_ICON), "Edit Company", lambda: self._open_edit_window(index))
                    context_menu.addAction(QIcon(DELETE_ICON), "Delete Company",
                                           lambda: self._on_row_double_clicked(index))
                    context_menu.addSeparator()
                    context_menu.addAction(QIcon(ADD_ICON), "Add Role", lambda: self._open_new_window(index))
                case RowType.ROLE:
                    context_menu.addAction(QIcon(EDIT_ICON), "Edit Role", lambda: self._open_edit_window(index))
                    context_menu.addAction(QIcon(DELETE_ICON), "Delete Role",
                                           lambda: self._on_row_double_clicked(index))
                    context_menu.addSeparator()
                    context_menu.addAction(QIcon(ADD_ICON), "Add Interview", lambda: self._open_new_window(index))
                case _:
                    context_menu.addAction(QIcon(EDIT_ICON), "Edit Interview",
                                           lambda: self._open_edit_window(index))
                    context_menu.addAction(QIcon(DELETE_ICON), "Delete Interview",
                                           lambda: self._on_row_double_clicked(index))
        else:
            context_menu.addAction(QIcon(ADD_ICON), "Add Company", lambda: self._open_new_window(index))

        context_menu.exec(self.view.viewport().mapToGlobal(point))

    def _on_row_double_clicked(self, index: QModelIndex):
        self._open_edit_window(index)

    def _open_edit_window(self, index: QModelIndex):
        item_data = self.tree_model.get_item(index).item_data
        row_type = item_data[4]
        detail_window: QDialog
        company_index: QModelIndex
        row: int
        column: int
        match row_type:
            case RowType.COMPANY:
                row = index.row()
                column = index.column()
                company = self.data_service.get_company_by_uuid(item_data[3])
                detail_window = CompanyWindow(company)
            case RowType.ROLE:
                company_index = index.parent()
                row = company_index.row()
                column = company_index.column()
                company = self.data_service.get_company_by_role_uuid(item_data[3])
                detail_window = RoleWindow(item_data, company)
            case _:
                company_index = index.parent().parent()
                row = company_index.row()
                column = company_index.column()
                company = self.data_service.get_company_by_interview_uuid(item_data[3])
                detail_window = InterviewWindow(item_data, company)

        if detail_window.exec() == 1:
            self._set_tree_view_model()
            new_index = self.tree_model.index(row, column)
            self.view.expandRecursively(new_index, -1)

    def _open_new_window(self, index: QModelIndex):
        detail_window: QDialog
        if index.isValid():
            item_data = self.tree_model.get_item(index).item_data
            row_type = item_data[4]
            row: int
            column: int
            match row_type:
                case RowType.COMPANY:
                    row = index.row()
                    column = index.column()
                    company = self.data_service.get_company_by_uuid(item_data[3])
                    detail_window = RoleWindow(item_data, company)
                case _:
                    company_index = index.parent()
                    row = company_index.row()
                    column = company_index.column()
                    company = self.data_service.get_company_by_role_uuid(item_data[3])
                    detail_window = InterviewWindow(item_data, company)
            if detail_window.exec() == 1:
                self._set_tree_view_model()
                new_index = self.tree_model.index(row, column)
                self.view.expandRecursively(new_index, -1)
        else:
            detail_window = CompanyWindow(None)
            if detail_window.exec() == 1:
                self._set_tree_view_model()

    def _set_tree_view_model(self):
        data_model: List[Company] = self.data_service.get_companies()
        self.tree_model = CompaniesTreeModel(self.headers, data_model, self)
        self.view.setModel(self.tree_model)
        self.view.setColumnWidth(0, int(MAIN_WINDOW_WIDTH / 3))
        self.view.setColumnWidth(1, int(MAIN_WINDOW_WIDTH / 3))
        self.view.setColumnWidth(2, int(MAIN_WINDOW_WIDTH / 3))


class CompaniesTreeModel(BaseTreeModel):
    """Tree model for companies"""

    def __init__(self, headers: list, data: List[Company], parent=None):
        super().__init__(headers, parent=parent)
        self.setup_model_data(data, self.root_item)

    def setup_model_data(self, companies: List[Company], parent: TreeItem):
        """Sets up the model data."""
        for company in companies:
            self._insert_company(company, parent)

    def _insert_company(self, company: Company, parent: TreeItem):
        parent.insert_children(parent.child_count(), 1, VISIBLE_COLUMNS_COUNT + 2)
        child = parent.last_child()
        child.set_data(0, company.name)
        child.set_data(1, "" if company.website is None else company.website)
        child.set_data(2, ", ".join([p.name for p in company.recruiters]))
        child.set_data(3, company.uuid)
        child.set_data(4, RowType.COMPANY)

        for role in company.roles:
            self._insert_role(role, child)

    def _insert_role(self, role: Role, parent: TreeItem):
        parent.insert_children(parent.child_count(), 1, VISIBLE_COLUMNS_COUNT + 2)
        child = parent.last_child()
        child.set_data(0, role.title)
        child.set_data(1, f"{role.applied_date} (applied date)")
        child.set_data(2, f"{role.employment_type.value}/{role.work_location.value}")
        child.set_data(3, role.uuid)
        child.set_data(4, RowType.ROLE)

        for interview in role.interviews:
            self._insert_interview(interview, child)

    @staticmethod
    def _insert_interview(interview: Interview, parent: TreeItem):
        parent.insert_children(parent.child_count(), 1, VISIBLE_COLUMNS_COUNT + 2)
        child = parent.last_child()
        child.set_data(0, f"({interview.sequence}) {interview.title}")
        child.set_data(1, f"{interview.type.value} at {interview.date}")
        child.set_data(2, ", ".join([p.name for p in interview.interviewers]))
        child.set_data(3, interview.uuid)
        child.set_data(4, RowType.INTERVIEW)

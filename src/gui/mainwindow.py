from enum import Enum
from typing import List, Optional

from PySide6.QtCore import QModelIndex, Qt
from PySide6.QtGui import QIcon, QAction, QFont, QColor
from PySide6.QtWidgets import QMainWindow, QTreeView, QAbstractItemView, QDialog, QMenu, QDockWidget, QLineEdit, \
    QStatusBar, QLabel, QSizePolicy, QMenuBar, QMessageBox

from backend.data_service import DataService
from backend.models import Company, Role, Interview
from gui.basetreemodel import BaseTreeModel
from gui.companywindow import CompanyWindow, EDIT_ICON, DELETE_ICON, ADD_ICON
from gui.guiutils import verify_delete_row, SEARCH_ICON, RESET_ICON
from gui.interviewwindow import InterviewWindow
from gui.rolewindow import RoleWindow
from gui.treeitem import TreeItem

MAIN_WINDOW_HEIGHT = 800

MAIN_WINDOW_WIDTH = 1200

VISIBLE_COLUMNS_COUNT = 3


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
        self.addDockWidget(Qt.DockWidgetArea.TopDockWidgetArea, self._get_dock_widget())
        self._config_menu(self.menuBar())
        self.setStatusBar(self._get_status_bar())

        self.headers = ["Title", "Details", "Recruiter(s), Interviewer(s)"]
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
                                           lambda: self._delete_row(index))
                    context_menu.addSeparator()
                    context_menu.addAction(QIcon(ADD_ICON), "Add Role", lambda: self._open_new_window(index))
                case RowType.ROLE:
                    context_menu.addAction(QIcon(EDIT_ICON), "Edit Role", lambda: self._open_edit_window(index))
                    context_menu.addAction(QIcon(DELETE_ICON), "Delete Role",
                                           lambda: self._delete_row(index))
                    context_menu.addSeparator()
                    context_menu.addAction(QIcon(ADD_ICON), "Add Interview", lambda: self._open_new_window(index))
                case _:
                    context_menu.addAction(QIcon(EDIT_ICON), "Edit Interview",
                                           lambda: self._open_edit_window(index))
                    context_menu.addAction(QIcon(DELETE_ICON), "Delete Interview",
                                           lambda: self._delete_row(index))
        else:
            context_menu.addAction(QIcon(ADD_ICON), "Add Company", lambda: self._open_new_window(index))

        context_menu.exec(self.view.viewport().mapToGlobal(point))

    def _on_row_double_clicked(self, index: QModelIndex):
        self._open_edit_window(index)

    def _delete_row(self, index: QModelIndex):
        item_data = self.tree_model.get_item(index).item_data
        row_type = item_data[4]
        company_index: QModelIndex
        row: int
        column: int
        match row_type:
            case RowType.COMPANY:
                row = index.row()
                column = index.column()
                if verify_delete_row(f"Are you sure you want to delete {item_data[0]}?", self):
                    self.data_service.delete_company(item_data[3])
                else:
                    return
            case RowType.ROLE:
                company_index = index.parent()
                row = company_index.row()
                column = company_index.column()
                if verify_delete_row(f"Are you sure you want to delete {item_data[0]}?", self):
                    self.data_service.delete_role(item_data[3])
                else:
                    return
            case _:
                company_index = index.parent().parent()
                row = company_index.row()
                column = company_index.column()
                if verify_delete_row(f"Are you sure you want to delete {item_data[0]}?", self):
                    self.data_service.delete_interview(item_data[3])
                else:
                    return

        self._set_tree_view_model()
        new_index = self.tree_model.index(row, column)
        if row_type != RowType.COMPANY:
            self.view.expandRecursively(new_index, -1)

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

    def _open_new_window(self, index: Optional[QModelIndex]):
        detail_window: QDialog
        if index and index.isValid():
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

    def _set_tree_view_model(self, data_model: List[Company] = None):
        if data_model is None:
            data_model: List[Company] = self.data_service.get_companies()
            self.companies_count.setText(f"Companies: {len(data_model)}")
            self.status_label.setText("Ready")
        else:
            self.status_label.setText(f"Search results: {len(data_model)} company(s)")
        self.tree_model = CompaniesTreeModel(self.headers, data_model, self,
                                             self.search_value.text() if data_model else "")
        self.view.setModel(self.tree_model)
        self.view.setColumnWidth(0, int(MAIN_WINDOW_WIDTH * .37))
        self.view.setColumnWidth(1, int(MAIN_WINDOW_WIDTH * .25))
        self.view.setColumnWidth(2, int(MAIN_WINDOW_WIDTH * .37))

    def _config_menu(self, menu_bar: QMenuBar):
        companies_menu = menu_bar.addMenu("Companies")
        companies_menu.addAction(QIcon(ADD_ICON), "Add Company", lambda: self._open_new_window(None))

        help_menu = menu_bar.addMenu("Help")
        help_menu.addAction("About", lambda: QMessageBox.about(
            self,
            "About",
            "Next Job\n 0.4.0\n\nCopyright © 2024 Shahram Ensan\nMIT License"))

    def _get_dock_widget(self) -> QDockWidget:
        dock = QDockWidget(self)
        dock.setAllowedAreas(Qt.DockWidgetArea.AllDockWidgetAreas)
        self.search_value = QLineEdit()
        self.search_value.setPlaceholderText("Search ...")
        self.search_value.textChanged.connect(self._search_text_changed)
        search_action = QAction(QIcon(SEARCH_ICON), "Search", self.search_value)
        reset_action = QAction(QIcon(RESET_ICON), "Reset", self.search_value)
        self.search_value.addAction(reset_action, QLineEdit.ActionPosition.TrailingPosition)
        self.search_value.addAction(search_action, QLineEdit.ActionPosition.TrailingPosition)
        search_action.triggered.connect(self._search_action_triggered)
        reset_action.triggered.connect(self._reset_action_triggered)
        dock.setWidget(self.search_value)
        return dock

    def _get_status_bar(self) -> QStatusBar:
        status_bar = QStatusBar(self)
        self.status_label = QLabel("Ready")
        self.status_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self.companies_count = QLineEdit()
        self.companies_count.setReadOnly(True)
        self.companies_count.setDisabled(True)
        self.companies_count.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Preferred)
        self.companies_count.setAlignment(Qt.AlignmentFlag.AlignCenter)

        status_bar.addWidget(self.status_label, 1)
        status_bar.addPermanentWidget(self.companies_count)

        return status_bar

    def _search_text_changed(self, text: str):
        if len(text) > 2:
            self._search(text)

    def _search_action_triggered(self):
        self._search(self.search_value.text())

    def _reset_action_triggered(self):
        self.search_value.setText("")
        self._set_tree_view_model()

    def _search(self, text: str):
        search_result = self.data_service.search_in_db(text)
        self._set_tree_view_model(search_result)
        self.view.expandAll()


class CompaniesTreeModel(BaseTreeModel):
    """Tree model for companies"""

    def __init__(self, headers: list, data: List[Company], parent=None, search_value: str = ""):
        super().__init__(headers, parent=parent)
        self.setup_model_data(data, self.root_item)
        self.search_value = search_value

    def data(self, index: QModelIndex, role: int = None):
        """Customization of data formatting."""
        if index.isValid():
            if role == Qt.ItemDataRole.FontRole and index.column() == 0 and index.parent().column() == -1:
                font = QFont()
                font.setWeight(QFont.Weight.Bold)
                return font
            if (role == Qt.ItemDataRole.BackgroundRole and
                    self.search_value and self.search_value.lower() in index.data().lower()):
                return QColor('#FAF691')
        return super().data(index, role)

    def setup_model_data(self, companies: List[Company], parent: TreeItem):
        """Sets up the model data."""
        for company in companies:
            self._insert_company(company, parent)

    def _insert_company(self, company: Company, parent: TreeItem):
        parent.insert_children(parent.child_count(), 1, VISIBLE_COLUMNS_COUNT + 2)
        child = parent.last_child()
        interview_count = 0
        for role in company.roles:
            interview_count += len(role.interviews)
        child.set_data(0, company.name)
        child.set_data(1, f"Roles: {len(company.roles)}, Interview: {interview_count}")
        child.set_data(2, ", ".join([p.name for p in company.recruiters]))
        child.set_data(3, company.uuid)
        child.set_data(4, RowType.COMPANY)

        for role in company.roles:
            self._insert_role(role, child)

    def _insert_role(self, role: Role, parent: TreeItem):
        parent.insert_children(parent.child_count(), 1, VISIBLE_COLUMNS_COUNT + 2)
        child = parent.last_child()
        child.set_data(0, role.title)
        child.set_data(1, f"{role.applied_date}")
        child.set_data(2, f"{role.employment_type.value}, {role.work_location.value}")
        child.set_data(3, role.uuid)
        child.set_data(4, RowType.ROLE)

        for interview in role.interviews:
            self._insert_interview(interview, child)

    @staticmethod
    def _insert_interview(interview: Interview, parent: TreeItem):
        parent.insert_children(parent.child_count(), 1, VISIBLE_COLUMNS_COUNT + 2)
        child = parent.last_child()
        child.set_data(0, f"({interview.sequence}) {interview.title}")
        child.set_data(1, f"{interview.date}, {interview.type.value}")
        child.set_data(2, ", ".join([f"{p.name} ({p.role})" if p.role else p.name for p in interview.interviewers]))
        child.set_data(3, interview.uuid)
        child.set_data(4, RowType.INTERVIEW)

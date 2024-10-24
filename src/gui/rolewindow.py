from dataclasses import dataclass
from datetime import date
from typing import List

from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QComboBox, \
    QTextEdit, QTableView, QAbstractItemView

from backend.data_service import DataService
from backend.models import Company, EmploymentType, WorkLocation, Interview
from gui.basetreemodel import BaseTreeModel
from gui.guiutils import get_line_layout, create_save_cancel_layout
from gui.treeitem import TreeItem

MAIN_WINDOW_WIDTH = 800

VISIBLE_COLUMNS_COUNT = 5


@dataclass
class RoleWindowComponents:
    """The editable components of the role window."""

    def __init__(self):
        pass

    title_value: QLineEdit
    applied_date_value: QLineEdit
    employment_type_value: QComboBox
    work_location_value: QComboBox
    description_value: QTextEdit
    interviews_table: QTableView


class RoleWindow(QDialog):
    """Role edit window."""
    # pylint: disable=too-few-public-methods

    def __init__(self, item_data: list, company: Company):
        super().__init__()
        self.setWindowTitle("Role Details")
        self.resize(MAIN_WINDOW_WIDTH, 600)

        self.company = company
        self.role = self._find_role(item_data[3], company)

        vertical = QVBoxLayout()
        self.components = RoleWindowComponents()
        title_label = QLabel("Title:")
        self.components.title_value = QLineEdit(self.role.title)
        vertical.addLayout(get_line_layout(title_label, self.components.title_value, 2, 3, 5))

        applied_date_label = QLabel("Applied Date:")
        self.components.applied_date_value = QLineEdit(str(self.role.applied_date))
        vertical.addLayout(get_line_layout(
            applied_date_label,
            self.components.applied_date_value,
            2,
            3,
            5
        ))

        employment_type_label = QLabel("Employment Type:")
        self.components.employment_type_value = QComboBox()
        self.components.employment_type_value.addItems([et.value for et in EmploymentType])
        self.components.employment_type_value.setCurrentText(self.role.employment_type.value)
        vertical.addLayout(get_line_layout(
            employment_type_label,
            self.components.employment_type_value,
            2,
            3,
            5
        ))

        work_location_label = QLabel("Work Location:")
        self.components.work_location_value = QComboBox()
        self.components.work_location_value.addItems([wl.value for wl in WorkLocation])
        self.components.work_location_value.setCurrentText(self.role.work_location.value)
        vertical.addLayout(get_line_layout(
            work_location_label,
            self.components.work_location_value,
            2,
            3,
            5
        ))

        description_label = QLabel("Description:")
        vertical.addWidget(description_label)
        self.components.description_value = QTextEdit(self.role.description)
        self.components.description_value.setMaximumWidth(int(MAIN_WINDOW_WIDTH / 2))
        self.components.description_value.setMaximumHeight(80)
        vertical.addWidget(self.components.description_value)

        interviews_label = QLabel("Interviews:")
        vertical.addWidget(interviews_label)

        self._create_table_view()
        vertical.addWidget(self.components.interviews_table)

        vertical.addLayout(create_save_cancel_layout(self._cancel, self._save))

        self.setLayout(vertical)

    def _create_table_view(self):
        self.components.interviews_table = QTableView()
        self.components.interviews_table.setSelectionBehavior(
            QAbstractItemView.SelectionBehavior.SelectRows
        )
        self.components.interviews_table.setEditTriggers(
            QAbstractItemView.EditTrigger.NoEditTriggers
        )
        self.components.interviews_table.setAlternatingRowColors(True)
        self.components.interviews_table.setHorizontalScrollMode(
            QAbstractItemView.ScrollMode.ScrollPerPixel
        )
        headers = ["Seq", "Title", "Interview type", "Date", "Interviewers"]
        self.interviews_model = InterviewsTableModel(headers, self.role.interviews, self)
        self.components.interviews_table.setModel(self.interviews_model)
        self.components.interviews_table.setColumnWidth(0, int(MAIN_WINDOW_WIDTH * .5 / 10))
        self.components.interviews_table.setColumnWidth(1, int(MAIN_WINDOW_WIDTH * 2.6 / 10))
        self.components.interviews_table.setColumnWidth(2, int(MAIN_WINDOW_WIDTH * 1.5 / 10))
        self.components.interviews_table.setColumnWidth(3, int(MAIN_WINDOW_WIDTH * 1.2 / 10))
        self.components.interviews_table.setColumnWidth(4, int(MAIN_WINDOW_WIDTH * 3.5 / 10))

    @staticmethod
    def _find_role(role_uuid: str, company: Company):
        for role in company.roles:
            if role.uuid == role_uuid:
                return role
        return None

    def _cancel(self):
        self.reject()

    def _save(self):
        data_service = DataService()
        self.role.title = self.components.title_value.text()
        self.role.applied_date = date.fromisoformat(self.components.applied_date_value.text())
        self.role.employment_type = list(EmploymentType)[
            self.components.employment_type_value.currentIndex()
        ]
        self.role.work_location = list(WorkLocation)[
            self.components.work_location_value.currentIndex()
        ]
        self.role.description = self.components.description_value.toPlainText()

        data_service.update_company(self.company)
        self.accept()


class InterviewsTableModel(BaseTreeModel):
    """Table model for interviews."""
    # pylint: disable=too-few-public-methods

    def __init__(self, headers: list, data: List[Interview], parent=None):
        super().__init__(headers, parent=parent)
        self.setup_model_data(data, self.root_item)

    def setup_model_data(self, interviews: List[Interview], parent: TreeItem):
        """Setups the model data."""
        for interview in interviews:
            self._insert_interview(interview, parent)

    @staticmethod
    def _insert_interview(interview: Interview, parent: TreeItem):
        parent.insert_children(parent.child_count(), 1, VISIBLE_COLUMNS_COUNT + 1)
        child = parent.last_child()
        child.set_data(0, interview.sequence)
        child.set_data(1, interview.title)
        child.set_data(2, interview.type.value)
        child.set_data(3, f"{interview.date}")
        child.set_data(4, ", ".join([i.name for i in interview.interviewers]))
        child.set_data(5, interview.uuid)

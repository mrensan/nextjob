from datetime import date

from PySide6.QtWidgets import QDialog, QLabel, QVBoxLayout, QLineEdit, QComboBox

from backend.data_service import DataService
from backend.models import Company, InterviewType
from gui.guiutils import get_line_layout, create_save_cancel_layout
from gui.personstablemodel import create_person_table_view

MAIN_WINDOW_WIDTH = 800

VISIBLE_COLUMNS_COUNT = 5


class InterviewWindow(QDialog):
    """Interview edit window."""

    # pylint: disable=too-few-public-methods

    def __init__(self, item_data: list, company: Company):
        super().__init__()
        self.setWindowTitle("Interview Details")
        self.resize(MAIN_WINDOW_WIDTH, 600)

        self.company = company
        self.interview = self._find_interview(item_data[3], company)

        vertical = QVBoxLayout()

        seq_label = QLabel("Sequence:")
        seq_value = QLineEdit(str(self.interview.sequence))
        seq_value.setReadOnly(True)
        seq_value.setDisabled(True)
        vertical.addLayout(get_line_layout(seq_label, seq_value))

        title_label = QLabel("Title:")
        self.title_value = QLineEdit(self.interview.title)
        vertical.addLayout(get_line_layout(title_label, self.title_value))

        type_label = QLabel("Type:")
        self.type_value = QComboBox()
        self.type_value.addItems([t.value for t in InterviewType])
        self.type_value.setCurrentText(self.interview.type.value)
        vertical.addLayout(get_line_layout(type_label, self.type_value))

        date_label = QLabel("Date:")
        self.date_value = QLineEdit(str(self.interview.date))
        vertical.addLayout(get_line_layout(date_label, self.date_value))

        interviewers_label = QLabel("Interviewers:")
        vertical.addWidget(interviewers_label)

        self.interviewers_table, self.interviewers_model = create_person_table_view(
            self.interview.interviewers,
            self
        )
        vertical.addWidget(self.interviewers_table)

        vertical.addLayout(create_save_cancel_layout(self._cancel, self._save))

        self.setLayout(vertical)

    @staticmethod
    def _find_interview(interview_uuid: str, company: Company):
        for role in company.roles:
            for interview in role.interviews:
                if interview.uuid == interview_uuid:
                    return interview
        return None

    def _cancel(self):
        self.reject()

    def _save(self):
        data_service = DataService()
        self.interview.title = self.title_value.text()
        self.interview.type = list(InterviewType)[self.type_value.currentIndex()]
        self.interview.date = date.fromisoformat(self.date_value.text())

        data_service.update_company(self.company)
        self.accept()

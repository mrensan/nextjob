import logging
from typing import Optional

from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QLabel,
    QComboBox,
    QLineEdit,
    QTextEdit,
)
from pydantic import ValidationError

from backend.data_service import DataService
from backend.models import Company, TITLE, Person, Interview
from gui.guiutils import (
    get_line_layout,
    get_attr,
    create_save_cancel_layout,
    translate_validation_error,
    show_error_dialog,
)

MAIN_WINDOW_WIDTH = 700


class PersonWindow(QDialog):
    """Person edit window."""

    def __init__(self, item_data: list, company: Company, interview: Interview = None):
        super().__init__()
        self.logger = logging.getLogger(self.__class__.__name__)
        self.setWindowTitle(
            f"{'Recruiter' if interview is None else 'Interviewer'} Details"
        )
        self.resize(MAIN_WINDOW_WIDTH, 250)

        self.company = company
        self.interview = interview
        self.person = (
            self._find_person(item_data[5], company, interview)
            if len(item_data) > 5
            else None
        )

        vertical = QVBoxLayout()
        title_label = QLabel("Title:")
        self.title_value = QComboBox()
        self.title_value.addItems([t.value for t in TITLE])
        if self.person:
            self.title_value.setCurrentText(self.person.title.value)
        vertical.addLayout(get_line_layout(title_label, self.title_value, 1, 1, 8))

        name_label = QLabel("Name: (*)")
        self.name_value = QLineEdit(get_attr(self.person, "name"))
        vertical.addLayout(get_line_layout(name_label, self.name_value, 1, 7, 2))

        role_label = QLabel("Role:")
        self.role_value = QLineEdit(get_attr(self.person, "role"))
        vertical.addLayout(get_line_layout(role_label, self.role_value, 1, 7, 2))

        email_label = QLabel("Email:")
        self.email_value = QLineEdit(get_attr(self.person, "email"))
        vertical.addLayout(get_line_layout(email_label, self.email_value, 1, 7, 2))

        description_label = QLabel("Description:")
        vertical.addWidget(description_label)
        self.description_value = QTextEdit(get_attr(self.person, "description"))
        self.description_value.setMaximumHeight(100)
        vertical.addWidget(self.description_value)

        vertical.addLayout(create_save_cancel_layout(self._cancel, self._save, 2, 2, 6))

        self.setLayout(vertical)

    def _cancel(self):
        self.reject()

    def _save(self):
        try:
            data_service = DataService()
            title_value = list(TITLE)[self.title_value.currentIndex()]
            name_value = self.name_value.text().strip()
            role_value = self.role_value.text().strip()
            email_value = self.email_value.text().strip()
            description_value = self.description_value.toHtml()
            if not self.person:
                self.person = Person(title=title_value, name=name_value)
                if self.interview:
                    self.interview.interviewers.append(self.person)
                else:
                    self.company.recruiters.append(self.person)
            else:
                self.person.title = title_value
                self.person.name = name_value
            self.person.role = role_value
            self.person.email = email_value
            self.person.description = description_value

            data_service.update_company(self.company)
            self.accept()

        except ValidationError as e:
            self.logger.error("Saving company validation error: %s", e)
            show_error_dialog(self, "Validation Error", translate_validation_error(e))

    @staticmethod
    def _find_person(
        person_uuid: str, company: Company, interview: Interview
    ) -> Optional[Person]:
        if interview is None:
            for recruiter in company.recruiters:
                if recruiter.uuid == person_uuid:
                    return recruiter
        else:
            for interviewer in interview.interviewers:
                if interviewer.uuid == person_uuid:
                    return interviewer
        return None

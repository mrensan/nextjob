import logging
from datetime import date

from PySide6.QtCore import QModelIndex
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QDialog, QLabel, QVBoxLayout, QLineEdit, QComboBox, QMenu
from pydantic import ValidationError

from backend.data_service import DataService
from backend.models import Company, InterviewType, Interview, Role
from gui.desctextedit import DescriptionTextEdit
from gui.guiutils import get_line_layout, create_save_cancel_layout, get_attr, verify_delete_row, DELETE_ICON, \
    EDIT_ICON, ADD_ICON, translate_validation_error, translate_date_format_error, show_error_dialog
from gui.personstablemodel import create_person_table_view, set_person_table_model
from gui.personwindow import PersonWindow

import gui.iconsrc  # pylint: disable=unused-import

MAIN_WINDOW_WIDTH = 900

VISIBLE_COLUMNS_COUNT = 5


class InterviewWindow(QDialog):
    """Interview edit window."""

    def __init__(self, item_data: list, company: Company):
        super().__init__()
        self.logger = logging.getLogger(self.__class__.__name__)
        self.setWindowTitle("Interview Details")
        self.resize(MAIN_WINDOW_WIDTH, 600)

        self.data_service = DataService()
        self.company = company
        self.interview = self._find_interview(item_data[3], company)
        self.role = self._find_role(item_data[3], company)

        vertical = QVBoxLayout()

        seq_label = QLabel("Sequence:")
        if self.interview:
            self.seq_value = QLineEdit(str(self.interview.sequence))
        else:
            self.seq_value = QLineEdit(str(self._get_next_sequence(self.role)))
        self.seq_value.setReadOnly(True)
        self.seq_value.setDisabled(True)
        vertical.addLayout(get_line_layout(seq_label, self.seq_value))

        title_label = QLabel("Title: (*)")
        self.title_value = QLineEdit(get_attr(self.interview, "title"))
        vertical.addLayout(get_line_layout(title_label, self.title_value, 1, 4, 5))

        type_label = QLabel("Type:")
        self.type_value = QComboBox()
        self.type_value.addItems([t.value for t in InterviewType])
        if self.interview:
            self.type_value.setCurrentText(self.interview.type.value)
        vertical.addLayout(get_line_layout(type_label, self.type_value))

        date_label = QLabel("Date: (*)")
        self.date_value = QLineEdit(str(get_attr(self.interview, "date")))
        vertical.addLayout(get_line_layout(date_label, self.date_value))

        description_label = QLabel("Description:")
        vertical.addWidget(description_label)
        self.description_value = DescriptionTextEdit(get_attr(self.interview, "description"))
        vertical.addWidget(self.description_value)

        interviewers_label = QLabel("Interviewers:")
        vertical.addWidget(interviewers_label)

        self.interviewers_table, self.interviewers_model = create_person_table_view(
            get_attr(self.interview, "interviewers", []),
            self,
            MAIN_WINDOW_WIDTH
        )
        self.interviewers_table.customContextMenuRequested.connect(self._open_context_menu)
        vertical.addWidget(self.interviewers_table)

        vertical.addLayout(create_save_cancel_layout(self._cancel, self._save))

        self.setLayout(vertical)

    def _open_context_menu(self, point):
        index = self.interviewers_table.indexAt(point)
        context_menu = QMenu()
        if index.isValid():
            context_menu.addAction(QIcon(EDIT_ICON), "Edit Interviewer", lambda: self._open_interviewer_window(index))
            context_menu.addAction(QIcon(DELETE_ICON), "Delete Interviewer",
                                   lambda: self._delete_interviewer_row(index))
        else:
            if self.interview:
                context_menu.addAction(QIcon(ADD_ICON), "Add Interviewer", lambda: self._open_interviewer_window(index))
            else:
                context_menu.addAction(QIcon(ADD_ICON), "Save Interview and Add Interviewer",
                                       lambda: self._save_interview_and_open_interviewer_window(index))

        context_menu.exec(self.interviewers_table.viewport().mapToGlobal(point))

    def _save_interview_and_open_interviewer_window(self, index: QModelIndex):
        if self._save_interview():
            self._open_interviewer_window(index)

    def _open_interviewer_window(self, index: QModelIndex):
        item_data = self.interviewers_model.get_item(index).item_data
        interviewer_window = PersonWindow(item_data, self.company, self.interview)
        if interviewer_window.exec():
            self._set_interviewer_table_model()

    def _delete_interviewer_row(self, index: QModelIndex):
        item_data = self.interviewers_model.get_item(index).item_data
        if verify_delete_row(f"Are you sure you want to delete interviewer: {item_data[0]} {item_data[1]}?", self):
            self.data_service.delete_interviewer(item_data[5], self.interview.uuid)
            self._set_interviewer_table_model()

    def _set_interviewer_table_model(self):
        self.company = self.data_service.get_company_by_uuid(self.company.uuid)
        self.interview = self._find_interview(self.interview.uuid, self.company)
        set_person_table_model(self.interview.interviewers, self.interviewers_table, self)

    @staticmethod
    def _find_interview(interview_uuid: str, company: Company):
        for role in company.roles:
            for interview in role.interviews:
                if interview.uuid == interview_uuid:
                    return interview
        return None

    @staticmethod
    def _find_role(role_uuid: str, company: Company):
        for role in company.roles:
            if role.uuid == role_uuid:
                return role
        return None

    @staticmethod
    def _get_next_sequence(role: Role) -> int:
        if len(role.interviews) == 0:
            return 1
        return role.interviews[-1].sequence + 1

    def _cancel(self):
        self.accept()

    def _save(self):
        if self._save_interview():
            self.accept()

    def _save_interview(self) -> bool:
        try:
            sequence_value = int(self.seq_value.text().strip())
            title_value = self.title_value.text().strip()
            type_value = list(InterviewType)[self.type_value.currentIndex()]
            date_value = date.fromisoformat(self.date_value.text().strip())
            if not self.interview:
                self.interview = Interview(
                    sequence=sequence_value,
                    title=title_value,
                    type=type_value,
                    date=date_value
                )
                self.role.interviews.append(self.interview)
            else:
                self.interview.title = title_value
                self.interview.type = type_value
                self.interview.date = date_value

            self.interview.description = self.description_value.toHtml()
            self.data_service.update_company(self.company)
            return True
        except ValidationError as e:
            self.logger.error("Saving interview validation error: %s", e)
            show_error_dialog(self, "Validation Error", translate_validation_error(e))
        except ValueError as e:
            self.logger.error("Saving interview validation error: %s", e)
            show_error_dialog(self, "Validation Error", translate_date_format_error(e))

        return False
